### Project SessionReplay

This project is a Python-based application that analyzes screen recording videos to automatically generate a detailed log of user interactions and a final, step-by-step instructional guide.

It moves beyond simple computer vision and uses a powerful multimodal Large Language Model (Google's Gemini) to understand the context of user actions, read text on the screen, and transcribe audio.
How It Works: An AI-Powered Pipeline

The application processes videos in a sophisticated, multi-stage pipeline to transform raw pixels into a structured, useful guide.

    Pre-processing: The video is first sampled to extract key frames at a regular interval (e.g., every 2 seconds) and its audio track is saved as a .wav file.

    LLM Vision Analysis: Each pair of frames is sent to the Gemini API, which analyzes the differences to identify user actions like clicks, typing, or scrolling. This produces a raw log of low-level events.

    Event Consolidation: The raw log is processed to merge fragmented actions. For example, multiple consecutive typing events are combined into a single, coherent "user typed..." event, creating a much cleaner log.

    Audio Transcription: The extracted audio file is sent to the Gemini API to be transcribed into text. The system gracefully handles videos that have no audio track.

    Final Report Generation: A final LLM call synthesizes the consolidated events and the audio transcript to create a human-readable, step-by-step guide in a .txt file.

Setup Instructions
1. Prerequisites

    Python 3.8+

    FFmpeg: This must be installed on your system and accessible from the command line. It's used for video processing. You can download it from ffmpeg.org.

2. Get Your Google Gemini API Key

This project relies on the Google Gemini API for its core functionality.

    Go to Google AI Studio at aistudio.google.com.

    Create a new project and get your API key.

3. Set Up the Environment

Clone the repository and set up a Python virtual environment.

# Clone the repository
git clone <repository_url>
cd session_replay

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`

# Install the required Python libraries
pip install -r requirements.txt

4. Configure Your API Key

You must set your Gemini API key as an environment variable. Open your terminal and run the following command, using quotes and replacing "YOUR_API_KEY_HERE" with the key you obtained.

On macOS/Linux:

export GEMINI_API_KEY="YOUR_API_KEY_HERE"

On Windows (Command Prompt):

set GEMINI_API_KEY="YOUR_API_KEY_HERE"

Running the Analysis

With your environment activated and the API key set, run the analysis using the main.py script.

python main.py --video path/to/your/video.mp4

Options

    --video: (Required) The path to the screen recording you want to analyze.

    --keep-temp-files: (Optional) Add this flag to prevent the script from deleting the temporary frame and audio files after the analysis is complete. This is useful for debugging.

Understanding the Output

After a successful run, an output folder will be created (e.g., output/your_video_20250925_172900/). Inside, you will find the complete set of generated artifacts:

    raw_llm_events.json: The unfiltered, frame-by-frame event log as returned by the AI. Useful for debugging the visual analysis stage.

    final_session_log.json: The polished, consolidated event log. Consecutive typing actions are merged here. This is the ideal file for feeding into a UI.

    audio_transcription.txt: A text file containing the transcription of any spoken words from the video. If no audio was present, this file will state that.

    step_by_step_instructions.txt: The final deliverable. A human-readable guide synthesized from both the user's actions and their spoken words.

    screenshots/: A folder containing image snapshots corresponding to each event in the final_session_log.json.

Important Notes & Limitations

    Internet Connection Required: This application relies on API calls to Google and will not work offline.

    Performance: The analysis speed is primarily limited by the API's latency and rate limits. The script includes an automatic "exponential backoff" mechanism to handle rate limits gracefully, but this can slow down processing for long videos.

    Cost: Be mindful that analyzing long videos will result in many API calls, which may incur costs depending on your Google AI Platform usage and billing.
