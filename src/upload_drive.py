"""
upload_drive.py — uploads today's output files to a Google Drive folder
using OAuth (refresh token), NOT a service account.

Why OAuth and not a service account: a service account is its own
"robot" identity with zero storage of its own. When it uploads a file to
your folder, it's still the file's owner internally, and it needs its own
quota to do that — which is 0 on a personal Gmail account (this only
works differently inside a paid Google Workspace org with Shared Drives).
OAuth instead acts AS your own account, using your real storage quota, so
it works on a normal personal Google account.

One-time setup (see README.md for the click-by-click version):
  1. Create an OAuth Client ID (type: Desktop app) in Google Cloud Console.
  2. Use it once, interactively, to get a refresh token (a short helper
     script for this is in README.md — you only ever run it once, locally).
  3. Store three values as GitHub Secrets:
       GOOGLE_CLIENT_ID
       GOOGLE_CLIENT_SECRET
       GOOGLE_REFRESH_TOKEN
"""

import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

TOKEN_URI = "https://oauth2.googleapis.com/token"
SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_drive_service():
    credentials = Credentials(
        token=None,  # no access token yet — the library fetches one automatically below
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        token_uri=TOKEN_URI,
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        scopes=SCOPES,
    )
    return build("drive", "v3", credentials=credentials)


def upload_file(service, local_path, filename, folder_id, mime_type="application/octet-stream"):
    file_metadata = {"name": filename, "parents": [folder_id]}
    media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
    uploaded = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"[upload_drive] uploaded {filename} -> file id {uploaded.get('id')}")
    return uploaded.get("id")


def upload_daily_outputs(video_path: str, metadata_path: str, folder_id: str, date_str: str):
    service = _get_drive_service()
    upload_file(service, video_path, f"{date_str}-video.mp4", folder_id, "video/mp4")
    upload_file(service, metadata_path, f"{date_str}-metadata.txt", folder_id, "text/plain")


if __name__ == "__main__":
    print("Import and call upload_daily_outputs(...) from main.py — not meant to run standalone.")
