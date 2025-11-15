На русском тута <a href="https://github.com/Kerimniy/QuartUptimeService/blob/main/README-RU.md">тык</a>


<img src="https://github.com/Kerimniy/QuartUptimeService/blob/main/for_readme/QUS.png" style="width: 70px">

# QuartUptimeService

## What It Is

Uptime Monitor is an asynchronous web service built on Python (Quart + asyncio) for monitoring the availability of websites and APIs. It periodically sends HTTP requests to specified URLs, logs statuses in SQLite, and generates uptime charts (for the last hour). Supports service groups, authentication, and a simple dashboard.

<img src="https://github.com/Kerimniy/QuartUptimeService/blob/main/for_readme/QUSP.png" style="width: 95%; margin-left: 2vh; position: relative; left:50%; transform: translateX(-50%)">


## Installation

1. **Dependencies** (Python 3.12+):
   ```
   pip install requerments.txt
   ```

2. **Files**: clone repo.

3. **Run**:
   ```
   python app.py
   ```
   - Server starts at `http://localhost:5000`.
   - On first run: registration (login/password). DB (`uptime.db`) creates automatically.

## What You Can Do

- **Monitor**: Add URLs (with interval from 3 sec, timeout, redirects, groups). Service pings asynchronously.
  
- **View**: On dashboard (`/`): uptime charts (colors: green/red via RGB formula), auto-refresh. Customizable Markdown description and logo.

- **Administer** (`/admin/` after login):
  - Create/edit/delete monitors.
  - Upload logo (PNG/JPG etc., up to 50 MB).
  - Change title and Markdown.

- **API**: GET/POST for stats (`/api/hourinfo`), monitors (`/api/createMonitor` etc.). Rate limiting: 15 requests/5 sec.

