"""Quick test for get_openai_analysis() using output_image.jpg."""

import sys
import json
import cv2
from analyze_with_openai_api import get_openai_analysis

IMAGE_PATH = "output_image.jpg"


def main():
    img = cv2.imread(IMAGE_PATH)
    if img is None:
        print(f"Error: could not read {IMAGE_PATH}")
        sys.exit(1)

    print(f"Loaded {IMAGE_PATH}  ({img.shape[1]}x{img.shape[0]})")
    print("Calling OpenAI Responses API with web search …")

    with open(IMAGE_PATH, "rb") as f:
        image_bytes = f.read()

    result = get_openai_analysis(
        img,
        image_path=IMAGE_PATH,
        image_bytes=image_bytes,
    )

    if result is None:
        print("Analysis returned None – check API key / errors above.")
        sys.exit(1)

    print("\n--- Result ---")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
