# 🌿 CivicLens — AI-Powered Civic Issue Reporting Platform

<p align="center">
  <strong>Your Neighbourhood. Your Voice. Real Action.</strong>
</p>

<p align="center">
  An AI-powered civic issue reporting platform that transforms photographs of local problems into structured, actionable civic complaints using Google's Gemma 4 multimodal AI.
</p>

<p align="center">
  <a href="https://civiclens-pzyg.onrender.com">🌐 Live Demo</a>
</p>

---

## 🚀 About the Project

CivicLens is a community-driven civic issue reporting platform designed to make reporting local infrastructure and public-service problems easier, faster, and more accessible.

Citizens can upload photographs of civic problems such as potholes, damaged roads, garbage accumulation, drainage issues, and other public infrastructure concerns.

Using **Google's Gemma 4 multimodal AI**, CivicLens analyses uploaded images and descriptions to generate structured complaint information, identify issue categories, estimate priority, suggest responsible departments, and prepare complaint drafts.

The platform also provides an interactive map to visualise reported civic issues and a tracking system to follow submitted reports.

**Our goal:** Turn a photograph of a local problem into a clear, actionable civic report.

## ✨ Key Features

### 1. AI-Powered Civic Issue Analysis
- Analyses uploaded photographs and user descriptions.
- Uses Google Gemma 4 multimodal AI.
- Identifies civic issue categories.
- Generates clear issue summaries.
- Estimates complaint priority.
- Suggests the relevant department.

### 2. Automatic Complaint Generation
- Converts user descriptions into structured complaint drafts.
- Supports complaint language selection.
- Generates helpful details and additional evidence suggestions.
- Makes complaints easier to understand and communicate.

### 3. Interactive Civic Issue Map
- Displays reported issues using geographical coordinates.
- Uses Leaflet and OpenStreetMap.
- Supports interactive map markers.
- Uses marker clustering to organise overlapping reports.
- Allows users to explore reported problems geographically.

### 4. Complaint Tracking
- Generates a unique tracking ID for every report.
- Allows users to look up submitted complaints.
- Displays complaint status and progress.

### 5. Community Reports
- Displays submitted civic complaints.
- Organises reports by category and status.
- Helps users explore reported community problems.

### 6. Demo Admin Dashboard
- Provides a dashboard for reviewing reports.
- Allows demonstration of complaint status updates.
- Supports CSV export for report data.

## 🧠 AI Integration — Google Gemma 4

CivicLens uses Google's Gemma 4 through the Google GenAI SDK.

The multimodal AI integration helps interpret uploaded civic issue photographs alongside user-provided descriptions.

The AI analysis produces structured information such as:

- Issue category
- Complaint title
- Issue summary
- Estimated severity
- Suggested department
- Complaint draft
- Missing evidence or helpful details

The generated information helps transform unstructured citizen reports into more organised civic complaints.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Flask |
| AI Model | Google Gemma 4 |
| AI Integration | Google GenAI SDK |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Maps | Leaflet, OpenStreetMap |
| Image Processing | Pillow |
| Production Server | Gunicorn |
| Hosting | Render |

## 🏗️ Project Structure

```text
CivicLens/
│
├── app.py
├── requirements.txt
├── test_gemma.py
├── .env.example
├── .gitignore
├── README.md
├── run_windows.bat
│
├── static/
│   ├── app.js
│   ├── style.css
│   └── uploads/
│
└── templates/
    ├── base.html
    ├── index.html
    ├── report.html
    ├── reports.html
    ├── detail.html
    ├── track.html
    ├── admin.html
    ├── map.html
    └── not_found.html
```

## ⚙️ Installation and Setup

Follow these steps to run CivicLens locally.

### Prerequisites

- Python 3.10 or later
- Git
- Google AI Studio API key
- VS Code (recommended)

### Step 1: Clone the repository

```bash
git clone https://github.com/kanan-pm07/CivicLens.git
cd CivicLens
```

### Step 2: Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Create a `.env` file in the project root directory.

Add the following:

```env
GEMINI_API_KEY=your_google_ai_studio_api_key
GEMMA_MODEL=gemma-4-26b-a4b-it
FLASK_SECRET_KEY=your_secure_random_secret
```

Get your API key from:

https://aistudio.google.com/apikey

**Important:** Never commit your `.env` file or expose your API key publicly.

### Step 5: Run the application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

CivicLens should now be running locally.

## 🌐 Live Deployment

CivicLens is publicly deployed using Render.

**Live Website:** https://civiclens-pzyg.onrender.com

The application uses:
- GitHub for source-code management.
- Render for hosting.
- Gunicorn as the production WSGI server.
- Environment variables for API keys and application secrets.

### Deployment Configuration

| Setting | Value |
|---|---|
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
| Hosting Platform | Render |

Configure the required environment variables in your hosting dashboard instead of uploading the `.env` file.

## 🔄 How CivicLens Works

1. A citizen visits the CivicLens website.
2. The citizen uploads a photograph and describes the civic issue.
3. Gemma 4 analyses the photograph and description.
4. The application generates a structured complaint and AI recommendations.
5. The citizen submits the report.
6. CivicLens generates a unique tracking ID.
7. The report appears in the community reports section and, when coordinates are provided, on the interactive issue map.
8. Users can track the report using its tracking ID.

## 🔐 Privacy and Limitations

- AI-generated complaint information should be reviewed by users before submission.
- CivicLens is a prototype civic reporting platform.
- Reports are not automatically submitted to an official municipal authority.
- The demo admin dashboard is intended for demonstration, not production-grade administrative security.
- The current free hosting deployment uses temporary local storage. Database records and uploaded images are not guaranteed to survive service restarts or redeployments.
- Avoid uploading photographs containing sensitive personal information.

## 🔮 Future Improvements

- Integration with official municipal complaint systems.
- Persistent cloud database and image storage.
- Secure administrator authentication and role-based access.
- Real-time complaint status notifications.
- Duplicate civic issue detection.
- Improved geolocation and address identification.
- Analytics dashboard for civic issue trends.
- Multilingual complaint generation and accessibility improvements.

## 🎯 Project Vision

CivicLens aims to bridge the gap between citizens and civic problem reporting by combining multimodal AI, geographical visualisation, and structured complaint generation.

We believe that reporting a civic problem should be simple, understandable, and actionable.

**Your Neighbourhood. Your Voice. Real Action.**

---

## 👨‍💻 Author

**Kanan Prasad Moharana**

GitHub: https://github.com/kanan-pm07

---

<p align="center">
  Built with ❤️ using Python, Flask, and Google Gemma 4.
</p>