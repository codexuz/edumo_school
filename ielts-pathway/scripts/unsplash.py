"""Find and download Unsplash photos for IELTS Pathway, with credits.

The access key is read from the UNSPLASH_ACCESS_KEY environment variable (never stored in the repo).

  python3 scripts/unsplash.py search "students talking" [--n 8] [--sheet out.jpg]
  python3 scripts/unsplash.py get <photo_id> <name>      -> assets/photos/<name>.jpg + assets/photos/credits.json

`get` follows the Unsplash API guidelines: it calls the photo's download_location endpoint (which counts the
download for the photographer) and stores the photographer's name and links for the credit line in the book.
"""
import io
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "assets" / "photos"
CREDITS = PHOTOS / "credits.json"
API = "https://api.unsplash.com"
UTM = "utm_source=ielts_pathway&utm_medium=referral"


def call(path, params=None):
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        sys.exit("Set UNSPLASH_ACCESS_KEY first.")
    url = path if path.startswith("http") else API + path
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Client-ID {key}", "Accept-Version": "v1"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "ielts-pathway"}), timeout=120) as r:
        return r.read()


def search(query, n=8, sheet=None):
    d = call("/search/photos", {"query": query, "per_page": n, "orientation": "landscape", "content_filter": "high"})
    thumbs = []
    for i, p in enumerate(d["results"]):
        print(f'{i}  {p["id"]}  {p["width"]}x{p["height"]}  {p["user"]["name"]}  | {p.get("alt_description") or ""}')
        thumbs.append(p["urls"]["thumb"])
    if sheet and thumbs:
        from PIL import Image, ImageDraw
        ims = [Image.open(io.BytesIO(fetch(t))).convert("RGB") for t in thumbs]
        w = 200
        ims = [im.resize((w, int(im.height * w / im.width))) for im in ims]
        h = max(im.height for im in ims)
        cols = 4
        rows = (len(ims) + cols - 1) // cols
        out = Image.new("RGB", (cols * (w + 6), rows * (h + 22)), "white")
        dr = ImageDraw.Draw(out)
        for i, im in enumerate(ims):
            x, y = (i % cols) * (w + 6), (i // cols) * (h + 22)
            out.paste(im, (x, y + 20))
            dr.text((x + 2, y + 4), str(i), fill="black")
        out.save(sheet)


def get(pid, name):
    p = call(f"/photos/{pid}")
    call(p["links"]["download_location"])          # required by the API guidelines: register the download
    raw = p["urls"]["raw"]
    img = fetch(raw + ("&" if "?" in raw else "?") + "w=1800&q=80&fm=jpg&fit=max")
    PHOTOS.mkdir(parents=True, exist_ok=True)
    (PHOTOS / f"{name}.jpg").write_bytes(img)
    credits = json.loads(CREDITS.read_text(encoding="utf-8")) if CREDITS.exists() else {}
    credits[name] = {"id": pid, "photographer": p["user"]["name"],
                     "profile": f'{p["user"]["links"]["html"]}?{UTM}', "photo": f'{p["links"]["html"]}?{UTM}',
                     "alt": p.get("alt_description") or ""}
    CREDITS.write_text(json.dumps(credits, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f'{name}.jpg  {len(img) // 1024} KB  Photo: {p["user"]["name"]} / Unsplash')


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "search":
        n = int(a[a.index("--n") + 1]) if "--n" in a else 8
        sheet = a[a.index("--sheet") + 1] if "--sheet" in a else None
        search(a[1], n, sheet)
    elif a and a[0] == "get" and len(a) == 3:
        get(a[1], a[2])
    else:
        sys.exit(__doc__)
