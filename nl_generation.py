from math import sqrt

def point_in_bbox(point, bbox):
    """Check if a point (x, y) is inside a bounding box [x1, y1, x2, y2]."""
    return bbox[0] <= point[0] <= bbox[2] and bbox[1] <= point[1] <= bbox[3]

def get_bbox_center(bbox):
    """Get the center of a bounding box."""
    return ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)

def generate_narrative(events):
    """
    Generates a human-readable description for each event, now using
    the rich context we've extracted (element text, typed characters).
    """
    print("Generating narrative descriptions...")
    
    for event in events:
        event_type = event.get("eventType")
        timestamp = event.get("timestamp")
        
        # Default description
        desc = f"At {timestamp:.2f}s, an event of type '{event_type}' occurred."
        
        if event_type == "click":
            element_text = event.get("targetElement", {}).get("text")
            if element_text and element_text != "Unknown Element":
                desc = f"At {timestamp:.2f}s, the user clicked the '{element_text}' element."
            else:
                bbox = event.get("targetElement", {}).get("bbox")
                center = get_bbox_center(bbox)
                desc = f"At {timestamp:.2f}s, the user clicked near position {center} on an unidentified element."
        
        elif event_type == "type":
            value = event.get("value", "")
            desc = f"At {timestamp:.2f}s, the user typed: '{value}'"
            
        elif event_type == "speak":
            value = event.get("value", "")
            desc = f"At {timestamp:.2f}s, the user spoke: '{value}'"
            
        event["naturalLanguageDescription"] = desc
        
    return events

