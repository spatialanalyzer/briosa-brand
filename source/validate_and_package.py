"""Check vector/raster integrity, create ICO and proof images, and package assets."""
from pathlib import Path
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from collections import deque
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
WORDMARK = json.loads((ROOT/'source/wordmark.json').read_text(encoding='utf-8'))
TAGLINE = MANIFEST['tagline']
PALETTE = MANIFEST['palette']
ALLOWED = set(PALETTE.values()) | {'#000000'}
VERSION = (ROOT/'VERSION').read_text(encoding='utf-8').strip()
NS = '{http://www.w3.org/2000/svg}'
failures=[]
results=[]

def check(test, message):
    results.append({'passed':bool(test),'check':message})
    if not test:
        failures.append(message)

check(re.fullmatch(r'v[1-9][0-9]*(?:\.[0-9]+)*', VERSION) is not None, 'Brand version is a valid release tag')
check(MANIFEST.get('version') == VERSION, 'Manifest version matches VERSION')

for item in MANIFEST['assets']:
    file=ROOT/item['file']
    xml=file.read_text(encoding='utf-8')
    root=ET.fromstring(xml)
    nodes=list(root.iter())
    tags={element.tag.removeprefix(NS) for element in nodes}
    check(tags <= {'svg','title','desc','g','path','rect','circle'}, f'{item["file"]}: vector-only content')
    check(root.find(NS+'title') is not None and root.find(NS+'desc') is not None, f'{item["file"]}: accessible title and description')
    check(not re.search(r'(?:href=|url\(|data:image|<text\b|<image\b|<script\b|<style\b|font-family)',xml), f'{item["file"]}: no external image, script, style or font dependency')
    ids=[node.attrib['id'] for node in nodes if 'id' in node.attrib]
    check(len(ids)==len(set(ids)), f'{item["file"]}: unique IDs')
    fills={node.attrib['fill'] for node in nodes if 'fill' in node.attrib}
    check(fills <= ALLOWED, f'{item["file"]}: exact approved colors')
    check(not any('stroke' in node.attrib for node in nodes), f'{item["file"]}: filled outlines, no strokes to rescale')
    translucent=[node for node in nodes if {'opacity','fill-opacity'} & set(node.attrib)]
    check(all(node.get('data-part')=='glow' for node in translucent), f'{item["file"]}: only the glow is translucent')
    check(not translucent or item['theme'] in ('color','inverse'), f'{item["file"]}: one-color artwork has no glow')
    check('data-plane' not in xml and 'Precision, connected.' not in xml, f'{item["file"]}: v1 artwork and superseded slogan absent')
    if item['tagline']:
        check(TAGLINE in root.find(NS+'desc').text, f'{item["file"]}: selected slogan recorded')
    if item['kind'] not in ('master','icon'):
        png=ROOT/'png'/Path(item['file']).with_suffix('.png')
        im=Image.open(png).convert('RGBA')
        alpha=np.asarray(im)[:,:,3]
        yy,xx=np.where(alpha>127)
        check(len(xx)>0 and xx.min()>0 and yy.min()>0 and xx.max()<im.width-1 and yy.max()<im.height-1,
              f'{png.relative_to(ROOT)}: artwork visible, unclipped and padded')
        check(alpha.min()==0, f'{png.relative_to(ROOT)}: transparent background retained')

sizes=[16,32,48,64,128,256]
frames={s:Image.open(ROOT/f'icons/briosa-icon-{s}.png').convert('RGBA') for s in sizes}
frames[256].save(ROOT/'icons/favicon.ico',format='ICO',sizes=[(s,s) for s in sizes],append_images=[frames[s] for s in sizes if s!=256])
ico=Image.open(ROOT/'icons/favicon.ico')
check(ico.ico.sizes()=={(s,s) for s in sizes},'ICO includes 16, 32, 48, 64, 128 and 256 px frames')
check(np.array_equal(np.asarray(ico.ico.getimage((16,16))),np.asarray(frames[16])),'ICO preserves the dedicated favicon 16 px frame')

# The outlines must match the font's own rendering: draw the same letters with
# FreeType at the same instance, size and pen positions, then compare silhouettes.
# FreeType draws at 4x and is reduced, so pixel-grid hinting does not shift edges.
outline_svg=(ROOT/'qa/wordmark-outline.svg').read_text(encoding='utf-8')
tx,ty,scale=map(float,re.search(r'translate\(([-\d.]+) ([-\d.]+)\) scale\(([-\d.]+)\)',outline_svg).groups())
outline=Image.open(ROOT/'qa/wordmark-outline.png').convert('RGBA')
saira=ROOT/WORDMARK['font']['file']
order=[axis.axisTag for axis in TTFont(saira)['fvar'].axes]
up=4
font=ImageFont.truetype(str(saira),WORDMARK['qa_em']*up)
font.set_variation_by_axes([WORDMARK['font']['axes'][tag] for tag in order])
reference=Image.new('L',(outline.width*up,outline.height*up),0)
draw=ImageDraw.Draw(reference)
for letter,pen in zip(WORDMARK['text'],WORDMARK['pen_positions']):
    draw.text(((tx+pen*scale)*up,ty*up),letter,font=font,fill=255,anchor='ls')
