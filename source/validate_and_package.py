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

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
TAGLINE = MANIFEST['tagline']
ALLOWED = set(MANIFEST['palette'].values()) | {'#000000'}
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
    tags={element.tag.removeprefix(NS) for element in root.iter()}
    check(tags <= {'svg','title','desc','g','path','rect'}, f'{item["file"]}: vector-only content')
    check(root.find(NS+'title') is not None and root.find(NS+'desc') is not None, f'{item["file"]}: accessible title and description')
    check(not re.search(r'(?:href=|url\(|data:image|<text\b|<image\b|<script\b|font-family)',xml), f'{item["file"]}: no external image, script or font dependency')
    ids=[node.attrib['id'] for node in root.iter() if 'id' in node.attrib]
    check(len(ids)==len(set(ids)), f'{item["file"]}: unique IDs')
    fills={node.attrib['fill'] for node in root.iter() if 'fill' in node.attrib}
    check(fills <= ALLOWED, f'{item["file"]}: exact approved colors')
    check('Precision, connected.' not in xml, f'{item["file"]}: superseded slogan absent')
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
check(np.array_equal(np.asarray(ico.ico.getimage((16,16))),np.asarray(frames[16])),'ICO preserves the dedicated optical 16 px frame')

src=np.asarray(Image.open(ROOT/'source/wordmark-mask.png'))<128
raster=np.asarray(Image.open(ROOT/'qa/wordmark-trace.png').convert('RGBA'))[4:-4,4:-4,3]>127
iou=float(np.logical_and(src,raster).sum()/np.logical_or(src,raster).sum())
check(iou>0.98,'Outlined wordmark preserves over 98% silhouette overlap with selected lettering')

def components(mask):
    seen=np.zeros_like(mask,dtype=bool)
    count=0
    areas=[]
    for y,x in zip(*np.where(mask)):
        if seen[y,x]: continue
        count+=1
        queue=deque([(int(y),int(x))]);seen[y,x]=True;area=0
        while queue:
            py,px=queue.popleft();area+=1
            for dy,dx in [(-1,0),(1,0),(0,-1),(0,1)]:
                yy,xx=py+dy,px+dx
                if 0<=yy<mask.shape[0] and 0<=xx<mask.shape[1] and mask[yy,xx] and not seen[yy,xx]:
                    seen[yy,xx]=True;queue.append((yy,xx))
        areas.append(area)
    return count,areas

icon_results=[]
for size in [16,24,32,48,64,128]:
    im=Image.open(ROOT/f'icons/briosa-icon-{size}.png').convert('RGBA')
    arr=np.asarray(im)
    # The navy background has a red channel of zero; each plane has strong green.
    mask=(arr[:,:,1]>120)&(arr[:,:,3]>127)
    count,areas=components(mask)
    icon_results.append({'size':size,'visible_plane_components':count,'component_pixels':areas})
    check(count==3,f'{size} px icon: three separate visible planes')

font=ImageFont.truetype(str(ROOT/'fonts/Inter-Variable.ttf'),24)
proof=Image.new('RGB',(1264,276),'#F2F2F2')
draw=ImageDraw.Draw(proof)
draw.text((36,22),'APPROVED CONCEPT',font=font,fill='#585B62')
draw.text((668,22),'SVG OUTLINE',font=font,fill='#585B62')
origin=Image.open(ROOT/'source/approved-concept.png').convert('RGB').crop((128,456,696,598))
proof.paste(origin,(36,80))
trace=Image.open(ROOT/'qa/wordmark-trace.png').convert('RGBA').crop((4,4,572,146))
white=Image.new('RGBA',trace.size,'#FFFFFF');white.putalpha(trace.getchannel('A'))
back=Image.new('RGBA',trace.size,'#003875');back.alpha_composite(white)
proof.paste(back.convert('RGB'),(668,80))
smallfont=ImageFont.truetype(str(ROOT/'fonts/Inter-Variable.ttf'),18)
draw.text((36,240),'Same scale. The wordmark is an outline, not a replacement font.',font=smallfont,fill='#585B62')
proof.save(ROOT/'qa/source-outline-comparison.png')

report={
    'version':VERSION,
    'status':'passed' if not failures else 'failed',
    'svg_assets':len(MANIFEST['assets']),
    'checks_passed':sum(r['passed'] for r in results),
    'checks_total':len(results),
    'wordmark_silhouette_iou':iou,
    'icon_separation':icon_results,
    'failures':failures,
    'checks':results,
}
(ROOT/'qa/validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
summary=f'''# Asset Validation

Status: **{report['status']}**. {report['checks_passed']} of {report['checks_total']} automated checks passed.

Brand version: **{VERSION}**.

- {report['svg_assets']} deliverable SVG assets were parsed and checked for vector-only content, approved solid colors, accessible titles/descriptions, unique IDs, and absence of external images, scripts and font dependencies.
- Every exported logo, symbol and suite PNG was checked for visibility, transparent background, and unclipped artwork with safety padding.
- The outlined wordmark achieved **{iou:.2%} silhouette overlap** with the selected concept at the source scale. This checks tracing fidelity, not an independent design or trademark assessment.
- Icons at 16, 24, 32, 48, 64 and 128 px retain three separate visible planes. The 16/24/32 px artwork has slightly larger gaps for optical clarity.
- The ICO contains six frames and preserves the dedicated 16 px optical artwork.
- Exact slogan: **{TAGLINE}**

## Visual Proofs

![Source versus vector lettering](source-outline-comparison.png)

![Color, inverse, black, white and small-size variants](variant-and-size-proof.png)

The generated preview and these proofs must also be visually inspected after a rebuild. Automated checks alone do not establish visual quality. The original delivery was visually reviewed for shape fidelity, readable slogan placement, correct color assignment, and clear small-size icons.

Detailed results: [validation.json](validation.json).
'''
(ROOT/'qa/VALIDATION.md').write_text(summary,encoding='utf-8')
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
        'fonts': ['*.ttf', 'OFL.txt'],
        'source': ['*.py', '*.cjs', '*.json', '*.txt', '*.md', '*.svg', '*.png'],
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
(ROOT/'SHA256SUMS.txt').write_text('\n'.join(checksums)+'\n',encoding='utf-8')
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
    encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('checks','icon_separation')},indent=2))
print(f'Packaged {len(packaged_files())} files; ZIP {archive.stat().st_size:,} bytes.')
