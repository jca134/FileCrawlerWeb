# FileCrawler

FileCrawler uses the Google Drive API to list the files in a Drive folder and
display their sharing permissions.

## Prerequisites

- A Google account authorized to use the FileCrawler OAuth application
- [uv](https://docs.astral.sh/uv/) installed

## Setup

Clone the repository and install its dependencies:

```bash
git clone <repository-url>
cd FileCrawler
uv sync
```

Ask a project owner for the desktop OAuth client configuration and save it as
`credentials.json` in the repository root. It is not committed to git.

From the repository root, authorize your Google account:

```bash
uv run python src/filecrawler/api/auth.py
```

A browser window will open for Google sign-in and consent. After authorization,
the script creates a local `token.json` for your Google account. Each
collaborator must run this step and generate their own token.

If Google rejects the sign-in while the OAuth application is in testing mode,
ask a project owner to add your account as a test user.

## Run FileCrawler

From the repository root, run:

```bash
uv run python src/filecrawler/api/api_utils.py
```

When prompted, enter a Google Drive folder URL such as:

```text
https://drive.google.com/drive/folders/FOLDER_ID
```

FileCrawler lists the files directly inside that folder and displays their
sharing permissions.

## Web Demo

The same scan is available as a small website, deployable to Vercel. Visitors
sign in with Google, paste a folder URL, and get the red/yellow/green report.

### Google Cloud setup

The web demo needs a **Web application** OAuth client (the desktop client in
`credentials.json` will not work). In Google Cloud Console, under
**APIs & Services → Credentials**, create one and add these authorized
redirect URIs:

```text
http://localhost:8000/auth/callback
https://<your-vercel-domain>/auth/callback
```

While the OAuth app is in testing mode, only listed test users can sign in.

### Run locally

Create a `.env` file in the repository root with the web client's values. It
is excluded by `.gitignore`.

```text
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
SESSION_SECRET=...
```

`SESSION_SECRET` can be any long random string, e.g. from
`python -c "import secrets; print(secrets.token_urlsafe(32))"`.

Load the file into your shell and start the app:

```bash
set -a; source .env; set +a
uv run uvicorn api.index:app --reload
```

Then open http://localhost:8000.

### Deploy to Vercel

1. Import the repository in Vercel (framework preset: **Other**).
2. Add these environment variables:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `SESSION_SECRET`: a long random string, e.g. from
     `python -c "import secrets; print(secrets.token_urlsafe(32))"`
3. Deploy, then add the deployed `/auth/callback` URL to the OAuth client.

## Project Structure

```text
FileCrawler/
├── credentials.json          # Desktop OAuth client; local only, not committed
├── token.json                # Per-user authorization; generated locally
├── .env                      # Web demo environment variables; local only
├── pyproject.toml            # Project metadata and dependencies
├── uv.lock                   # Locked dependency versions
├── vercel.json               # Routes /auth/* and /api/* to the Python app
├── api/
│   └── index.py              # Vercel entrypoint for the web app
├── public/
│   └── index.html            # Web demo page
└── src/filecrawler/
    ├── web.py                # FastAPI app: Google sign-in and scan endpoint
    └── api/
        ├── auth.py           # Generates token.json
        └── api_utils.py      # Inspects Drive file permissions
```

## Credential Safety

`credentials.json` is excluded by `.gitignore`. Earlier commits contain it, so
rotate the desktop client secret before making the repository public.

The web demo only stores the short-lived Google access token, in a signed,
HTTP-only session cookie that expires after an hour. It never stores Drive
data.

`token.json` grants access associated with an individual Google account. Never
commit or share it. It is excluded by `.gitignore`, along with `.env` and
`.venv/`.
