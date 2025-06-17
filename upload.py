import os, pathlib, io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SERVICE_ACCOUNT_FILE = os.environ["SERVICE_ACCOUNT_FILE"]
DRIVE_FOLDER_ID      = os.environ["DRIVE_FOLDER_ID"]
CSV_NAME             = os.getenv("CSV_NAME", "dataset.csv")

def main():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/drive.file"],
    )
    drive = build("drive", "v3", credentials=creds)

    here = pathlib.Path(__file__).parent
    csv_path = here / CSV_NAME
    if not csv_path.exists():
        raise FileNotFoundError(f"{csv_path} not found")

    # --- look for an existing file with the same name in the folder ---
    query = (
        f"'{DRIVE_FOLDER_ID}' in parents "
        f"and name = '{CSV_NAME}' "
        f"and trashed = false"
    )
    resp = drive.files().list(q=query, spaces="drive", fields="files(id)").execute()
    existing_id = resp["files"][0]["id"] if resp["files"] else None

    media = MediaIoBaseUpload(io.FileIO(csv_path, "rb"), mimetype="text/csv", resumable=True)

    if existing_id:
        # replace contents, keep the same file URL
        drive.files().update(fileId=existing_id, media_body=media).execute()
        print(f"✅ Replaced contents of {CSV_NAME} (fileId={existing_id})")
    else:
        # first-time upload
        file_meta = {"name": CSV_NAME, "parents": [DRIVE_FOLDER_ID]}
        drive.files().create(body=file_meta, media_body=media).execute()
        print(f"✅ Uploaded new {CSV_NAME}")

if __name__ == "__main__":
    main()