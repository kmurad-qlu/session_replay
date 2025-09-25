import os
import requests
import base64

# --- Configuration ---
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={API_KEY}"

def transcribe_audio_file(audio_path, output_dir):
    """
    Transcribes the given audio file, saves the transcription to a text file,
    and returns the transcribed text. Handles cases where no audio is present.
    """
    transcription = "No audio track was found in the video."

    # --- FIX: Check if audio_path is valid before using it ---
    # This block will only run if an audio file was actually extracted.
    if audio_path and os.path.exists(audio_path):
        if not API_KEY:
            print("  [Audio Error] GEMINI_API_KEY not set. Skipping transcription.")
            transcription = "Audio transcription skipped: API key not configured."
        else:
            print(f"  -> Transcribing audio from {os.path.basename(audio_path)}...")
            try:
                with open(audio_path, "rb") as audio_file:
                    audio_b64 = base64.b64encode(audio_file.read()).decode('utf-8')

                payload = {
                    "contents": [{"parts": [{"text": "Transcribe the following audio file. Provide only the transcribed text."},
                                            {"inline_data": {"mime_type": "audio/wav", "data": audio_b64}}]}]
                }
                
                response = requests.post(MODEL_ENDPOINT, json=payload, timeout=120)
                response.raise_for_status()
                response_json = response.json()
                
                if 'candidates' in response_json and response_json['candidates']:
                    # Use .get() for safer dictionary access
                    text = response_json['candidates'][0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()
                    if text:
                        transcription = text
                    else:
                        transcription = "Audio contained no discernible speech."
                else:
                    transcription = "Audio transcription failed due to an unexpected API response."
            except requests.exceptions.RequestException as e:
                transcription = f"Audio transcription failed: {e}"

    # The rest of the function runs regardless, ensuring the file is always created.
    else:
         print("  -> No valid audio file found to transcribe.")

    # Save the result (either the transcription or the 'no audio' message) to a file
    transcription_path = os.path.join(output_dir, "audio_transcription.txt")
    try:
        with open(transcription_path, 'w') as f:
            f.write(transcription)
        print(f"  -> Transcription result saved to {os.path.basename(transcription_path)}")
    except Exception as e:
        print(f"  [File Error] Could not save transcription file. Reason: {e}")

    return transcription

