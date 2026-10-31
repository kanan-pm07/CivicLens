import os, json, uuid, sqlite3, base64, csv, io
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, make_response
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from PIL import Image
from google import genai

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "civiclens.db"
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED = {"png", "jpg", "jpeg", "webp"}
MODEL = os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it")

app = Flask(__name__)
app.jinja_env.filters['fromjson'] = json.loads
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-before-deploying")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY, created_at TEXT NOT NULL, category TEXT NOT NULL,
            severity TEXT NOT NULL, title TEXT NOT NULL, description TEXT NOT NULL,
            location TEXT NOT NULL, ward TEXT, image_path TEXT, ai_summary TEXT,
            department TEXT, complaint TEXT, missing_evidence TEXT,
            status TEXT NOT NULL DEFAULT 'Submitted', language TEXT DEFAULT 'English', latitude REAL, longitude REAL
        )""")
        columns = {
            row["name"]
            for row in con.execute("PRAGMA table_info(reports)")
        }

        if "latitude" not in columns:
            con.execute("ALTER TABLE reports ADD COLUMN latitude REAL")

        if "longitude" not in columns:
            con.execute("ALTER TABLE reports ADD COLUMN longitude REAL")

def fallback_analysis(description, location):
    text = (description or "").lower()
    categories = [
        (["pothole", "road", "crater"], "Road damage", "Roads & Infrastructure"),
        (["garbage", "waste", "dump", "rubbish"], "Waste accumulation", "Solid Waste Management"),
        (["streetlight", "light pole", "lamp"], "Streetlight issue", "Electrical / Street Lighting"),
        (["waterlog", "flood", "drain", "sewage"], "Waterlogging or drainage", "Drainage & Sewerage"),
        (["water leak", "pipe leak"], "Water leakage", "Water Supply"),
    ]
    category, department = "Public infrastructure issue", "Municipal Grievance Cell"
    for words, cat, dept in categories:
        if any(w in text for w in words):
            category, department = cat, dept
            break
    severity = "High" if any(w in text for w in ["danger", "accident", "blocked", "deep", "exposed wire"]) else "Medium"
    return {
        "category": category, "severity": severity,
        "title": f"{category} reported near {location or 'the provided location'}",
        "summary": "Demo analysis: the report appears to describe a civic infrastructure issue. Add precise landmarks and a clear photograph before submitting.",
        "department": department,
        "complaint": f"Dear Municipal Grievance Team,\\n\\nI would like to report {category.lower()} near {location or '[exact location]'}. {description}\\n\\nPlease inspect the site, assess the issue, and arrange appropriate action. I can provide additional details if required.\\n\\nThank you.",
        "missing_evidence": ["Add a nearby landmark or street name", "Include the date/time the issue was observed"]
    }


def analyse_with_gemma(description, location, language, image_path=None):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        result = fallback_analysis(description, location)
        result["mode"] = "demo"
        return result

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are CivicLens, a multimodal civic infrastructure
reporting assistant.

Your job is to analyse a user's photograph and description
and help them prepare an accurate civic issue report.

USER INFORMATION:
Location: {location or "Not provided"}
Description: {description or "Not provided"}
Complaint language: {language}

ANALYSIS RULES:

1. Examine the photograph carefully if provided.
2. Identify visible civic infrastructure problems.
3. Consider the user's description alongside the image.
4. Never invent details that are not visible or provided.
5. If the image and description disagree, mention the
   uncertainty in the summary.
6. Do not claim that an issue has been officially verified.
7. Do not identify people, vehicle owners or private details.

CLASSIFICATION:
Choose the most appropriate category:
- Road damage
- Waste accumulation
- Streetlight issue
- Waterlogging or drainage
- Water leakage
- Public infrastructure issue
- Other

SEVERITY:
Choose Low, Medium, High or Urgent.

Low: Minor issue with little apparent immediate risk.
Medium: Noticeable issue requiring attention.
High: Significant damage or potential safety risk.
Urgent: Credible indication of immediate serious danger.

Do not automatically assign High or Urgent just because
the user uses alarming language.

DEPARTMENT:
Suggest a relevant municipal function.
This is a recommendation, not a confirmed authority.

COMPLAINT:
Generate a polite, factual complaint in {language}.
Do not add fabricated facts.

MISSING EVIDENCE:
Identify information that would improve the report,
such as exact landmark, date, time or clearer photographs.

Return ONLY valid JSON with these exact keys:

{{
  "category": "string",
  "severity": "Low, Medium, High or Urgent",
  "title": "string",
  "summary": "string",
  "department": "string",
  "complaint": "string",
  "missing_evidence": ["string"]
}}
"""

    contents = [prompt]

    if image_path:
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            contents.append(image)

            response = client.models.generate_content(
                model=MODEL,
                contents=contents
            )
    else:
        response = client.models.generate_content(
            model=MODEL,
            contents=contents
        )

    raw = response.text.strip()

    # Handle responses wrapped in Markdown code blocks.
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    # Extract JSON if the model adds extra surrounding text.
    start = raw.find("{")
    end = raw.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError("Gemma did not return valid JSON.")

    data = json.loads(raw[start:end + 1])

    required = [
        "category",
        "severity",
        "title",
        "summary",
        "department",
        "complaint",
        "missing_evidence"
    ]

    for field in required:
        if field not in data:
            raise ValueError(f"Gemma response missing {field}")

    if data["severity"] not in ["Low", "Medium", "High", "Urgent"]:
        raise ValueError("Invalid severity returned by Gemma.")

    if not isinstance(data["missing_evidence"], list):
        raise ValueError("Invalid missing_evidence format.")

    for field in required[:-1]:
        if not isinstance(data[field], str):
            raise ValueError(f"Invalid data type for {field}")

    data["mode"] = "gemma"

    return data

