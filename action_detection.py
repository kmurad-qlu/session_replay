import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import os
import pytesseract
from PIL import Image

# NEW: Define a cooldown period (in seconds) to prevent typing from being registered as rapid clicks.
CLICK_COOLDOWN = 2.0 

def track_cursor(frame, cursor_template):
    """
    Finds the cursor in a frame using template matching.
    This is a simplified prototype function.
    """
    if cursor_template is None:
        return None
        
    # Convert both to grayscale
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    res = cv2.matchTemplate(frame_gray, cursor_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the match is good enough, return the location
    # LOWERED THRESHOLD: Made it less strict to allow for small variations.
    if max_val > 0.6: 
        w, h = cursor_template.shape[::-1]
        top_left = max_loc
        # Return center of the cursor
        return (top_left[0] + w // 2, top_left[1] + h // 2)
    # ADDED FOR DEBUGGING: See the matching score in your console.
    elif max_val > 0.1:
        # This is very noisy, so let's comment it out for now.
        # print(f"  [Debug Action] Cursor match was too low: {max_val:.2f}")
        pass
    return None

def detect_significant_change(frame1, frame2):
    """
    Detects significant visual changes between two frames, ignoring cursor movement.
    This can indicate a click animation or window change.
    """
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    
    score, diff = ssim(gray1, gray2, full=True)
    
    # ADDED FOR DEBUGGING: See the frame similarity score.
    # A score closer to 1.0 means the frames are very similar.
    # print(f"  [Debug Action] Frame similarity score: {score:.4f}")
    
    # LOWERED THRESHOLD: A lower score means more difference. 
    # This now catches more subtle changes.
    return score < 0.98

def identify_clicked_element_text(frame, click_pos, search_radius=100):
    """
    When a click is detected, perform targeted OCR in a box around the click
    to identify the text of the element (e.g., a button label).
    """
    x, y = click_pos
    
    # Define a bounding box around the click position
    # The box is larger than the cursor to capture the whole button/link
    start_x = max(0, x - search_radius // 2)
    start_y = max(0, y - search_radius)
    end_x = min(frame.shape[1], x + search_radius // 2)
    end_y = min(frame.shape[0], y + search_radius)

    # Crop the image to the region of interest
    roi = frame[start_y:end_y, start_x:end_x]

    # Pre-process the ROI for better OCR results
    # Convert to grayscale, apply thresholding to get clear black/white text
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, thresh_roi = cv2.threshold(gray_roi, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Use Pytesseract to find text in the pre-processed region
    try:
        # Convert OpenCV image (NumPy array) to PIL Image
        pil_img = Image.fromarray(thresh_roi)
        text = pytesseract.image_to_string(pil_img, config='--psm 6').strip()
        # Clean up common OCR noise by keeping only alphanumeric characters
        cleaned_text = ''.join(char for char in text if char.isalnum())
        return cleaned_text if cleaned_text else "Unknown Element"
    except Exception as e:
        print(f"  [OCR Warning] Could not extract text from clicked element: {e}")
        return "Unknown Element"


def process_actions(frame_files, cursor_template_path):
    """
    Main function for the action detection module.
    """
    print("Processing frames for action detection...")
    events = []
    cursor_template = cv2.imread(cursor_template_path, cv2.IMREAD_GRAYSCALE)
    if cursor_template is None:
        print(f"Warning: Failed to load cursor template from {cursor_template_path}. Cursor tracking disabled.")

    prev_frame = None
    last_event_timestamp = -CLICK_COOLDOWN # Initialize to allow an immediate first event

    for i, frame_path in enumerate(frame_files):
        frame = cv2.imread(frame_path)
        if frame is None:
            continue
            
        timestamp = i * 5 / 1.0 
        
        cursor_pos = track_cursor(frame, cursor_template)
        
        if prev_frame is not None:
            is_change = detect_significant_change(prev_frame, frame)

            # Only register a change as a click if it's outside the cooldown period
            if is_change and cursor_pos and (timestamp > last_event_timestamp + CLICK_COOLDOWN):
                print(f"  -> Click detected at timestamp {timestamp:.2f}!")
                
                element_text = identify_clicked_element_text(prev_frame, cursor_pos)
                print(f"    -> Clicked on element with text: '{element_text}'")

                events.append({
                    "timestamp": timestamp,
                    "eventType": "click",
                    "targetElement": {
                        "bbox": [cursor_pos[0]-10, cursor_pos[1]-10, cursor_pos[0]+10, cursor_pos[1]+10],
                        "text": element_text
                    },
                    "value": f"Potential click detected at {cursor_pos}"
                })
                
                # Update the timestamp of the last registered event
                last_event_timestamp = timestamp
            elif is_change:
                # This helps see the changes that are being ignored due to the cooldown
                # print(f"  -> Change detected at {timestamp:.2f} but ignored (cooldown).")
                pass
        
        prev_frame = frame
        
        if i % 20 == 0:
            print(f"  ...processed action frame {i}/{len(frame_files)}")
            
    return events

