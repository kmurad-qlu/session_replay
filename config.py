import os
from dotenv import load_dotenv

load_dotenv()

# --- Project Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_INPUT_DIR = os.path.join(BASE_DIR, "video_storage")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_storage")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
os.makedirs(VIDEO_INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# --- Model Configurations ---
# Note: This model should be fine-tuned on a UI element dataset.
# Using the base 'yolov8n.pt' as a placeholder. [2, 3]
UI_DETECTION_MODEL_PATH = os.path.join(BASE_DIR, "models", "yolov8n-ui.pt") 
SPEECH_TO_TEXT_MODEL = "base"  # Options: tiny, base, small, medium, large

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")

# --- Pipeline Parameters ---
VIDEO_CHUNK_DURATION_SECONDS = 30 # Duration for video segmentation

# --- Module 1: Vision Core Parameters ---
# Cursor Tracking
CURSOR_VELOCITY_THRESHOLD_PX_PER_SEC = 5
HOVER_DURATION_MS = 500

# Scroll Detection
OPTICAL_FLOW_PYR_SCALE = 0.5
OPTICAL_FLOW_LEVELS = 3
OPTICAL_FLOW_WINSIZE = 15
OPTICAL_FLOW_ITERATIONS = 3
OPTICAL_FLOW_POLY_N = 5
OPTICAL_FLOW_POLY_SIGMA = 1.2
SCROLL_DOMINANT_FLOW_THRESHOLD = 0.75 # 75% of vectors must be in same direction

# State Change Detection
PHASH_DISTANCE_THRESHOLD = 5 # Threshold for detecting major frame changes

# --- Module 3: Synthesis Parameters ---
# Time window in seconds to correlate events during fusion
EVENT_FUSION_WINDOW_SECONDS = 1.5 
LLM_MODEL_FOR_SYNTHESIS = "gpt-4o"

# --- Module 4: Output Parameters ---
CRITICAL_FRAME_KEYWORD_TRIGGERS = ["error", "failed", "warning", "access denied"]
