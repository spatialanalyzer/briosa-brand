"""Build outlined SVG assets from the committed vector master data.

Requires Python 3.12+ and the dependencies in source/requirements.txt.
"""
from pathlib import Path
import html
import json
import math
from functools import lru_cache

ROOT = Path(__file__).resolve().parents[1]
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

COLORS = {'blue':'#003875', 'cyan':'#00BAF1', 'graphite':'#585B62', 'silver':'#F2F2F2', 'white':'#FFFFFF'}
TAGLINE = 'SpatialAnalyzer integration, simplified.'
DESCRIPTION = 'An open-source gRPC bridge to the SpatialAnalyzer SDK.'
WM = json.loads((ROOT / 'source/wordmark.json').read_text(encoding='utf-8'))
FONT = instantiateVariableFont(TTFont(ROOT / 'fonts/Inter-Variable.ttf'), {'wght':400, 'opsz':14}, inplace=False)
GLYPHS = FONT.getGlyphSet()
CMAP = FONT.getBestCmap()
UNITS = FONT['head'].unitsPerEm
SQRT3 = math.sqrt(3)
MARK_W = 320
MARK_H = 244 - 92 / SQRT3 + 112 / SQRT3
PLANES = {
    'left': [[0,190], [144,190-144/SQRT3], [144,286-144/SQRT3], [0,286]],
    'upper': [[160,0], [248,88/SQRT3], [248,148+88/SQRT3], [160,148]],
    'lower': [[116,244], [208,244-92/SQRT3], [320,244-92/SQRT3+112/SQRT3], [228,244+112/SQRT3]],
}
# The lower plane's far lower vertex is the vertical extent of the symbol.
MARK_H = max(p[1] for points in PLANES.values() for p in points)
THEMES = {
    'color': [COLORS['blue'], COLORS['cyan'], COLORS['graphite'], COLORS['graphite']],
    'inverse': [COLORS['white'], COLORS['cyan'], COLORS['silver'], COLORS['white']],
    'black': ['#000000'] * 4,
    'white': ['#FFFFFF'] * 4,
}
MANIFEST = []

def n(v):
    return f'{v:.4f}'.rstrip('0').rstrip('.') if isinstance(v, float) else str(v)

def svg(width, height, content, title, desc=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{n(width)}" height="{n(height)}" '
            f'viewBox="0 0 {n(width)} {n(height)}" role="img" aria-labelledby="title desc">\n'
            f'<title id="title">{html.escape(title)}</title>\n'
            f'<desc id="desc">{html.escape(desc or title)}</desc>\n{content}\n</svg>\n')

def write_asset(folder, filename, width, height, content, title, theme, kind, tagline=False):
    path = ROOT / folder / (filename + '.svg')
    path.parent.mkdir(parents=True, exist_ok=True)
    desc = ('Briosa. ' + TAGLINE) if tagline else title
    path.write_text(svg(width, height, content, title, desc), encoding='utf-8')
    MANIFEST.append({'file':path.relative_to(ROOT).as_posix(), 'theme':theme, 'kind':kind,
                     'width':width, 'height':height, 'tagline':tagline})

def mark(x, y, width, theme='color', micro=False):
    parts = []
    # Identical plane geometry; 16/24/32 px variants increase separation optically.
    offsets = {'left':(-8,4), 'upper':(4,-8), 'lower':(4,8)} if micro else {k:(0,0) for k in PLANES}
    ox, oy = (-8,-8) if micro else (0,0)
    mw = 332 if micro else MARK_W
    scale = width / mw
    for (name, points), fill in zip(PLANES.items(), THEMES[theme][:3]):
        dx, dy = offsets[name]
        d = 'M' + ' L'.join(f'{n(x+(px+dx-ox)*scale)},{n(y+(py+dy-oy)*scale)}' for px,py in points) + ' Z'
        parts.append(f'<path data-plane="{name}" fill="{fill}" d="{d}"/>')
    return '\n'.join(parts)

def wordmark(x, y, width=568, theme='color'):
    scale = width / WM['width']
    return (f'<g data-part="briosa-wordmark" transform="translate({n(x)} {n(y)}) scale({n(scale)})">'
            f'<path fill="{THEMES[theme][3]}" fill-rule="evenodd" d="{WM["path"]}"/></g>')

