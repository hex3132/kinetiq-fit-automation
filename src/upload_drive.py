import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN_URI = "https://oauth2.googleapis.com/token"
SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_drive_service():
    credentials = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        token_uri=TOKEN_URI,
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        scopes=SCOPES,
    )
    return build("drive", "v3", credentials=credentials)


def upload_file(service, local_path, filename, folder_id, mime_type="application/octet-stream"):
    file_metadata = {"name": filename, "parents": [folder_id]}
    media = MediaFileUpload(local_path, mimetype=mime_type, resumable=False)
    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id",
        supportsAllDrives=True,
    ).execute()
    print(f"[upload_drive] uploaded {filename} -> file id {uploaded.get('id')}")
    return uploaded.get("id")


def upload_daily_outputs(video_path: str, metadata_path: str, folder_id: str, date_str: str):
    folder_id = folder_id.strip()
    service = _get_drive_service()
    upload_file(service, video_path, f"{date_str}-video.mp4", folder_id, "video/mp4")
    upload_file(service, metadata_path, f"{date_str}-metadata.txt", folder_id, "text/plain")


if __name__ == "__main__":
    print("Import and call upload_daily_outputs(...) from main.py — not meant to run standalone.")
