import os, datetime, pathlib
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ----- config pulled from Render -----
DRIVE_FOLDER_ID = os.environ["DRIVE_FOLDER_ID"]      # set in Render dashboard
CSV_NAME        = os.getenv("CSV_NAME", "webflow_requests.csv")  # defaults to dataset.csv
SERVICE_ACCOUNT_FILE = "service_account.json"        # mounted private file
# -------------------------------------

def main():
    # 1. Auth
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/drive.file"],
    )
    drive = build("drive", "v3", credentials=creds)

    # 2. Locate the CSV (same dir as script)
    here = pathlib.Path(__file__).parent
    csv_path = here / CSV_NAME

    if not csv_path.exists():
        raise FileNotFoundError(f"💥 {csv_path} not found")

    # 3. Build metadata
    stamp = datetime.date.today().isoformat()
    file_meta = {
        "name": f"{csv_path.stem}_{stamp}{csv_path.suffix}",
        "parents": [DRIVE_FOLDER_ID],
    }
    media = MediaFileUpload(csv_path, mimetype="text/csv")

    # 4. Upload
    drive.files().create(body=file_meta, media_body=media, fields="id").execute()
    print(f"✅ Uploaded {csv_path.name} as {file_meta['name']}")

if __name__ == "__main__":
    main()