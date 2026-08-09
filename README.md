# Home Fit Daily — Automation Pipeline

Fully automated daily pipeline: researches a trending topic → grounds it
in real facts → writes a segmented script with emotion tags → generates
voiceover (alternating female/male coach by day) → generates matching AI
images → assembles a finished vertical video → writes platform titles/
descriptions/hashtags → uploads everything to Google Drive. No manual
paste-into-Flow step — this produces a finished video by itself.

## Pipeline order (src/main.py runs these in sequence)

topic → research → script → voiceover → images → video assembly →
platform metadata → Drive upload

Each step's output feeds the next step's input. If platform-metadata
generation or the Drive upload fails, the pipeline still keeps the video
it already built (see the try/except blocks in `main.py`) — a partial
success beats losing a finished video over one broken step.

## One-time setup — everything below is done on github.com and
## console.cloud.google.com, no local machine required.

### 1. LLM API key (script writing + metadata)
- Free option: [Groq](https://console.groq.com) (fast, generous free tier) — set `LLM_PROVIDER` to `groq`
- Or: [Google AI Studio](https://aistudio.google.com/apikey) for a Gemini key — set `LLM_PROVIDER` to `gemini` (this is the default if unset)
- Repo → **Settings → Secrets and variables → Actions**:
  - New **repository variable**: `LLM_PROVIDER` = `gemini` or `groq`
  - New **repository secret**: `LLM_API_KEY` = your key

### 2. Google Drive — OAuth setup (not a service account)
A service account can't upload into a personal Gmail's storage (it has
its own 0-byte quota) — so this uses OAuth, acting as your real account.

**a. Create OAuth credentials:**
1. console.cloud.google.com → create/select a project → enable the **Google Drive API**
2. **APIs & Services → Credentials → Create Credentials → OAuth client ID**
3. Application type: **Desktop app** → Create
4. Copy the **Client ID** and **Client Secret** shown

**b. Get a refresh token (one-time, run once on your own computer or in this project's own Actions run using the snippet below):**

Run this once, locally, in any Python environment with `pip install google-auth-oauthlib`:

```python
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_config(
    {
        "installed": {
            "client_id": "YOUR_CLIENT_ID",
            "client_secret": "YOUR_CLIENT_SECRET",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    },
    scopes=["https://www.googleapis.com/auth/drive.file"],
)
creds = flow.run_local_server(port=0)
print("Refresh token:", creds.refresh_token)
```

This opens a browser once, asks you to log into the Google account you
want files uploaded to, and prints a refresh token — grab it, you only
do this once (it doesn't expire unless you revoke access).

**c. Create the Drive folder and get its ID:**
- Make a folder in your Drive, open it, copy the ID from the URL:
  `https://drive.google.com/drive/folders/<THIS_PART>`

**d. Add to GitHub:**
- Secrets: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`
- Variable: `GDRIVE_FOLDER_ID`

### 3. Push the repo
- Create a new GitHub repo, upload this whole folder (drag-and-drop
  through the GitHub website works, or `git push` if you use the command
  line) — keep `.github/workflows/` exactly where it is.
- Go to the **Actions** tab, enable workflows if prompted.

## Running it

- Runs automatically at the time set in
  `.github/workflows/daily-video.yml` (`cron: "0 0 * * *"` — edit this,
  cron is always UTC).
- Run immediately: **Actions → Daily Home-Fit Video → Run workflow**.
- Every run also saves an artifact (video + metadata) on the run's page,
  even when the Drive upload step is skipped or fails.

## Customizing

- `config.yaml` — everything content-related lives here: character
  descriptions/voices, topic keyword list, script segment count/length,
  video resolution. Change this, not the code, for most tweaks.
- Character alternation (female on even days / male on odd days) is in
  `src/main.py`, function `pick_todays_character`.
- To swap the free image generator (Pollinations) or free voice engine
  (edge-tts) for a paid one later, only `generate_ai_visuals.py` and
  `tts.py` need to change — every other file is unaffected.

## Files

```
config.yaml                          — all content/behavior settings
requirements.txt                     — Python dependencies
.github/workflows/daily-video.yml    — daily trigger + secrets wiring
src/main.py                          — orchestrator
src/fetch_topics.py                  — Reddit-based trend research + fallback list
src/research_topic.py                — Wikipedia fact-grounding
src/llm_client.py                    — provider-agnostic LLM caller w/ model fallback
src/generate_script.py               — segmented script + emotion tags
src/tts.py                           — emotion-aware voiceover generation
src/generate_ai_visuals.py           — free AI image generation per segment
src/assemble_video.py                — Ken Burns video assembly, audio-synced
src/generate_platform_metadata.py    — titles/descriptions/hashtags
src/generate_flow_prompts.py         — OPTIONAL: Google Flow JSON export
src/upload_drive.py                  — OAuth-based Drive upload
```
