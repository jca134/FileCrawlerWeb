import re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]


def get_folder_id(url):
    match = re.search(r"/folders/([a-zA-Z0-9_-]+)", url)
    if not match:
        raise ValueError("Invalid Google Drive folder URL")
    return match.group(1)


def get_folder_permissions(folder_url):
    folder_id = get_folder_id(folder_url)

    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    drive = build("drive", "v3", credentials=creds)

    # Get files directly inside the folder
    response = drive.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id, name)",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()

    for file in response.get("files", []):
        permissions = drive.permissions().list(
            fileId=file["id"],
            fields="permissions(type, role, emailAddress, domain, allowFileDiscovery)",
            supportsAllDrives=True,
        ).execute()

        print(f"\n{file['name']}")

        for p in permissions.get("permissions", []):
            print(
                f"  Type: {p.get('type')}, "
                f"Role: {p.get('role')}, "
                f"Email: {p.get('emailAddress')}, "
                f"Domain: {p.get('domain')}"
            )


folder_url = input("Google Drive folder URL: ")
get_folder_permissions(folder_url)