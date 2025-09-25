import os
import json
import requests

# --- Configuration ---
API_KEY = os.getenv("GEMINI_API_KEY")
# Using a model that's good for text generation and summarization.
MODEL_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={API_KEY}"

def generate_step_by_step_report(final_events_json, audio_transcription, output_dir):
    """
    Takes the final event log and audio transcription, and uses an LLM to generate
    a human-readable, step-by-step instruction file.
    """
    if not API_KEY:
        print("  [Report Error] GEMINI_API_KEY not set. Skipping report generation.")
        return

    print("  -> Synthesizing final report...")

    # Prepare the data for the prompt
    events_str = json.dumps(final_events_json, indent=2)

    prompt = f"""
You are an expert technical writer. Your task is to create a clear, concise, step-by-step guide based on a session replay log and an audio transcription.

**CONTEXT:**
1.  **Event Log:** A JSON object detailing user actions on a screen (clicks, typing, scrolling).
2.  **Audio Narration:** A transcription of the user's spoken words during the session, which provides context and intent.

**YOUR TASK:**
Synthesize the information from both sources into a single, easy-to-follow instructional document.
- Merge the user's actions with their narration.
- Interpret the actions. For example, a "TYPE" action followed by a "CLICK" on a 'Search' button should be described as "Search for...".
- Ignore minor or irrelevant events. Focus on the main steps to complete the task.
- Present the output as a numbered list.
- Do not mention timestamps or technical details from the JSON.

**INPUT DATA:**

**1. JSON Event Log:**
```json
{events_str}
```

**2. Audio Narration:**
```text
{audio_transcription}
```

**OUTPUT (Numbered List of Instructions):**
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        response = requests.post(MODEL_ENDPOINT, json=payload, timeout=120)
        response.raise_for_status()
        
        response_json = response.json()
        
        if 'candidates' in response_json and response_json['candidates']:
            content = response_json['candidates'][0].get('content', {})
            if 'parts' in content and content['parts']:
                report_text = content['parts'][0].get('text', '')
                
                # Save the report to a .txt file
                report_path = os.path.join(output_dir, "step_by_step_instructions.txt")
                with open(report_path, 'w') as f:
                    f.write(report_text)
                
                print(f"  -> Successfully generated and saved report to {report_path}")
                return report_path

    except requests.exceptions.RequestException as e:
        print(f"  [Report Error] API request failed: {e}")

    return None
