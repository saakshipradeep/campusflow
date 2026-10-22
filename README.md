# CampusFlow — Recruitment Coordination & Candidate Experience

An interactive **fictional** applicant tracking and recruitment coordination portfolio project built with Python, Streamlit and Pandas.

## Features
- 100 reproducible simulated candidates; editable stage, recruiter and notes; add candidate
- Pipeline overview and recruiter workload
- Interview scheduling, cancellation/rescheduling, and interviewer conflict detection
- Recruiter task tracking and overdue alerts
- Candidate communication templates and draft log (no messages sent)
- Structured interview evaluations
- Mock offer preparation checklist
- CSV exports and stage-change history

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Upload `app.py`, `requirements.txt`, and `README.md` to the root of a GitHub repository.
2. Visit https://share.streamlit.io/ and create a new app.
3. Select your repository, branch `main`, and entry point `app.py`.
4. Deploy. No API keys or secrets are required.

## Limitations
All data is simulated. **Changes persist only in the active Streamlit session** and reset on refresh/restart/session expiry; they are not shared across users. No real emails, calendar invites, offers or ATS integrations are performed. Uses a fixed May 31, 2027 fictional snapshot. Not for real applicant personal data.