@lru_cache(maxsize=100)
def outlined_text(text, size):
    """Outline supporting typography, with kerning from the font's pair-position lookups."""
    scale = size / UNITS
    names = [CMAP[ord(char)] for char in text]
    cursor = 0
    pieces = []
    for index, name in enumerate(names):
        pen = SVGPathPen(GLYPHS)
        transformed = TransformPen(pen, (scale, 0, 0, -scale, cursor, 0))
        GLYPHS[name].draw(transformed)
        pieces.append(pen.getCommands())
        advance = FONT['hmtx'][name][0]
        if index + 1 < len(names) and 'GPOS' in FONT:
            second = names[index+1]
            for lookup in FONT['GPOS'].table.LookupList.Lookup:
                subtables = lookup.SubTable
                if lookup.LookupType == 9:
                    subtables = [s.ExtSubTable for s in subtables if s.ExtensionLookupType == 2]
                elif lookup.LookupType != 2:
                    continue
                for table in subtables:
                    if name not in table.Coverage.glyphs:
                        continue
                    value = None
                    if table.Format == 1:
                        i = table.Coverage.glyphs.index(name)
                        pair = next((p for p in table.PairSet[i].PairValueRecord if p.SecondGlyph == second), None)
                        if pair:
                            value = pair.Value1
                    elif table.Format == 2:
                        c1 = table.ClassDef1.classDefs.get(name, 0)
                        c2 = table.ClassDef2.classDefs.get(second, 0)
                        value = table.Class1Record[c1].Class2Record[c2].Value1
                    if value:
                        advance += getattr(value, 'XAdvance', 0) or 0
                    break
        cursor += advance * scale
    return ' '.join(pieces), cursor

def text(text_value, x, baseline, size, color, align='left', max_width=None):
    path, width = outlined_text(text_value, size)
    if max_width and width > max_width:
        size *= max_width / width
        path, width = outlined_text(text_value, size)
    if align == 'center':
        x -= width / 2
    elif align == 'right':
        x -= width
    return f'<g transform="translate({n(x)} {n(baseline)})"><path fill="{color}" d="{path}"/></g>'

def rect(x,y,w,h,fill,rx=0):
    return f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(rx)}" fill="{fill}"/>'

def logo(theme, layout, tagline):
    col = THEMES[theme][3]
    if layout == 'horizontal':
        if tagline:
            w,h = 872,272
            parts = mark(32,36,200,theme) + wordmark(272,38,568,theme)
            parts += text(TAGLINE,272,231,30,col,max_width=568)
        else:
            w,h = 852,238
            parts = mark(32,32,180,theme) + wordmark(252,48,568,theme)
    else:
        w,h = (704,624) if tagline else (704,568)
        parts = mark(192,32,320,theme) + wordmark(68,382,568,theme)
        if tagline:
            parts += text(TAGLINE,352,588,30,col,align='center',max_width=640)
    return w,h,parts

def make_assets():
    for theme in THEMES:
        write_asset('marks',f'briosa-symbol-{theme}',384,MARK_H+64,mark(32,32,320,theme),
                    f'Briosa symbol — {theme}',theme,'symbol')
        write_asset('logos',f'briosa-wordmark-{theme}',600,174,wordmark(16,16,568,theme),
                    f'Briosa wordmark — {theme}',theme,'wordmark')
        for layout in ('horizontal','stacked'):
            for tagline in (False,True):
                w,h,content = logo(theme,layout,tagline)
                suffix = '-tagline' if tagline else ''
                write_asset('logos',f'briosa-{layout}{suffix}-{theme}',w,h,content,
                            f'Briosa {layout} logo — {theme}',theme,'logo',tagline)
    for slug,label in [('server','server'),('dotnet','.NET'),('js','JS'),('python','Python'),('docs','docs')]:
        for theme in ('color','inverse'):
            parts = mark(24,29,128,theme) + wordmark(184,26,360,theme)
            parts += text('/ '+label,184,157,32,THEMES[theme][3])
            write_asset('suite',f'briosa-{slug}-{theme}',600,192,parts,
                        f'Briosa {label} — {theme}',theme,'suite')
    for filename,rounded,micro in [('app-icon',True,False),('app-icon-maskable',False,False),('favicon',True,True)]:
        # Insets keep the symbol inside an OS-mask-safe central area.
        mw = 660 if rounded else 560
        mh = (MARK_H + 16) / 332 * mw if micro else MARK_H / 320 * mw
        parts = rect(0,0,1024,1024,COLORS['blue'],180 if rounded else 0)
        parts += mark((1024-mw)/2,(1024-mh)/2,mw,'inverse',micro)
        write_asset('icons',filename,1024,1024,parts,'Briosa application icon','inverse','icon')
    write_asset('source','briosa-master',704,624,logo('color','stacked',True)[2],
                'Briosa master identity','color','master',True)
    # A borderless natural-size rasterization target for source/outline comparison.
    (ROOT/'qa').mkdir(exist_ok=True)
    (ROOT/'qa/wordmark-trace.svg').write_text(svg(WM['width']+8,WM['height']+8,
        wordmark(4,4,568,'black'),'Briosa wordmark tracing verification'),encoding='utf-8')

