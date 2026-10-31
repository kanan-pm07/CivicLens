# CivicLens

A responsive civic-issue reporting and tracking website powered by Gemma 4.

## Features
- Submit a civic issue with a photo, description, location and ward.
- Gemma 4 multimodal analysis (server-side API key; never expose it in browser code).
- AI-generated category, severity estimate, suggested municipal function, complaint draft and missing-evidence checklist.
- SQLite-backed report storage and tracking IDs.
- Public report dashboard, status filters, report detail and CSV export.
- Demo status-management page for judges.
- Works in demo mode without an API key using a clearly labelled rule-based fallback.

## Run on Windows
1. Install Python 3.10 or newer.
2. Extract this ZIP and open the `civiclens` folder in VS Code.
3. Open Terminal and run:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   copy .env.example .env
   ```
4. Get a Gemini API key from https://aistudio.google.com/apikey
5. Open `.env` and set `GEMINI_API_KEY=your_key`.
6. Run:
   ```powershell
   python app.py
   ```
7. Open http://127.0.0.1:5000

The default model is `gemma-4-26b-a4b-it`. You can change `GEMMA_MODEL` in `.env` if the event gives you access to another supported Gemma 4 model.

## Important before public deployment
- The `/admin` page is a judge/demo status manager and is intentionally unauthenticated. Add authentication and role-based access before public deployment.
- This prototype stores uploaded photos locally and does not connect to Bhubaneswar Municipal Corporation or any government grievance API. Do not present a generated complaint as officially filed.
- AI severity/category are suggestions, not official determinations. Users should verify the generated text before sharing.
- Add HTTPS, rate limiting, image scanning, retention controls and production database/storage before real public use.

## Suggested event submission
- Project name: CivicLens
- Prize categories: Best Use of Gemma 4; Best Open-Source AI Project
- AI your project calls: Gemma
- Technologies: Python, Flask, SQLite, HTML, CSS, JavaScript, Google GenAI SDK, Gemma 4
