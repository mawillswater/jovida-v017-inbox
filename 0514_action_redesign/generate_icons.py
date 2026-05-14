#!/usr/bin/env python3
"""Generate 6 Jovida action icons using Gemini 2.5 Flash Image (Nano Banana)."""
import os
import time
from io import BytesIO
from pathlib import Path
from google import genai
from google.genai import types
from PIL import Image

os.environ.setdefault('GEMINI_API_KEY', 'AIzaSyAYRAL3HnnpAqs4PLAGQwK3I1lvtttAb7c')
client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

OUT_DIR = Path(__file__).parent / 'icons'
OUT_DIR.mkdir(exist_ok=True)

PROMPT_TEMPLATE = (
    "A premium 3D isometric icon of {subject}, minimalist style. "
    "High-fidelity textures with a soft, matte tactile feel. Smooth rounded geometry. "
    "Diffused studio lighting, soft shadows, pure white background. "
    "High-end product photography style, 8k resolution, C4D render."
)

ICONS = [
    ("icon-1-painting",   "a small framed classical oil painting"),
    ("icon-2-tweet",      "a small blue bird perched on a glowing microchip"),
    ("icon-3-reply",      "three small overlapping speech bubbles"),
    ("icon-4-sleep-book", "a small open book with a tiny crescent moon resting on it"),
    ("icon-5-lamp-off",   "a switched-off bedside lamp"),
    ("icon-6-server",     "a small server tower next to a rising bar chart"),
]


def generate(name: str, subject: str):
    prompt = PROMPT_TEMPLATE.format(subject=subject)
    print(f'→ {name}: {subject[:50]}...')
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=['IMAGE'],
            image_config=types.ImageConfig(aspect_ratio="1:1")
        )
    )
    if not response.candidates:
        print(f'  ✗ No candidates returned')
        return False
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            img = Image.open(BytesIO(part.inline_data.data))
            out_path = OUT_DIR / f'{name}.png'
            img.save(out_path)
            print(f'  ✓ {out_path.name} {img.size}')
            return True
    print(f'  ✗ No inline_data found')
    return False


def main():
    for i, (name, subject) in enumerate(ICONS):
        for attempt in range(3):
            try:
                if generate(name, subject):
                    break
            except Exception as e:
                print(f'  ! Attempt {attempt + 1} failed: {e}')
                if '429' in str(e):
                    time.sleep(10)
                else:
                    time.sleep(3)
        if i < len(ICONS) - 1:
            time.sleep(2)
    print('\nAll done. Icons saved to:', OUT_DIR)


if __name__ == '__main__':
    main()