def make_preview():
    width,height = 1600,1320
    content = rect(0,0,width,height,'#FFFFFF')
    content += rect(0,0,850,790,COLORS['blue'])
    content += text('BRIOSA / BRAND ASSETS',64,54,16,'#FFFFFF')
    content += text('SELECTED IDENTITY',1536,54,16,COLORS['graphite'],align='right')
    content += mark(270,110,310,'inverse') + wordmark(118,444,614,'inverse')
    content += text(TAGLINE,425,660,31,'#FFFFFF',align='center',max_width=700)
    content += text('Vector logos  /  Outlined lettering  /  Suite lockups',425,738,16,'#FFFFFF',align='center')
    content += mark(1105,116,240,'color') + wordmark(994,404,462,'color')
    content += text(TAGLINE,1225,566,23,COLORS['graphite'],align='center',max_width=610)
    content += text('FULL COLOR ON WHITE',1225,678,14,COLORS['graphite'],align='center')
    content += text('SpatialAnalyzer integration, simplified.',64,848,28,COLORS['blue'])
    labels = [('Deep blue',COLORS['blue']),('Cyan',COLORS['cyan']),('Graphite',COLORS['graphite']),('Silver',COLORS['silver']),('White',COLORS['white'])]
    for i,(name,fill) in enumerate(labels):
        x = 64 + i*296
        if name == 'White':
            content += rect(x-1,883,265,86,COLORS['silver'])
        content += rect(x,884,263,84,fill,8)
        content += text(name,x,1002,19,COLORS['graphite'])
        content += text(fill,x,1032,16,COLORS['blue'])
    content += rect(64,1060,1472,1,COLORS['silver'])
    for i,label in enumerate(('server','.NET','JS','Python','docs')):
        x = 64 + i*296
        content += mark(x,1100,54,'color') + wordmark(x+73,1104,161,'color')
        content += text('/ '+label,x+73,1191,21,COLORS['graphite'])
    content += rect(64,1220,1472,1,COLORS['silver'])
    content += text('All logo lettering is vector artwork. No font installation required.',64,1270,17,COLORS['graphite'])
    content += text('BRIOSA / 2026',1536,1270,14,COLORS['graphite'],align='right')
    (ROOT/'preview.svg').write_text(svg(width,height,content,'Briosa brand asset pack',TAGLINE),encoding='utf-8')

if __name__ == '__main__':
    make_assets()
    make_preview()
    (ROOT/'source/symbol.json').write_text(json.dumps({'width':MARK_W,'height':MARK_H,'planes':PLANES},indent=2)+'\n',encoding='utf-8')
    version = (ROOT/'VERSION').read_text(encoding='utf-8').strip()
    (ROOT/'manifest.json').write_text(json.dumps({'brand':'Briosa','version':version,'tagline':TAGLINE,'description':DESCRIPTION,'palette':COLORS,'assets':MANIFEST},indent=2)+'\n',encoding='utf-8')
    (ROOT/'colors.json').write_text(json.dumps({'brand':'Briosa','colors':COLORS,'text_on_light':COLORS['graphite'],'link_on_light':COLORS['blue'],'text_on_dark':COLORS['white'],'accent_on_dark':COLORS['cyan']},indent=2)+'\n',encoding='utf-8')
    (ROOT/'colors.css').write_text(':root {\n'+''.join(f'  --briosa-{k}: {v};\n' for k,v in COLORS.items())+'}\n',encoding='utf-8')
    print(f'Built {len(MANIFEST)} outlined SVG assets and the brand preview.')
