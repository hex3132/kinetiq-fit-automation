import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN_URI = "https://oauth2.googleapis.com/token"
SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_NAME = "Home Fit Videos"


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


def _resolve_folder_id(service, folder_name):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id,name)").execute()
    folders = results.get("files", [])
    if not folders:
        raise RuntimeError(f"No folder named '{folder_name}' found in this Drive account.")
    resolved_id = folders[0]["id"]
    print(f"[upload_drive] resolved '{folder_name}' -> id {resolved_id}")
    return resolved_id


def upload_file(service, local_path, filename, folder_id, mime_type="application/octet-stream"):
    file_metadata = {"name": filename, "parents": [folder_id]}
    media = MediaFileUpload(local_path, mimetype=mime_type, resumable=False)
    uploaded = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"[upload_drive] uploaded {filename} -> file id {uploaded.get('id')}")
    return uploaded.get("id")


def upload_daily_outputs(video_path: str, metadata_path: str, folder_id: str, date_str: str, flow_prompt_path: str = None):
    service = _get_drive_service()
    resolved_folder_id = _resolve_folder_id(service, FOLDER_NAME)

    upload_file(service, video_path, f"{date_str}-video.mp4", resolved_folder_id, "video/mp4")
    upload_file(service, metadata_path, f"{date_str}-metadata.txt", resolved_folder_id, "text/plain")

    if flow_prompt_path and os.path.exists(flow_prompt_path):
        upload_file(service, flow_prompt_path, f"{date_str}-flow-prompt.txt", resolved_folder_id, "text/plain")


if __name__ == "__main__":
    print("Import and call upload_daily_outputs(...) from main.py — not meant to run standalone.")
