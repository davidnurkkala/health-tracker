"""Generate Cadence's app icons.

No image libraries in this environment, so this rasterises the mark directly:
signed-distance fields, 4x4 supersampled, written out as PNG with zlib.
Re-run it if the mark or the palette ever changes; the PNGs are committed.
"""
import math, struct, zlib, os

INK   = (0x13, 0x1a, 0x21)
EDGE  = (0x2a, 0x36, 0x41)
BRASS = (0xd3, 0xa2, 0x4c)

SS = 4                 # supersampling factor per axis
ARC = 0.66             # fraction of the dial that has refilled

def blend(dst, src, a):
    return tuple(round(d + (s - d) * a) for d, s in zip(dst, src))

def rrect_sdf(px, py, cx, cy, hw, hh, r):
    """Negative inside a rounded rectangle."""
    qx = abs(px - cx) - (hw - r)
    qy = abs(py - cy) - (hh - r)
    ax, ay = max(qx, 0.0), max(qy, 0.0)
    return math.hypot(ax, ay) + min(max(qx, qy), 0.0) - r

def dial_coverage(px, py, cx, cy, radius, thick, cap_r):
    """Distance-to-shape for the arc track and the refilled arc.

    Returns (on_track, on_arc) as booleans for one sample point.
    """
    dx, dy = px - cx, py - cy
    d = math.hypot(dx, dy)
    on_track = abs(d - radius) <= thick / 2.0

    # angle measured clockwise from 12 o'clock, in [0, 1)
    ang = math.atan2(dx, -dy) / (2 * math.pi)
    if ang < 0:
        ang += 1.0
    on_arc = on_track and ang <= ARC

    # round caps at both ends of the arc
    if not on_arc:
        for t in (0.0, ARC):
            a = t * 2 * math.pi
            ex = cx + math.sin(a) * radius
            ey = cy - math.cos(a) * radius
            if math.hypot(px - ex, py - ey) <= cap_r:
                on_arc = True
                break
    return on_track, on_arc

def render(size, maskable):
    # maskable icons are full-bleed; the mark shrinks into the 80% safe zone
    scale = 0.52 if maskable else 0.68
    cx = cy = size / 2.0
    radius = size * scale / 2.0
    thick = max(2.0, size * scale * 0.145)
    cap_r = thick / 2.0
    dot_r = size * scale * 0.105
    corner = size * 0.22          # rounded-square plate for the "any" icon
    plate_half = size * 0.5 if maskable else size * 0.5

    rows = []
    inv = 1.0 / (SS * SS)
    for y in range(size):
        row = bytearray()
        for x in range(size):
            plate = track = arc = dot = 0
            for sy in range(SS):
                py = y + (sy + 0.5) / SS
                for sx in range(SS):
                    px = x + (sx + 0.5) / SS
                    if maskable:
                        plate += 1
                    elif rrect_sdf(px, py, cx, cy, plate_half, plate_half, corner) <= 0:
                        plate += 1
                    on_track, on_arc = dial_coverage(px, py, cx, cy, radius, thick, cap_r)
                    if on_track:
                        track += 1
                    if on_arc:
                        arc += 1
                    if math.hypot(px - cx, py - cy) <= dot_r:
                        dot += 1
            c = (0, 0, 0)
            a = plate * inv
            c = blend(c, INK, a)
            c = blend(c, EDGE, track * inv)
            c = blend(c, BRASS, arc * inv)
            c = blend(c, BRASS, dot * inv)
            row += bytes(c) + bytes([round(255 * max(a, track * inv, arc * inv, dot * inv))])
        rows.append(bytes(row))
    return rows

def write_png(path, size, rows):
    raw = b"".join(b"\x00" + r for r in rows)
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons")
for size, maskable, name in [
    (192, False, "icon-192.png"),
    (512, False, "icon-512.png"),
    (192, True,  "maskable-192.png"),
    (512, True,  "maskable-512.png"),
    (180, False, "apple-touch-icon.png"),
]:
    write_png(os.path.join(out, name), size, render(size, maskable))
    print(name, "ok")
