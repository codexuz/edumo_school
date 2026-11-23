"""Collect the SVG icons used by the book into data/icons.json (so the build needs no icon packages).

Usage: python3 scripts/icons.py <node_modules/@iconify-json dir>
Icons come from open Iconify sets: Material Design Icons (Apache-2.0), Game-icons.net (CC BY 3.0),
Healthicons (MIT), Hugeicons (MIT). A few simple icons are drawn here (CUSTOM).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ["mdi:cards-outline", "mdi:link-variant", "mdi:alphabetical-variant", "mdi:help-circle", "mdi:pencil", "mdi:lightning-bolt",
          "mdi:chat", "mdi:magnify", "mdi:account-edit", "mdi:star", "mdi:book-alphabet", "mdi:lightbulb-on", "mdi:puzzle",
          "mdi:map-marker-path", "mdi:key-variant", "mdi:format-list-bulleted", "mdi:account-voice", "mdi:trophy"]
CUSTOM = {
    "custom:onion": {"w": 24, "h": 24, "body":
        '<path fill="currentColor" d="M12 2.5c-.4 1.6-1 2.7-2.2 3.5C6.6 7.9 5 10.4 5 13.6 5 17.7 8.1 21 12 21s7-3.3 7-7.4c0-3.2-1.6-5.7-4.8-7.6C13 5.2 12.4 4.1 12 2.5z"/>'
        '<path fill="none" stroke="#fff" stroke-width="1" opacity=".75" d="M12 8c-2.2 2-2.8 5.6-2 10M12 8c2.2 2 2.8 5.6 2 10M12 8v12"/>'
        '<path fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" d="M10.5 21.2l-.6 1.4M12 21.3v1.5M13.5 21.2l.6 1.4"/>'},
    "custom:mango": {"w": 24, "h": 24, "body":
        '<path fill="currentColor" d="M6.6 6.4c3.6-2.7 9.4-1.7 11.6 2.6 2.2 4.2.4 10.4-4.3 12.2-4.7 1.9-9.6-.6-10.1-5.2-.4-3.7.3-7.6 2.8-9.6z"/>'
        '<path fill="currentColor" opacity=".55" d="M12.2 5.6c1-1.9 3.2-2.9 5.4-2.4-.8 1.8-2.8 2.9-5.4 2.4z"/>'
        '<path fill="none" stroke="#fff" stroke-width="1.2" stroke-linecap="round" opacity=".7" d="M8 10.5c.6-1.4 1.8-2.3 3.2-2.6"/>'},
    "custom:wristband": {"w": 24, "h": 24, "body":
        '<ellipse cx="12" cy="13" rx="9" ry="5.2" fill="none" stroke="currentColor" stroke-width="3.6"/>'
        '<path fill="none" stroke="currentColor" stroke-width="3.6" d="M3 11c0-2.9 4-5.2 9-5.2s9 2.3 9 5.2"/>'
        '<circle cx="12" cy="18.2" r="1.1" fill="#fff"/><circle cx="8" cy="17.4" r="1.1" fill="#fff"/><circle cx="16" cy="17.4" r="1.1" fill="#fff"/>'},
    "custom:shy": {"w": 24, "h": 24, "body":
        '<circle cx="12" cy="12" r="10" fill="currentColor"/>'
        '<ellipse cx="7.2" cy="13.6" rx="2" ry="1.2" fill="#fff" opacity=".55"/><ellipse cx="16.8" cy="13.6" rx="2" ry="1.2" fill="#fff" opacity=".55"/>'
        '<path fill="none" stroke="#fff" stroke-width="1.5" stroke-linecap="round" d="M7.4 10.2q1.4-1.2 2.8 0M13.8 10.2q1.4-1.2 2.8 0M10.2 16.2q1.8 1 3.6 0"/>'},
}


def main(src):
    src = Path(src)
    need = set(STATIC)
    for f in (ROOT / "data" / "units").glob("*.json"):
        u = json.loads(f.read_text(encoding="utf-8"))
        need.add(u["icon"])
        need.update(w[2] for w in u["words"])
    sets, out, missing = {}, {}, []
    for ident in sorted(need):
        if ident in CUSTOM:
            out[ident] = CUSTOM[ident]
            continue
        prefix, name = ident.split(":")
        if prefix not in sets:
            sets[prefix] = json.loads((src / prefix / "icons.json").read_text(encoding="utf-8"))
        s = sets[prefix]
        name = s.get("aliases", {}).get(name, {}).get("parent", name)
        icon = s["icons"].get(name)
        if not icon:
            missing.append(ident)
            continue
        out[ident] = {"w": icon.get("width", s.get("width", 24)), "h": icon.get("height", s.get("height", 24)), "body": icon["body"]}
    (ROOT / "data" / "icons.json").write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print("icons:", len(out), "missing:", missing)


if __name__ == "__main__":
    main(sys.argv[1])