reference=reference.resize(outline.size,Image.Resampling.BOX)
ours=np.asarray(outline)[:,:,3]>127
theirs=np.asarray(reference)>127
iou=float(np.logical_and(ours,theirs).sum()/np.logical_or(ours,theirs).sum())
check(iou>0.98,'Outlined wordmark matches FreeType\'s Saira rendering with over 98% silhouette overlap')

def components(mask):
    seen=np.zeros_like(mask,dtype=bool)
    areas=[]
    for y,x in zip(*np.where(mask)):
        if seen[y,x]: continue
        queue=deque([(int(y),int(x))]);seen[y,x]=True;area=0
        while queue:
            py,px=queue.popleft();area+=1
            for dy,dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                yy,xx=py+dy,px+dx
                if 0<=yy<mask.shape[0] and 0<=xx<mask.shape[1] and mask[yy,xx] and not seen[yy,xx]:
                    seen[yy,xx]=True;queue.append((yy,xx))
        areas.append(area)
    return len(areas),areas

def touches(a,b):
    grown=a.copy()
    grown[1:]|=a[:-1];grown[:-1]|=a[1:];grown[:,1:]|=a[:,:-1];grown[:,:-1]|=a[:,1:]
    return bool((grown&b).any())

icon_results=[]
for size in [16,24,32,48,64,128]:
    arr=np.asarray(Image.open(ROOT/f'icons/briosa-icon-{size}.png').convert('RGB')).astype(int)
    r,g,b=arr[:,:,0],arr[:,:,1],arr[:,:,2]
    # Solid cores only: cyan jaw, near-white beam, pale cyan point. Edges blend into void.
    jaw=(r<90)&(g>110)&(b>170)
    beam=(r>180)&(g>190)&(b>200)
    point=(r>100)&(r<180)&(g>200)&(b>230)
    jaw_count,jaw_areas=components(jaw)
    beam_count,beam_areas=components(beam)
    separate=not touches(jaw,beam)
    icon_results.append({'size':size,'jaw_components':jaw_count,'beam_components':beam_count,
                         'jaw_pixels':int(jaw.sum()),'beam_pixels':int(beam.sum()),'point_pixels':int(point.sum()),
                         'jaw_and_beam_separate':separate})
    check(jaw_count==1 and beam_count==1,f'{size} px icon: one solid jaw and one solid beam')
    check(separate,f'{size} px icon: jaw stays clear of the beam')
    if size>=24:
        check(point.sum()>0,f'{size} px icon: measured point visible')

def luminance(color):
    channel=[int(color[i:i+2],16)/255 for i in (1,3,5)]
    linear=[c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4 for c in channel]
    return 0.2126*linear[0]+0.7152*linear[1]+0.0722*linear[2]

def contrast(a,b):
    la,lb=sorted((luminance(a),luminance(b)),reverse=True)
    return (la+0.05)/(lb+0.05)

pairs=[('dark-ink','void',7),('dark-ink-2','void',4.5),('dark-ink-3','void',4.5),('dark-jaw','void',3),
       ('light-ink','clean-room',7),('light-ink-2','clean-room',4.5),('light-ink-3','clean-room',4.5),('light-link','clean-room',4.5),
       ('light-jaw','clean-room',3)]
contrast_results=[]
for fg,bg,minimum in pairs:
    ratio=contrast(PALETTE[fg],PALETTE[bg])
    contrast_results.append({'foreground':fg,'background':bg,'ratio':round(ratio,2),'minimum':minimum})
    check(ratio>=minimum,f'{fg} on {bg}: contrast {ratio:.2f}:1 meets {minimum}:1')

# Proof: FreeType's Saira, the SVG outline, and where they differ.
label=ImageFont.truetype(str(ROOT/'fonts/Inter-Variable.ttf'),22)
w,h=outline.size
proof=Image.new('RGB',(w+72,3*h+260),PALETTE['clean-room'])
pd=ImageDraw.Draw(proof)
ink=tuple(int(PALETTE['light-ink'][i:i+2],16) for i in (1,3,5))
for row,(title,mask) in enumerate([('SAIRA 600 · WDTH 125, RENDERED BY FREETYPE',theirs),('SVG OUTLINE',ours)]):
    y=36+row*(h+72)
    pd.text((36,y),title,font=label,fill=PALETTE['light-ink-3'])
    proof.paste(Image.new('RGB',(w,h),ink),(36,y+36),Image.fromarray((mask*255).astype('uint8')))
