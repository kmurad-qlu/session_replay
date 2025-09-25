import json
import os
import shutil

def _save_log_to_json(events, filepath):
    """Internal function to save an event log to a JSON file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(events, f, indent=4)
        return True
    except Exception as e:
        print(f"Error: Failed to save JSON log to {filepath}. Reason: {e}")
        return False

def _save_event_screenshots(events, output_dir, frame_files):
    """
    Internal function to copy the relevant frame as a screenshot for each key event.
    """
    screenshots_dir = os.path.join(output_dir, "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)
    
    print("Saving screenshots for key events...")
    
    SECONDS_PER_SAMPLE = 2 # Should match other modules

    for event in events:
        # Use a get call to avoid errors if screenshot is already set (like in consolidated events)
        if event.get('screenshot'):
            # This event already has a screenshot path, likely from consolidation.
            # We just need to ensure the source file exists and copy it.
            source_filename = os.path.basename(event['screenshot'])
            dest_path = os.path.join(screenshots_dir, source_filename)
            
            # Find the original full path of the frame
            frame_index = int(event['timestamp'] / SECONDS_PER_SAMPLE)
            if 0 < frame_index < len(frame_files):
                 source_frame_path = frame_files[frame_index]
                 if os.path.exists(source_frame_path) and not os.path.exists(dest_path):
                     shutil.copy(source_frame_path, dest_path)
            
            # Update the event to point to the final relative path
            event['screenshot'] = os.path.join("screenshots", source_filename)
            continue


        frame_index = int(event['timestamp'] / SECONDS_PER_SAMPLE)

        if 0 < frame_index < len(frame_files):
            source_frame_path = frame_files[frame_index]
            
            screenshot_filename = f"event_at_{event['timestamp']:.0f}s_{event['eventType']}.jpg"
            dest_path = os.path.join(screenshots_dir, screenshot_filename)
            
            try:
                shutil.copy(source_frame_path, dest_path)
                event['screenshot'] = os.path.join("screenshots", screenshot_filename)
            except Exception as e:
                print(f"Warning: Could not save screenshot for event at {event['timestamp']}s. Reason: {e}")
                event['screenshot'] = None
        else:
             event['screenshot'] = None

def format_and_save_output(raw_events, final_events, output_dir, frame_files):
    """
    Main entry point for the output formatter. 
    Saves screenshots and both the raw and final JSON logs.
    """
    # Screenshots are saved based on the final, consolidated events
    _save_event_screenshots(final_events, output_dir, frame_files)
    
    # Save the raw, unedited log for debugging
    raw_log_path = os.path.join(output_dir, "raw_llm_events.json")
    _save_log_to_json(raw_events, raw_log_path)
    print(f"Saved {len(raw_events)} raw events to {raw_log_path}")

    # Save the final, consolidated log for application use
    final_log_path = os.path.join(output_dir, "final_session_log.json")
    _save_log_to_json(final_events, final_log_path)
    print(f"Saved {len(final_events)} final events to {final_log_path}")
        
    return final_log_path

