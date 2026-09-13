"""One-time outline extraction from the approved Briosa concept; not a font."""
from pathlib import Path
import json
import sys
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
import potrace

REFERENCE = Path(sys.argv[1])
crop = (124, 453, 701, 602)
pixels = np.asarray(Image.open(REFERENCE).convert('RGB').crop(crop))
mask = pixels.min(axis=2) > 175
yy, xx = np.where(mask)
bounds = (int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1)
mask = mask[bounds[1]:bounds[3], bounds[0]:bounds[2]]
height, width = mask.shape
paths = potrace.Bitmap(~mask).trace(turdsize=8, alphamax=1.1, opttolerance=0.15)

def point(p):
    return f'{p.x:.3f},{p.y:.3f}'

outline = []
for curve in paths:
    parts = ['M' + point(curve.start_point)]
    for segment in curve:
        if segment.is_corner:
            parts += ['L' + point(segment.c), 'L' + point(segment.end_point)]
        else:
            parts += ['C' + ' '.join(point(p) for p in (segment.c1, segment.c2, segment.end_point))]
    outline.append(' '.join(parts) + ' Z')

data = {
    'description': 'Custom Briosa wordmark, outlined from the user-selected ImageGen concept.',
    'source_image': 'approved-concept.png',
    'source_crop': list(crop),
    'mask_bounds_within_crop': list(bounds),
    'width': width,
    'height': height,
    'path': ' '.join(outline),
    'contours': len(paths),
    'segments': sum(len(p) for p in paths),
    'trace': {'engine': 'potracer 0.0.4', 'threshold': 175, 'alphamax': 1.1, 'opttolerance': 0.15},
}
(ROOT / 'source' / 'wordmark.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
Image.fromarray(np.where(mask, 0, 255).astype('uint8')).save(ROOT / 'source' / 'wordmark-mask.png')
print(json.dumps({k:v for k,v in data.items() if k != 'path'}, indent=2))
