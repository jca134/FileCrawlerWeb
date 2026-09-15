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

The repository includes the desktop OAuth client configuration in
`credentials.json`, so no additional Google Cloud setup or credential download
is required.

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

## Project Structure

```text
FileCrawler/
├── credentials.json          # Shared desktop OAuth client configuration
├── token.json                # Per-user authorization; generated locally
├── pyproject.toml            # Project metadata and dependencies
├── uv.lock                   # Locked dependency versions
└── src/filecrawler/
    └── api/
        ├── auth.py           # Generates token.json
        └── api_utils.py      # Inspects Drive file permissions
```

## Credential Safety

`credentials.json` is committed for convenience while this is a private,
team-only project. Before making the repository public, review the production
OAuth strategy and replace or restrict the development OAuth client as needed.

`token.json` grants access associated with an individual Google account. Never
commit or share it. It is excluded by `.gitignore`, along with `.venv/`.
