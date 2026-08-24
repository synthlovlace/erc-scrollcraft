"""Generate hero images for ERC ScrollCraft build using Gemini API."""
import os, sys, time
from pathlib import Path

# Load API key from Starpath .env
env_path = Path("C:/Users/zacen/Starpath/.env")
api_key = None
for line in env_path.read_text().splitlines():
    if line.startswith("GEMINI_API_KEY="):
        api_key = line.split("=", 1)[1].strip().strip('"')
        break

if not api_key:
    print("ERROR: No GEMINI_API_KEY found in Starpath .env")
    sys.exit(1)

from google import genai
from google.genai import types

client = genai.Client(api_key=api_key)
MODEL = "gemini-3.1-flash-image-preview"

OUT_DIR = Path("C:/Users/zacen/engler-retail-construction/scrollcraft/builds/erc/out")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Style preamble — reused VERBATIM in every prompt
PREAMBLE = """Cinematic construction photography shot on 35mm anamorphic lenses. Shallow depth of field, high dynamic range, true blacks, matte film grain. Low-key lighting: one warm tungsten key from overhead work lights, cool ambient fill from daylight through unfinished windows, deep falloff into shadow. Colour grade of deep charcoal, warm amber highlights from construction lighting, desaturated mid-tones. Photographic realism. NOT 3D render, NOT clay, NOT illustration, NOT CGI, no digital glow, no plastic sheen."""

IMAGES = {
    "01-blueprints": f"""{PREAMBLE}

Architectural construction blueprints spread across a dark steel work table in a commercial construction office. Detailed floor plans for a retail store build-out, blue and white line drawings with dimension annotations, rolled drawings in the background. A yellow hard hat and steel ruler rest on the plans. Large empty shadowed space across the upper third of the frame for text overlay. The paper glows warm under a single desk lamp. Sharp focus on the nearest plan, background falling to bokeh.""",

    "02-materials": f"""{PREAMBLE}

Interior of a commercial construction site receiving materials delivery. Steel studs bundled and stacked on raw concrete floor, lumber sorted by size against an unfinished wall, boxes of electrical conduit and copper pipe, pallets of drywall. Industrial scale, a cavernous retail space shell with exposed ceiling joists and temporary work lighting casting long shadows. Subject low in the frame, large empty shadowed space above and to the left for text overlay. The sheer volume of materials conveys the scale of what is coming.""",

    "03-framing": f"""{PREAMBLE}

Active commercial retail construction site mid-build. Steel stud framing going up in a large open retail space, a worker in the mid-ground positioning a metal stud with a screw gun, sparks from a chop saw in the background catching the light. Electrical conduit roughed in along the ceiling. Dust particles visible in the warm work light beams. Construction grit and energy. Subject centered, large empty shadowed space to the right of frame for text overlay. The physical reality of building.""",

    "04-electrical": f"""{PREAMBLE}

Close-up of skilled electrical rough-in work inside a commercial retail construction site. Gloved hands pulling copper wire through steel conduit, junction boxes mounted on metal studs, color-coded wiring organized and bundled. The precision of the trade visible in every connection. Warm work light from above, cool daylight through plastic-sheeted windows behind. Shallow depth of field with razor-sharp focus on the hands and wire. Large empty space in the upper left for text overlay.""",

    "05-drywall": f"""{PREAMBLE}

Commercial retail space with fresh drywall installation in progress. Smooth white surfaces where raw framing used to be, the transformation halfway complete. Some walls taped and mudded, others still showing seams. A worker on stilts applying joint compound overhead. The space beginning to take its final shape, doorways and display alcoves now visible in the architecture. Warm construction lighting mixed with newly installed recessed can lights being tested. Large empty shadowed space across the lower third for text overlay.""",

    "06-finished": f"""{PREAMBLE}

Completed modern retail store interior, freshly built and ready for business. Polished concrete floors reflecting recessed LED lighting, clean white walls with architectural display niches, glass storefront entrance visible in the background. Sleek minimal fixtures, perfectly finished ceiling grid with integrated lighting. The same space that was raw concrete and steel studs, now transformed into a premium retail environment. Warm inviting lighting, cool clean surfaces. The subject fills the lower two-thirds, large empty space in the upper portion for text overlay. The reveal moment — construction is complete.""",
}

success = 0
fail = 0

for name, prompt in IMAGES.items():
    out_path = OUT_DIR / f"{name}.png"
    if out_path.exists() and out_path.stat().st_size > 10000:
        print(f"[SKIP] {name} — already exists ({out_path.stat().st_size // 1024}KB)")
        success += 1
        continue

    print(f"[GEN] {name} — generating...")
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["image", "text"],
            ),
        )
        # Extract image from response
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                out_path.write_bytes(part.inline_data.data)
                print(f"  [OK] {name} — {out_path.stat().st_size // 1024}KB")
                success += 1
                break
        else:
            print(f"  [FAIL] {name} — no image in response")
            if response.candidates[0].content.parts:
                for p in response.candidates[0].content.parts:
                    if hasattr(p, 'text') and p.text:
                        print(f"    Text: {p.text[:200]}")
            fail += 1
    except Exception as e:
        print(f"  [FAIL] {name} — {e}")
        fail += 1

    time.sleep(2)  # rate limit courtesy

print(f"\nDone: {success} OK, {fail} failed")
