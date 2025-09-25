

# Project: SessionReplay

SessionReplay is a Python-based application that analyzes screen recordings to automatically generate a detailed log of user interactions and a final **step-by-step instructional guide**.

Unlike traditional computer vision approaches, SessionReplay uses a **multimodal Large Language Model (Google Gemini)** to understand user actions in context, read on-screen text, and transcribe audio.

---

## 🚀 How It Works: AI-Powered Pipeline

The system transforms raw video into a structured instructional guide through a multi-stage pipeline:

1. **Pre-processing**

   * Extracts key frames from the video at regular intervals (e.g., every 2 seconds).
   * Saves the audio track as a `.wav` file.

2. **Vision Analysis (LLM)**

   * Sends frame pairs to the Gemini API.
   * Detects user actions (clicks, typing, scrolling, etc.).
   * Produces a raw log of low-level events.

3. **Event Consolidation**

   * Cleans the raw log by merging fragmented actions.
   * Example: multiple typing events → `"user typed ..."` consolidated entry.

4. **Audio Transcription**

   * Transcribes the `.wav` file with Gemini.
   * Handles videos with or without audio gracefully.

5. **Final Report Generation**

   * Combines consolidated events and transcription.
   * Produces a **human-readable step-by-step guide**.

---

## ⚙️ Setup Instructions

### 1. Prerequisites

* Python **3.8+**
* [**FFmpeg**](https://ffmpeg.org/) (must be installed and in your system path)

### 2. Get Your Google Gemini API Key

* Visit [Google AI Studio](https://aistudio.google.com/).
* Create a project and obtain an API key.

### 3. Set Up the Environment

```bash
# Clone the repository
git clone <repository_url>
cd session_replay

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Your API Key

Set your Gemini API key as an environment variable:

**macOS/Linux:**

```bash
export GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

**Windows (Command Prompt):**

```bash
set GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

---

## ▶️ Running the Analysis

Run the main script with your video:

```bash
python main.py --video path/to/your/video.mp4
```

### Options

* `--video` (**required**) → Path to the screen recording.
* `--keep-temp-files` (**optional**) → Keep temporary frame/audio files (useful for debugging).

---

## 📂 Output

After a successful run, results are saved in a new `output/<video_name_timestamp>/` folder, containing:

* **`raw_llm_events.json`** → Raw frame-by-frame events from Gemini (debugging).
* **`final_session_log.json`** → Consolidated, polished event log.
* **`audio_transcription.txt`** → Transcription of spoken words (or a note if no audio).
* **`step_by_step_instructions.txt`** → Final human-readable instructional guide.
* **`screenshots/`** → Frame snapshots linked to each event in the log.

---

## ⚠️ Notes & Limitations

* **Internet Required** → All analysis depends on Gemini API calls.
* **Performance** → Limited by API latency and rate limits (with exponential backoff).
* **Costs** → Long videos may incur significant API usage charges.

