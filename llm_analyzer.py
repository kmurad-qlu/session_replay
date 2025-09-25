import os
import base64
import json
import requests
import time
import random

# --- Configuration ---
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={API_KEY}"
MAX_RETRIES = 5

def encode_image_to_base64(image_path):
    """Encodes an image file to a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def construct_llm_prompt(prev_frame_b64, current_frame_b64):
    """
    Creates the structured prompt for the Gemini multimodal API.
    --- NEW: This prompt is heavily upgraded for contextual analysis. ---
    """
    return {
        "contents": [
            {
                "parts": [
                    {"text": """You are an expert UI/UX session replay analyst. Your task is to analyze two sequential screenshots and identify the single, direct user action that occurred.

**Primary Objective:** Focus ONLY on actions directly caused by the user's cursor or keyboard. Ignore automated changes like loading spinners, ads appearing, or content refreshing as a result of a previous action.

**Analysis Steps:**
1. Compare the 'BEFORE' and 'AFTER' frames.
2. Identify the most likely user action: `CLICK`, `TYPE`, `SCROLL`, `PAGE_LOAD`, or `NONE`.
3. A `PAGE_LOAD` occurs when the entire screen layout changes drastically, indicating navigation.
4. For a `CLICK`, describe the element clicked by its visible text label (e.g., 'Search button', 'User profile link').
5. For a `TYPE` action, provide only the new characters that were added.

**Output Format:** Respond ONLY with a single, minified JSON object. Do not use markdown.
{
  "action": "CLICK" | "TYPE" | "SCROLL" | "PAGE_LOAD" | "NONE",
  "target": "For a CLICK, this is the text on the element (e.g., 'Apply Filters'). For TYPE, this is the text that was added.",
  "confidence": "High" | "Medium" | "Low"
}
"""},
                    {"text": "---"},
                    {"text": "BEFORE:"},
                    {"inline_data": {"mime_type": "image/jpeg", "data": prev_frame_b64}},
                    {"text": "AFTER:"},
                    {"inline_data": {"mime_type": "image/jpeg", "data": current_frame_b64}}
                ]
            }
        ]
    }

def clean_llm_response(response_text):
    """Cleans and parses the LLM's JSON response, handling potential formatting issues."""
    if not response_text: return None
    # Find the start and end of the JSON blob
    start = response_text.find('{')
    end = response_text.rfind('}') + 1
    if start == -1 or end == 0:
        return None
    
    json_str = response_text[start:end]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        print(f"  [LLM Error] Failed to decode JSON from response: {json_str}")
        return None

def analyze_frames_with_llm(prev_frame_path, current_frame_path):
    """
    Sends a pair of frames to the LLM for analysis and returns the structured result.
    Includes exponential backoff to handle rate limiting.
    """
    if not API_KEY:
        print("\n[FATAL ERROR] GEMINI_API_KEY environment variable not set.")
        return None

    prev_frame_b64 = encode_image_to_base64(prev_frame_path)
    current_frame_b64 = encode_image_to_base64(current_frame_path)
    
    payload = construct_llm_prompt(prev_frame_b64, current_frame_b64)
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(MODEL_ENDPOINT, json=payload, timeout=60)
            response.raise_for_status()
            
            response_json = response.json()
            
            if 'candidates' in response_json and response_json['candidates']:
                content = response_json['candidates'][0].get('content', {})
                if 'parts' in content and content['parts']:
                    raw_text = content['parts'][0].get('text', '')
                    return clean_llm_response(raw_text)
            
            print(f"  [LLM Error] Unexpected API response format: {response_json}")
            return None

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"    [API Limit Reached] Rate limited. Waiting for {wait_time:.2f} seconds before retrying...")
                time.sleep(wait_time)
            else:
                print(f"  [LLM Error] HTTP request failed with status {e.response.status_code}: {e}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"  [LLM Error] API request failed: {e}")
            return None

    print(f"  [LLM Error] API call failed after {MAX_RETRIES} retries. Halting.")
    return None