@app.route("/")
def index():
    with db() as con:
        total = con.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
        open_count = con.execute("SELECT COUNT(*) FROM reports WHERE status NOT IN ('Resolved')").fetchone()[0]
        resolved = con.execute("SELECT COUNT(*) FROM reports WHERE status='Resolved'").fetchone()[0]
        recent = con.execute("SELECT * FROM reports ORDER BY created_at DESC LIMIT 6").fetchall()
    return render_template("index.html", total=total, open_count=open_count, resolved=resolved, recent=recent)

@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "GET":
        return render_template("report.html")
    description = request.form.get("description", "").strip()
    location = request.form.get("location", "").strip()
    ward = request.form.get("ward", "").strip()
    
    latitude_raw = request.form.get("latitude", "").strip()
    longitude_raw = request.form.get("longitude", "").strip()

    latitude = None
    longitude = None

    # Generate a location label if the user only supplied coordinates
    if not location and latitude is not None and longitude is not None:
        location = f"Coordinates: {latitude:.6f}, {longitude:.6f}"

    if latitude_raw or longitude_raw:
        try:
            latitude = float(latitude_raw)
            longitude = float(longitude_raw)

            if not (-90 <= latitude <= 90):
                raise ValueError("Invalid latitude")

            if not (-180 <= longitude <= 180):
                raise ValueError("Invalid longitude")

        except ValueError:
            flash("Please enter valid latitude and longitude.", "error")
            return redirect(url_for("report"))

    language = request.form.get("language", "English")
    photo = request.files.get("photo")
    if not description and (not photo or not photo.filename):
        flash("Please add a description or upload a photo.", "error")
        return redirect(url_for("report"))
    image_path = None
    if photo and photo.filename:
        ext = photo.filename.rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED:
            flash("Please upload a JPG, PNG, or WEBP image.", "error")
            return redirect(url_for("report"))
        filename = secure_filename(f"{uuid.uuid4().hex}.{ext}")
        full_path = UPLOAD_DIR / filename
        photo.save(full_path)
        image_path = f"uploads/{filename}"
    full_image = (BASE_DIR / "static" / image_path) if image_path else None
    try:
        ai = analyse_with_gemma(description, location, language, str(full_image) if full_image else None)
    except Exception as e:
        flash(f"AI analysis could not complete: {str(e)[:180]}. Your draft was not submitted; try again or remove the image.", "error")
        return redirect(url_for("report"))
    report_id = "CL-" + uuid.uuid4().hex[:8].upper()
    created = datetime.now().isoformat(timespec="seconds")
    
    with db() as con:
        con.execute("""
            INSERT INTO reports
            (id, created_at, category, severity, title,
            description, location, ward, image_path,
            ai_summary, department, complaint,
            missing_evidence, status, language,
            latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id, created, ai["category"], ai["severity"],
            ai["title"], description,
            location or "Location not provided", ward,
            image_path, ai["summary"], ai["department"],
            ai["complaint"],
            json.dumps(ai["missing_evidence"], ensure_ascii=False),
            "Submitted", language, latitude, longitude
        ))

    return redirect(url_for("report_detail", report_id=report_id, mode=ai.get("mode", "demo")))

@app.route("/reports")
def reports():
    status = request.args.get("status", "")
    with db() as con:
        if status:
            rows = con.execute("SELECT * FROM reports WHERE status=? ORDER BY created_at DESC", (status,)).fetchall()
        else:
            rows = con.execute("SELECT * FROM reports ORDER BY created_at DESC").fetchall()
    return render_template("reports.html", reports=rows, selected=status)

@app.route("/reports/<report_id>")
def report_detail(report_id):
    with db() as con:
        item = con.execute("SELECT * FROM reports WHERE id=?", (report_id,)).fetchone()
    if not item:
        return render_template("not_found.html"), 404
    return render_template("detail.html", item=item, mode=request.args.get("mode", "saved"))

@app.route("/track", methods=["GET", "POST"])
def track():
    item = None
    if request.method == "POST":
        rid = request.form.get("report_id", "").strip().upper()
        with db() as con:
            item = con.execute("SELECT * FROM reports WHERE id=?", (rid,)).fetchone()
        if not item:
            flash("No report found with that tracking ID.", "error")
    return render_template("track.html", item=item)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    # Demo-only status manager. Add authentication before public deployment.
    if request.method == "POST":
        rid = request.form.get("report_id")
        status = request.form.get("status")
        if status not in {"Submitted", "Under Review", "Assigned", "Resolved"}:
            flash("Invalid status.", "error")
        else:
            with db() as con:
                con.execute("UPDATE reports SET status=? WHERE id=?", (status, rid))
            flash("Report status updated.", "success")
        return redirect(url_for("admin"))
    with db() as con:
        rows = con.execute("SELECT * FROM reports ORDER BY created_at DESC").fetchall()
    return render_template("admin.html", reports=rows)

@app.route("/export.csv")
def export_csv():
    with db() as con:
        rows = con.execute("SELECT id, created_at, category, severity, title, location, ward, department, status FROM reports ORDER BY created_at DESC").fetchall()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Tracking ID", "Created", "Category", "Severity", "Title", "Location", "Ward", "Suggested Department", "Status"])
    writer.writerows([tuple(r) for r in rows])
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=civiclens-reports.csv"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    return response

@app.errorhandler(413)
def too_large(_):
    flash("Image is too large. Maximum upload size is 8 MB.", "error")
    return redirect(url_for("report"))

init_db()

@app.route("/api/reports")
def api_reports():
    with db() as con:
        rows = con.execute("""
            SELECT id, title, category, severity,
                   location, latitude, longitude, status
            FROM reports
            WHERE latitude IS NOT NULL
              AND longitude IS NOT NULL
        """).fetchall()

    return jsonify([dict(row) for row in rows])
@app.route("/map")
def civic_map():
    return render_template("map.html")
if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", 5000)))