y=36+2*(h+72)
pd.text((36,y),f'DIFFERENCE · {iou:.2%} OVERLAP',font=label,fill=PALETTE['light-ink-3'])
diff=np.zeros((h,w,3),dtype='uint8')+np.array([int(PALETTE['clean-room'][i:i+2],16) for i in (1,3,5)],dtype='uint8')
diff[ours&theirs]=(214,226,238)
diff[ours&~theirs]=(222,47,85)
diff[theirs&~ours]=(46,71,217)
proof.paste(Image.fromarray(diff),(36,y+36))
proof.save(ROOT/'qa/wordmark-outline-comparison.png')

report={
    'version':VERSION,
    'status':'passed' if not failures else 'failed',
    'svg_assets':len(MANIFEST['assets']),
    'checks_passed':sum(r['passed'] for r in results),
    'checks_total':len(results),
    'wordmark_silhouette_iou':iou,
    'icon_legibility':icon_results,
    'contrast':contrast_results,
    'failures':failures,
    'checks':results,
}
(ROOT/'qa/validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
contrast_lines='\n'.join(f'| `{c["foreground"]}` | `{c["background"]}` | {c["ratio"]:.2f}:1 | {c["minimum"]}:1 |' for c in contrast_results)
summary=f'''# Asset Validation

Status: **{report['status']}**. {report['checks_passed']} of {report['checks_total']} automated checks passed.

Brand version: **{VERSION}**.

- {report['svg_assets']} deliverable SVG assets were parsed and checked for vector-only content, approved solid colors, filled outlines without strokes, accessible titles/descriptions, unique IDs, and absence of external images, scripts, styles and font dependencies. Only the large cut's glow is translucent, and one-color artwork has none. No v1 plane artwork remains.
- Every exported logo, symbol and suite PNG was checked for visibility, transparent background, and unclipped artwork with safety padding.
- The outlined wordmark achieved **{iou:.2%} silhouette overlap** with FreeType's own rendering of Saira at wght 600 and wdth 125, at the same size and letter positions, supersampled to avoid hinting. This checks the outlines against the font, not the design.
- Icons at 16, 24, 32, 48, 64 and 128 px each show one solid jaw, clear of one solid beam. The measured point reaches its full color from 24 px; at 16 px it antialiases to a softer two-pixel dot, as the proof shows.
- The ICO contains six frames and preserves the favicon's 16 px frame.
- Exact slogan: **{TAGLINE}**

## Contrast

WCAG 2 contrast of the palette's text and accent colors on their grounds.

| Foreground | Background | Ratio | Required |
| --- | --- | --- | --- |
{contrast_lines}

## Visual Proofs

![Saira rendering versus the SVG outline](wordmark-outline-comparison.png)

![Color, inverse, black, white and small-size variants](variant-and-size-proof.png)

The generated preview and these proofs must also be visually inspected after a rebuild. Automated checks alone do not establish visual quality.

Detailed results: [validation.json](validation.json).
'''
(ROOT/'qa/VALIDATION.md').write_text(summary,encoding='utf-8',newline='\n')
if failures:
    print(json.dumps({k:v for k,v in report.items() if k != 'checks'},indent=2))
    raise SystemExit('Asset checks failed; ZIP was not created.')

def packaged_files():
    # Explicit paths keep Git metadata, dependencies and local files out of releases.
    names = [
        'README.md', 'BRAND-GUIDE.md', 'LICENSE', 'THIRD-PARTY-NOTICES.md',
        'VERSION', 'colors.css', 'colors.json', 'manifest.json',
        'preview.svg', 'preview.png',
    ]
    files = [ROOT/name for name in names]
    patterns = {
        'logos': ['*.svg'], 'marks': ['*.svg'], 'suite': ['*.svg'],
        'icons': ['*.svg', '*.png', '*.ico'],
        'fonts': ['*.ttf', '*.txt'],
        'source': ['*.py', '*.cjs', '*.json', '*.txt', '*.md', '*.svg'],
        'qa': ['*.md', '*.json', '*.svg', '*.png'],
        'png/logos': ['*.png'], 'png/marks': ['*.png'], 'png/suite': ['*.png'],
    }
    for directory, globs in patterns.items():
        for pattern in globs:
            files.extend((ROOT/directory).glob(pattern))
    return sorted(set(files))

checksums=[]
for file in packaged_files():
    checksums.append(hashlib.sha256(file.read_bytes()).hexdigest()+'  '+file.relative_to(ROOT).as_posix())
(ROOT/'SHA256SUMS.txt').write_text('\n'.join(checksums)+'\n',encoding='utf-8',newline='\n')
dist=ROOT/'dist'
dist.mkdir(exist_ok=True)
package_name='briosa-brand-'+VERSION
archive=dist/(package_name+'.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for file in [*packaged_files(), ROOT/'SHA256SUMS.txt']:
        z.write(file,package_name+'/'+file.relative_to(ROOT).as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
(dist/(archive.name+'.sha256')).write_text(
    hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name+'\n',
    encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('checks','icon_legibility')},indent=2))
print(f'Packaged {len(packaged_files())} files; ZIP {archive.stat().st_size:,} bytes.')
