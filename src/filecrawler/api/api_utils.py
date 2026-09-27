import re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]

RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RESET = "\033[0m"

RISK_COLORS = {"RED": RED, "YELLOW": YELLOW, "GREEN": GREEN}

RISK_LABELS = {
    "RED": "Publicly accessible",
    "YELLOW": "Restricted sharing (specific people/domain/group)",
    "GREEN": "Private (owner only)",
}


def get_folder_id(url):
    match = re.search(r"/folders/([a-zA-Z0-9_-]+)", url)
    if not match:
        raise ValueError("Invalid Google Drive folder URL")
    return match.group(1)


def classify_file_risk(permissions):
    """
    RED: anyone with the link (or a public/discoverable link) can access it
    YELLOW: shared with specific people, a domain, or a group (restricted sharing)
    GREEN: private: only the owner has access, not shared with anyone
    """
    is_shared = False
    for p in permissions:
        p_type = p.get("type")
        if p_type == "anyone":
            return "RED"
        if p_type in ("domain", "group"):
            is_shared = True
        elif p_type == "user" and p.get("role") != "owner":
            is_shared = True
    return "YELLOW" if is_shared else "GREEN"


def scan_folder(folder_url, creds=None):
    folder_id = get_folder_id(folder_url)

    if creds is None:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    drive = build("drive", "v3", credentials=creds)

    response = drive.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id, name, webViewLink, owners(displayName, emailAddress))",
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()

    results = []

    for file in response.get("files", []):
        permissions = drive.permissions().list(
            fileId=file["id"],
            fields="permissions(type, role, emailAddress, domain, allowFileDiscovery)",
            supportsAllDrives=True,
        ).execute().get("permissions", [])

        owners = file.get("owners") or []
        if owners:
            owner = owners[0].get("emailAddress") or owners[0].get("displayName")
        else:
            owner = None

        results.append({
            "name": file["name"],
            "id": file["id"],
            "risk": classify_file_risk(permissions),
            "permissions": permissions,
            "owner": owner,
            "link": file.get("webViewLink"),
        })

    return results


def print_report(results):
    counts = {"RED": 0, "YELLOW": 0, "GREEN": 0}

    print("\n" + "=" * 60)
    print("Drive Sharing Security Scan Report")
    print("=" * 60)

    for r in results:
        counts[r["risk"]] += 1
        color = RISK_COLORS[r["risk"]]
        print(f"\n{color}[{r['risk']}]{RESET} {r['name']} - {RISK_LABELS[r['risk']]}")
        print(f"    Owner: {r['owner']}")
        print(f"    Link:  {r['link']}")
        for p in r["permissions"]:
            print(
                f"    Type: {p.get('type')}, "
                f"Role: {p.get('role')}, "
                f"Email: {p.get('emailAddress')}, "
                f"Domain: {p.get('domain')}"
            )

    print("\nSummary")
    print(f"Files scanned: {len(results)}")
    print(f"  {RED}RED    (public):             {counts['RED']}{RESET}")
    print(f"  {YELLOW}YELLOW (restricted sharing): {counts['YELLOW']}{RESET}")
    print(f"  {GREEN}GREEN  (private):            {counts['GREEN']}{RESET}")

if __name__ == "__main__":
    folder_url = input("Google Drive folder URL: ")
    scan_results = scan_folder(folder_url)
    print_report(scan_results)
