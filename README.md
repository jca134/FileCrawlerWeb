# FileCrawler

FileCrawler uses the Google Drive API to inspect files in a Google Drive
folder and retrieve their sharing permissions.

## Project Structure

``` text
FileCrawler/
├── .gitignore
├── .python-version
├── README.md
├── pyproject.toml
├── uv.lock
├── credentials.json          # Git-ignored Google OAuth credentials
├── token.json                # Git-ignored generated OAuth token
├── .venv/                    # Git-ignored virtual environment
└── src/
    └── filecrawler/
        ├── __init__.py
        └── api/
            ├── auth.py       # Runs Google OAuth and creates token.json
            └── api_utils.py  # Reads a Drive folder and lists file permissions
```

## Prerequisites

You will need:

-   Access to the **FileCrawler** repository
-   Access to the **fileCrawler** Google Cloud project
-   A Google account authorized to use the FileCrawler OAuth application
-   [uv](https://docs.astral.sh/uv/) installed

Dependencies are managed using `uv`. The repository already contains
`pyproject.toml` and `uv.lock`.

## 1. Clone the Repository

``` bash
git clone <repository-url>
cd FileCrawler
```

## 2. Set Up the Environment

Run:

``` bash
uv sync
```

This creates the `.venv` virtual environment and installs the
dependencies specified by `pyproject.toml` and `uv.lock`.

You do not need to manually activate the virtual environment when using
`uv run`.

## 3. Download `credentials.json`

Google OAuth requires an OAuth client configuration file. This file is
intentionally not stored in Git.

To download it:

1.  Open the [Google Cloud Console](https://console.cloud.google.com/).
2.  Select the **fileCrawler** project.
3.  Go to **Google Auth Platform → Clients**.
4.  Select the Desktop OAuth client used by FileCrawler.
5.  Download the OAuth client JSON.
6.  Rename the downloaded file to:

``` text
credentials.json
```

7.  Place it in the **root of the repository**:

``` text
FileCrawler/
├── credentials.json
├── pyproject.toml
├── uv.lock
└── src/
```

Do not place `credentials.json` inside `src/`.

> **Never commit `credentials.json` to Git.**

## 4. Make Sure Your Google Account Can Use FileCrawler

If the OAuth application is in testing mode, your Google account may
need to be registered as a test user.

In the Google Cloud Console, go to:

**Google Auth Platform → Audience → Test users**

Make sure the Google account you intend to use is listed.

## 5. Generate Your `token.json`

From the root of the repository, run:

``` bash
uv run python src/filecrawler/api/auth.py
```

A browser window should open asking you to sign into Google.

Sign into the Google account whose Drive you want FileCrawler to access
and approve the requested permissions.

After successful authentication, `auth.py` will create:

``` text
token.json
```

in the repository root.

Your local repository should now look approximately like:

``` text
FileCrawler/
├── credentials.json
├── token.json
├── .venv/
├── pyproject.toml
├── uv.lock
└── src/
```

`token.json` contains authorization for **your individual Google
account**.

Each collaborator should generate their own `token.json`.

> **Never commit or share `token.json`.**

## 6. Run the Drive API Script

Once `token.json` has been generated, run:

``` bash
uv run python src/filecrawler/api/api_utils.py
```

If prompted for a Google Drive folder URL, provide a URL such as:

``` text
https://drive.google.com/drive/folders/FOLDER_ID
```

The script will use your Google authorization to inspect the files in
that folder and retrieve their permission information.

## Authentication Overview

All collaborators use the same Google Cloud project and OAuth
application, but each collaborator authorizes their own Google account.

``` text
              fileCrawler Google Cloud Project
                           |
                    OAuth Client
                           |
                   credentials.json
                           |
              +------------+------------+
              |                         |
         Collaborator A             Collaborator B
              |                         |
            auth.py                   auth.py
              |                         |
          Google Login                Google Login
              |                         |
          token.json                  token.json
        (A's account)               (B's account)
```

### `credentials.json`

`credentials.json` identifies the OAuth client associated with the
shared FileCrawler Google Cloud project.

Each collaborator can download the OAuth client configuration from the
shared Google Cloud project and place it in their local repository.

### `token.json`

`token.json` contains authorization for an individual Google account.

Every collaborator should generate their own token by running:

``` bash
uv run python src/filecrawler/api/auth.py
```

## Resetting Authentication

If you need to authenticate with a different Google account, or if the
requested OAuth scopes change, delete your existing token:

``` bash
rm token.json
```

Then run:

``` bash
uv run python src/filecrawler/api/auth.py
```

again.

A new `token.json` will be generated.

## Git-Ignored Files

The following should **not** be committed:

``` gitignore
# Google OAuth
credentials.json
token.json

# Local Python environment
.venv/
```

The following dependency-management files **should be committed**:

``` text
.python-version
pyproject.toml
uv.lock
```

This allows collaborators to reproduce the development environment with:

``` bash
uv sync
```

## Common Issues

### `credentials.json` not found

Make sure you are running the scripts from the root of the repository
and that the file exists at:

``` text
FileCrawler/credentials.json
```

You can download it from:

**Google Cloud Console → fileCrawler → Google Auth Platform → Clients**

### Google blocks authentication

If the OAuth application is in testing mode, check that your Google
account is listed under:

**Google Auth Platform → Audience → Test users**

### Authentication fails after OAuth scopes change

Delete the existing token:

``` bash
rm token.json
```

Then regenerate it:

``` bash
uv run python src/filecrawler/api/auth.py
```

## Development

Application code lives under:

``` text
src/filecrawler/
```

Google Drive API functionality is located under:

``` text
src/filecrawler/api/
```

-   `auth.py` handles Google OAuth authentication and creates
    `token.json`.
-   `api_utils.py` interacts with Google Drive and retrieves file
    permission information.

After pulling changes that modify `pyproject.toml` or `uv.lock`, run:

``` bash
uv sync
```

to update your local environment.
