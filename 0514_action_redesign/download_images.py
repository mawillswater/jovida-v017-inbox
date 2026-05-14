#!/usr/bin/env python3
"""Download real images via Wikipedia API (gets reliable thumb URLs)."""
import urllib.request, urllib.parse, json
from io import BytesIO
from pathlib import Path
from PIL import Image

OUT = Path(__file__).parent / 'images'
OUT.mkdir(exist_ok=True)
UA = 'JovidaPrototype/1.0 (contact@fluxvita.com)'

# (output filename, Wikipedia article title)
TARGETS = [
    ('painting-1-starry-night.jpg',  'The Starry Night'),
    ('painting-2-water-lilies.jpg',  'Water Lilies (Monet series)'),
    ('painting-3-great-wave.jpg',    'The Great Wave off Kanagawa'),
    ('news-1-nvidia.jpg',            'Nvidia'),
    ('news-2-datacenter.jpg',        'Data center'),
]


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def get_thumb(title: str, size: int = 600) -> str | None:
    params = {
        'action': 'query', 'format': 'json',
        'prop': 'pageimages', 'piprop': 'thumbnail',
        'pithumbsize': str(size), 'titles': title,
    }
    url = 'https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode(params)
    data = json.loads(fetch(url))
    for page in data.get('query', {}).get('pages', {}).values():
        thumb = page.get('thumbnail', {}).get('source')
        if thumb:
            return thumb
    return None


def process(name: str, title: str):
    print(f'→ {name} ({title})')
    try:
        thumb_url = get_thumb(title)
        if not thumb_url:
            print(f'  ✗ no thumbnail for "{title}"')
            return
        print(f'  thumb: {thumb_url}')
        data = fetch(thumb_url)
        img = Image.open(BytesIO(data)).convert('RGB')
        w, h = img.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        img = img.crop((left, top, left + side, top + side))
        img.thumbnail((512, 512), Image.LANCZOS)
        img.save(OUT / name, 'JPEG', quality=88)
        print(f'  ✓ {img.size}')
    except Exception as e:
        print(f'  ✗ {e}')


def main():
    for name, title in TARGETS:
        process(name, title)
    print('\nDone:', OUT)


if __name__ == '__main__':
    main()
