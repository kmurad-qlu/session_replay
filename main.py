import argparse
import os
import time
import shutil
import json

from video_processor import preprocess_video
from llm_analyzer import analyze_frames_with_llm
from event_processor import process_and_consolidate_events
from audio_transcriber import transcribe_audio_file
from report_generator import generate_step_by_step_report
from nl_generation import generate_narrative
from output_formatter import format_and_save_output

def main(args):
    start_time = time.time()
    print("Starting Project SessionReplay analysis...")

    # Setup output directory
    video_name = os.path.splitext(os.path.basename(args.video))[0]
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("output", f"{video_name}_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created output directory: {output_dir}\n")

    # --- Stage 1: Pre-processing ---
    print("--- Stage 1: Pre-processing Video ---")
    frame_dir, audio_path, total_frames, sampled_frame_files = preprocess_video(args.video, output_dir)
    print("Video pre-processing complete.\n")
    
    # --- Stage 2: Visual Analysis ---
    print("--- Stage 2: Analyzing Frames with Multimodal LLM ---")
    raw_events = []
    SECONDS_PER_SAMPLE = 2
    for i in range(len(sampled_frame_files) - 1):
        prev_frame = sampled_frame_files[i]
        current_frame = sampled_frame_files[i+1]
        print(f"  -> Analyzing frames {i} and {i+1}...")
        result = analyze_frames_with_llm(prev_frame, current_frame)
        if result and result.get('action') != 'NONE':
            current_timestamp = (i + 1) * SECONDS_PER_SAMPLE
            raw_events.append({
                'timestamp': current_timestamp,
                'eventType': result.get('action', 'UNKNOWN').upper(),
                'value': result.get('target', 'No detail')
            })
    print(f"LLM analysis complete. Found {len(raw_events)} raw events.\n")

    # --- Stage 3: Event Consolidation ---
    print("--- Stage 3: Consolidating Events ---")
    final_events = process_and_consolidate_events(raw_events)
    print(f"Consolidated into {len(final_events)} final events.\n")

    # --- Stage 4: Audio Transcription ---
    print("--- Stage 4: Transcribing Audio ---")
    # The function now handles saving the file internally
    transcription = transcribe_audio_file(audio_path, output_dir)
    print("Audio transcription complete.\n")

    # --- Stage 5: Final Output Formatting ---
    print("--- Stage 5: Formatting Final JSON Logs ---")
    final_events_with_narrative = generate_narrative(final_events)
    format_and_save_output(raw_events, final_events_with_narrative, output_dir, sampled_frame_files)
    print("JSON logs and screenshots saved.\n")
    
    # --- Stage 6: Step-by-Step Report Generation ---
    print("--- Stage 6: Generating Final Report ---")
    generate_step_by_step_report(final_events_with_narrative, transcription, output_dir)
    print("Report generation complete.\n")

    # --- Cleanup ---
    if not args.keep_temp_files:
        shutil.rmtree(os.path.join(output_dir, "temp"))
        print("Temporary files cleaned up.")
    else:
        print("Temporary files kept for debugging purposes.")

    end_time = time.time()
    print(f"Analysis complete in {end_time - start_time:.2f} seconds.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze a screen recording to generate a session log.")
    parser.add_argument("--video", required=True, help="Path to the video file to analyze.")
    parser.add_argument("--keep-temp-files", action='store_true', help="Keep temporary frames and audio for debugging.")
    args = parser.parse_args()
    main(args)

