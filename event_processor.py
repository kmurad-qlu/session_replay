import re

def _clean_typed_text(text):
    """
    A helper function to clean up the concatenated text from the LLM.
    It removes redundant phrases that the LLM sometimes adds.
    """
    # Remove phrases like "Typed '...' into the search input field, changing the text from '...' to '...'"
    # and keep only the final, complete text.
    match = re.search(r"to '(.*?)'", text)
    if match:
        return match.group(1)
    
    # Remove simpler prepended phrases
    text = re.sub(r"^Typed '(.*?)'", r'\1', text)
    
    return text.strip()


def process_and_consolidate_events(raw_events):
    """
    Takes the raw list of events from the LLM and consolidates consecutive
    typing events into single, meaningful blocks.
    """
    if not raw_events:
        return []

    final_events = []
    i = 0
    # A time in seconds. If the gap between typing events is larger than this,
    # start a new typing block.
    TYPING_TIME_THRESHOLD = 15.0 

    while i < len(raw_events):
        current_event = raw_events[i]

        if current_event['eventType'] == 'TYPE':
            # Start of a potential typing block
            typing_block = [current_event]
            j = i + 1
            while j < len(raw_events):
                next_event = raw_events[j]
                time_diff = next_event['timestamp'] - typing_block[-1]['timestamp']

                if next_event['eventType'] == 'TYPE' and time_diff <= TYPING_TIME_THRESHOLD:
                    typing_block.append(next_event)
                    j += 1
                else:
                    # The typing block has ended
                    break
            
            # Consolidate the typing block into a single event
            if typing_block:
                start_timestamp = typing_block[0]['timestamp']
                # Concatenate all the pieces of text
                full_text_fragments = [_clean_typed_text(event['value']) for event in typing_block]
                
                consolidated_event = {
                    'timestamp': start_timestamp,
                    'eventType': 'TYPE',
                    'value': " ".join(full_text_fragments).replace('  ', ' ').strip(),
                    # Keep the screenshot of the last typed fragment
                    'screenshot': typing_block[-1].get('screenshot') 
                }
                final_events.append(consolidated_event)
                i = j # Move the main counter past the processed block
            else:
                i += 1

        else:
            # This is not a typing event, add it directly
            final_events.append(current_event)
            i += 1
            
    return final_events
