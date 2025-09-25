import pytesseract
from PIL import Image
import speech_recognition as sr
import os
import difflib # <-- NEW IMPORT: To compare text between frames

def ocr_frame(frame_path):
    """
    Performs OCR on a single frame to extract all visible text.
    """
    try:
        return pytesseract.image_to_string(Image.open(frame_path)).strip()
    except Exception as e:
        print(f"OCR Error on {frame_path}: {e}")
        return ""

def transcribe_audio(audio_path):
    """
    Transcribes an audio file using SpeechRecognition library.
    Uses CMU Sphinx for offline processing if available, otherwise notes it.
    """
    if audio_path is None or not os.path.exists(audio_path):
        return "No audio to transcribe."

    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = r.record(source)  # read the entire audio file

    try:
        # Using recognize_sphinx for offline, engine-free recognition
        # This requires pocketsphinx to be installed (`pip install pocketsphinx`)
        # It's less accurate than cloud APIs but works offline.
        text = r.recognize_sphinx(audio)
        print("Sphinx transcription successful.")
        return text
    except sr.UnknownValueError:
        return "Sphinx could not understand audio"
    except sr.RequestError as e:
        return f"Sphinx error; {e}. Could not request results from Sphinx service"
    except Exception as e:
        # Fallback message if sphinx is not installed or fails
        print(f"Could not perform offline transcription: {e}")
        return "Audio present but offline transcription failed. (Requires pocketsphinx)"


def process_text(frame_files, audio_path, action_events):
    """
    Main function for the text capture module.
    NEW STRATEGY: Proactively compares OCR results between frames to find typed text.
    """
    print("Processing for text capture...")
    events = []
    
    # 1. Transcribe Audio (no changes)
    transcribed_text = transcribe_audio(audio_path)
    if transcribed_text:
        events.append({
            "timestamp": 0, # Assume narration starts at the beginning
            "eventType": "speak",
            "value": transcribed_text,
            "targetElement": None
        })

    # 2. NEW: Frame-by-frame OCR diffing to detect typed text
    print("  -> Scanning frames for typed text...")
    prev_text = ""
    for i, frame_path in enumerate(frame_files):
        timestamp = i * 5 / 1.0
        
        # We can sample frames to improve performance
        if i % 2 != 0: # Check every 2nd sampled frame
            continue
            
        current_text = ocr_frame(frame_path)
        
        if prev_text:
            # Use difflib to find what was ADDED to the text on screen
            matcher = difflib.SequenceMatcher(None, prev_text.split(), current_text.split())
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'insert':
                    typed_words = " ".join(current_text.split()[j1:j2])
                    # Clean up the text - often OCR adds stray newlines
                    cleaned_typed_text = typed_words.replace('\n', ' ').strip()
                    if cleaned_typed_text:
                        print(f"  -> Typing detected at {timestamp:.2f}: '{cleaned_typed_text}'")
                        events.append({
                           "timestamp": timestamp,
                           "eventType": "type",
                           "value": cleaned_typed_text,
                           "targetElement": None # BBox could be added in a future version
                       })

        prev_text = current_text
        
    return events

