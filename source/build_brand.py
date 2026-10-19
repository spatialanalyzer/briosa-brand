"""Build the outlined Briosa v2 assets from the committed geometry and fonts.

Requires Python 3.12+ and the dependencies in source/requirements.txt.
"""
from pathlib import Path
import html
import json
import math
import re

ROOT = Path(__file__).resolve().parents[1]
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

TAGLINE = 'SpatialAnalyzer integration, simplified.'
DESCRIPTION = 'An open-source gRPC bridge to the SpatialAnalyzer SDK.'
MANIFEST = []


def n(v):
    if isinstance(v, float):
        return f'{round(v, 4) + 0.0:.4f}'.rstrip('0').rstrip('.')
    return str(v)


def flatten(rgb, alpha, ground):
    """The solid color a browser paints for a translucent color over an opaque ground."""
    base = (int(ground[i:i + 2], 16) for i in (1, 3, 5))
    return '#' + ''.join(f'{round(alpha * c + (1 - alpha) * b):02X}' for c, b in zip(rgb, base))


# ---------------------------------------------------------------- color

VOID, CLEAN_ROOM, CYAN = '#040B17', '#F3F7FB', '#00BAF1'
DARK_TINT, LIGHT_TINT = (120, 190, 255), (0, 56, 117)        # hairline tints over each ground
COLORS = {
    'void': VOID,                     # dark ground
    'clean-room': CLEAN_ROOM,         # light ground
    'dark-ink': '#EAF3FF',            # beam, wordmark and text on dark
    'dark-ink-2': '#9DB3CF',          # secondary text, small-cut ticks
    'dark-ink-3': '#8199BA',          # tertiary text; 4.5:1 on every dark surface
    'dark-jaw': CYAN,                 # jaw, major ticks, accent
    'dark-point': '#FFFFFF',          # large-cut point
    'dark-point-small': '#8BE7FF',    # small-cut point, motion ring
    'dark-edge': flatten(DARK_TINT, .26, VOID),               # icon edge, dividers
    'light-ink': '#061A33',           # beam, wordmark and text on light
    'light-ink-2': '#46607E',         # secondary text
    'light-ink-3': '#536C8C',         # ticks, rule
    'light-jaw': '#0096D6',           # jaw, major ticks, point, motion ring
    'light-link': '#006DB6',          # links and accent text; the jaw is for artwork
    'light-edge': '#D6E2EE',          # icon tile edge
    'light-line': flatten(LIGHT_TINT, .24, CLEAN_ROOM),       # dividers
    'dark-tick': '#7690B0',           # large-cut ticks and the rule on dark; artwork, not text
    # Interface surfaces: an alternate band and two raised panels beside each ground.
    'dark-deep': '#071A33',
    'dark-panel': '#0B2546',
    'dark-panel-2': '#0E2C53',
    'light-deep': '#E7EFF7',
    'light-panel': '#FFFFFF',
    'light-panel-2': '#F7FAFD',
}
# The Scanline deviation scale, from -2 to +2 standard deviations.
DEVIATION = {
    'dark': {'n2': '#3E5BFF', 'n1': '#00BAF1', '0': '#34F5C5', 'p1': '#FFD23F', 'p2': '#FF4D6D'},
    'light': {'n2': '#2E47D9', 'n1': '#0096D6', '0': '#10A985', 'p1': '#D99A00', 'p2': '#DE2F55'},
}
# Status is the deviation map made text-safe: each color reads at 4.5:1 or more as a
# 10.5 px pill label on an 11% tint of itself, over every surface of its theme.
# Undecided is neutral; the others follow steps 0, -1, +1, +2 and -2.
STATUS = {
    'dark': {'current': '#34F5C5', 'next': '#00BAF1', 'undecided': '#9DB3CF', 'uncommitted': '#FFD23F',
             'excluded': '#FF7E95', 'unavailable': '#9CAEFF'},
    'light': {'current': '#076A55', 'next': '#0062A6', 'undecided': '#4A6280', 'uncommitted': '#805300',
              'excluded': '#B81E40', 'unavailable': '#3B4BC8'},
}


def theme(ink, ink2, jaw, tick_large, tick_small, point_large, point_small, rule, divider, glow=None):
    return {'ink': ink, 'ink2': ink2, 'jaw': jaw, 'tick': {'large': tick_large, 'small': tick_small},
            'point': {'large': point_large, 'small': point_small}, 'rule': rule, 'divider': divider, 'glow': glow}


C = COLORS
THEMES = {
    # Full color for light backgrounds.
    'color': theme(C['light-ink'], C['light-ink-2'], C['light-jaw'], C['light-ink-3'], C['light-ink-3'],
                   C['light-jaw'], C['light-jaw'], C['light-ink-3'], C['light-line'], glow=(CYAN, 24, .16)),
    # Full color for dark backgrounds, the primary presentation.
    'inverse': theme(C['dark-ink'], C['dark-ink-2'], C['dark-jaw'], C['dark-tick'], C['dark-ink-2'],
                     C['dark-point'], C['dark-point-small'], C['dark-tick'], C['dark-edge'], glow=(CYAN, 26, .2)),
    'black': theme(*['#000000'] * 9),
    'white': theme(*['#FFFFFF'] * 9),
}

# Interface roles per theme, for colors.json, the desktop theme and the QA proofs.
SURFACES = ('panel', 'panel-2', 'ground', 'deep')
UI = {
    'dark': {'ground': VOID, 'deep': C['dark-deep'], 'panel': C['dark-panel'], 'panel-2': C['dark-panel-2'],
             'ink': C['dark-ink'], 'ink-2': C['dark-ink-2'], 'ink-3': C['dark-ink-3'],
             'accent': C['dark-jaw'], 'accent-core': C['dark-point-small'], 'link': C['dark-jaw'],
             'tick': C['dark-tick'], 'line': C['dark-edge'], 'edge': C['dark-edge'],
             'line-tint': '#{:02X}{:02X}{:02X}'.format(*DARK_TINT)},
    'light': {'ground': CLEAN_ROOM, 'deep': C['light-deep'], 'panel': C['light-panel'], 'panel-2': C['light-panel-2'],
              'ink': C['light-ink'], 'ink-2': C['light-ink-2'], 'ink-3': C['light-ink-3'],
              'accent': C['light-jaw'], 'link': C['light-link'],
              'tick': C['light-ink-3'], 'line': C['light-line'], 'edge': C['light-edge'],
              'line-tint': '#{:02X}{:02X}{:02X}'.format(*LIGHT_TINT)},
}

# ---------------------------------------------------------------- the Caliper b mark
# The approved stroke geometry in a 256-unit grid. The beam carries vernier ticks,
# and the cyan jaw closes on the measured point in the bowl of the b.

GRID = 256
POINT = (129, 166)
CUTS = {
    # 64 px and up: fifteen fine ticks and a glow around a small point.
    'large': {'dx': 12, 'tick': 3, 'stroke': 24, 'point': 9.5,
              'ticks': 'M38 40H56M46 52H56M46 64H56M46 76H56M38 88H56M46 100H56M46 112H56M46 124H56'
                       'M38 136H56M46 148H56M46 160H56M46 172H56M38 184H56M46 196H56',
              'beam': [(76, 34), (76, 212), (140, 212)], 'jaw': [(112, 120), (182, 120), (182, 176)]},
    # 16 to 48 px and app icons: four heavy ticks, heavier strokes, a larger point.
    'small': {'dx': 15, 'tick': 7, 'stroke': 30, 'point': 15,
              'ticks': 'M28 52H48M28 92H48M28 132H48M28 172H48',
              'beam': [(76, 34), (76, 212), (138, 212)], 'jaw': [(116, 120), (182, 120), (182, 172)]},
}
# Motion only: a ring pings from the point as the jaw closes. It is invisible at rest.
MOTION = {
    'jaw': {'from_translate_y': -60, 'easing': 'cubic-bezier(.6,0,.3,1)'},
    'ring': {'r': {'large': 16, 'small': 15}, 'stroke_width': {'large': 3, 'small': '1.25px non-scaling'},
             'color': {'inverse': C['dark-point-small'], 'color': C['light-jaw']}},
    'once': {'jaw': '1.1s, delay .3s', 'ring': '.9s cubic-bezier(.2,.8,.2,1), delay 1.2s, scale 1 to 2.7, opacity .95 to 0'},
    'loop': {'duration': '5s', 'jaw': 'closes by 30%, holds to 84%, reopens at 100%',
             'ring': 'opacity .9 at 32%, scale 2.3 and opacity 0 by 62%'},
    'reduced_motion': 'Show the closed mark without animation.',
    # A reading: on hover or focus the jaw opens up the beam and closes on the point again.
    'reading': {'travel': '60/208 of the beam height', 'duration': '1s',
                'open': '0 to 40%, ease-out cubic, cubic-bezier(.33,1,.68,1)',
                'close': '40% to 100%, ease-in-out cubic, cubic-bezier(.65,0,.35,1)',
                'trigger': 'pointer entry or keyboard focus on a linked mark, or once on coming into full view',
                'ring': 'none', 'reduced_motion': 'none; the jaw stays closed'},
    'pause': 'Every loop needs a visible pause control (WCAG 2.2.2); a paused loop holds its current frame.',
}


def segment(x1, y, x2, width):
    """A butt-capped horizontal stroke as a rectangle."""
    h = width / 2
    return [(x1, y - h), (x2, y - h), (x2, y + h), (x1, y + h)]


def stroke_outline(points, width):
    """Outline an axis-aligned polyline stroked with square caps and miter joins."""
    h = width / 2
    sign = lambda v: (v > 0) - (v < 0)
    dirs = [(sign(x2 - x1), sign(y2 - y1)) for (x1, y1), (x2, y2) in zip(points, points[1:])]
    normals = [(-dy, dx) for dx, dy in dirs]
    spine = [(points[0][0] - dirs[0][0] * h, points[0][1] - dirs[0][1] * h), *points[1:-1],
             (points[-1][0] + dirs[-1][0] * h, points[-1][1] + dirs[-1][1] * h)]
    # A right-angle miter lies one half-width along both adjacent normals.
    offsets = [normals[0], *[(a[0] + b[0], a[1] + b[1]) for a, b in zip(normals, normals[1:])], normals[-1]]
    left = [(x + ox * h, y + oy * h) for (x, y), (ox, oy) in zip(spine, offsets)]
    right = [(x - ox * h, y - oy * h) for (x, y), (ox, oy) in zip(spine, offsets)]
    return left + right[::-1]


def polygon(points):
    x, y = points[0]
    d = f'M{n(x)} {n(y)}'
    for px, py in points[1:]:
        d += f'H{n(px)}' if py == y else f'V{n(py)}' if px == x else f'L{n(px)} {n(py)}'
        x, y = px, py
    return d + 'Z'


def union(*boxes):
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))


def cut_shapes(cut):
    c = CUTS[cut]
    move = lambda pts: [(float(x + c['dx']), float(y)) for x, y in pts]
    ticks = [move(segment(float(x1), float(y), float(x2), c['tick']))
             for x1, y, x2 in re.findall(r'M([\d.]+) ([\d.]+)H([\d.]+)', c['ticks'])]
    return {'ticks': ticks, 'beam': move(stroke_outline(c['beam'], c['stroke'])),
            'jaw': move(stroke_outline(c['jaw'], c['stroke'])), 'point': (POINT[0] + c['dx'], POINT[1], c['point'])}


SHAPES = {cut: cut_shapes(cut) for cut in CUTS}


def cut_bounds(cut):
    s = SHAPES[cut]
    xs, ys = zip(*[p for poly in [*s['ticks'], s['beam'], s['jaw']] for p in poly])
    x, y, r = s['point']
    return union((min(xs), min(ys), max(xs), max(ys)), (x - r, y - r, x + r, y + r))


MARK_BOX = {cut: cut_bounds(cut) for cut in CUTS}


def mark_svg(theme_name, cut):
    t, s = THEMES[theme_name], SHAPES[cut]
    x, y, r = s['point']
    parts = [f'<path data-part="ticks" fill="{t["tick"][cut]}" d="{"".join(polygon(p) for p in s["ticks"])}"/>',
             f'<path data-part="beam" fill="{t["ink"]}" d="{polygon(s["beam"])}"/>',
             f'<path data-part="jaw" fill="{t["jaw"]}" d="{polygon(s["jaw"])}"/>']
    if cut == 'large' and t['glow']:
        color, radius, opacity = t['glow']
        parts.append(f'<circle data-part="glow" cx="{n(x)}" cy="{n(y)}" r="{n(radius)}" fill="{color}" fill-opacity="{n(opacity)}"/>')
    parts.append(f'<circle data-part="point" cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="{t["point"][cut]}"/>')
    return ''.join(parts)


# ---------------------------------------------------------------- type

class Face:
    """A static font, or an instance of a variable font, with simple left-to-right outline layout."""

    def __init__(self, path, **axes):
        self.font = instantiateVariableFont(TTFont(path), axes, inplace=False) if axes else TTFont(path)
        self.axes = axes
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.upm = self.font['head'].unitsPerEm
        self.cap = self.font['OS/2'].sCapHeight / self.upm
        self.ascent = self.font['hhea'].ascent / self.upm
        self.descent = -self.font['hhea'].descent / self.upm
        self.cache = {}

    def kern(self, name, second):
        """Pair kerning from the font's pair-position lookups."""
        advance = 0
        if 'GPOS' not in self.font:
            return advance
        for lookup in self.font['GPOS'].table.LookupList.Lookup:
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
        return advance

    def layout(self, text, tracking=0.0):
        """Outline text in font units with y down, the pen starting at zero.

        Returns the path, its ink box, the pen positions and the advance. Tracking
        follows every letter, like CSS letter-spacing, but the advance ends at the
        last letter."""
        key = (text, tracking)
        if key not in self.cache:
            pen = SVGPathPen(self.glyphs, ntos=lambda v: n(round(v, 2)))
            box = BoundsPen(self.glyphs)
            names = [self.cmap[ord(char)] for char in text]
            x, positions = 0.0, []
            for index, name in enumerate(names):
                positions.append(x)
                for target in (pen, box):
                    self.glyphs[name].draw(TransformPen(target, (1, 0, 0, -1, x, 0)))
                x += self.font['hmtx'][name][0] + tracking * self.upm
                if index + 1 < len(names):
                    x += self.kern(name, names[index + 1])
            self.cache[key] = (pen.getCommands(), box.bounds, positions, x - tracking * self.upm)
        return self.cache[key]


SAIRA = ROOT / 'fonts/Saira-Variable.ttf'
INTER = ROOT / 'fonts/Inter-Variable.ttf'
JETBRAINS = ROOT / 'fonts/JetBrainsMono-Variable.ttf'
WORD = Face(SAIRA, wght=600, wdth=125)     # the wordmark
SLOGAN = Face(SAIRA, wght=500, wdth=106)   # the slogan, as set on briosa.dev
LABEL = Face(SAIRA, wght=500, wdth=125)    # product labels and captions
BODY = Face(INTER, wght=400, opsz=14)      # supporting text in the preview

WORDMARK, TRACKING = 'BRIOSA', 0.14
WM_PATH, WM_BOX, WM_PEN, WM_ADVANCE = WORD.layout(WORDMARK, TRACKING)
WM_WIDTH = WM_BOX[2] - WM_BOX[0]
# The vernier rule reproduces the identity sheet's 60 px wordmark, in em: a 14 px
# gap below the line-height-1 text box, a 2 px line, 2 px ticks hanging below it,
# 7 px minor and 13 px major. Twenty divisions span the wordmark from the B's stem
# to the A's foot, about 14 px each at 60 px, with a major tick at every fifth.
RULE = {'offset': (1 - WORD.ascent - WORD.descent) / 2 + WORD.descent + 14 / 60,
        'line': 2 / 60, 'tick': 2 / 60, 'minor': 7 / 60, 'major': 13 / 60, 'divisions': 20, 'major_every': 5}
RULE_DEPTH = RULE['offset'] + RULE['line'] + RULE['major']


def rule_paths():
    u = WORD.upm
    top, line, tick = RULE['offset'] * u, RULE['line'] * u, RULE['tick'] * u
    step = (WM_WIDTH - tick) / RULE['divisions']
    minor = [[(WM_BOX[0], top), (WM_BOX[2], top), (WM_BOX[2], top + line), (WM_BOX[0], top + line)]]
    major = []
    for k in range(RULE['divisions'] + 1):
        x = WM_BOX[0] + k * step
        is_major = k % RULE['major_every'] == 0
        depth = (RULE['major'] if is_major else RULE['minor']) * u
        (major if is_major else minor).append([(x, top + line), (x + tick, top + line),
                                               (x + tick, top + line + depth), (x, top + line + depth)])
    fmt = lambda polys: ''.join(polygon([(round(x, 2), round(y, 2)) for x, y in poly]) for poly in polys)
    return fmt(minor), fmt(major)


RULE_MINOR, RULE_MAJOR = rule_paths()

# ---------------------------------------------------------------- composition

class Element:
    """A positioned part of a composition: its ink box and a renderer for an offset."""

    def __init__(self, box, render):
        self.box, self.render = box, render


def place_mark(x, y, size, theme_name, cut):
    s = size / GRID
    b = MARK_BOX[cut]
    render = lambda dx, dy: (f'<g data-part="briosa-mark" transform="translate({n(x + dx)} {n(y + dy)}) scale({n(s)})">'
                             f'{mark_svg(theme_name, cut)}</g>')
    return Element((x + b[0] * s, y + b[1] * s, x + b[2] * s, y + b[3] * s), render)


def place_wordmark(x, cap_top, em, theme_name, rule=False):
    """BRIOSA with its B stem at x and its capitals' top at cap_top, optionally ruled."""
    t = THEMES[theme_name]
    s = em / WORD.upm
    baseline = cap_top + WORD.cap * em
    left = x - WM_BOX[0] * s
    body = f'<path data-part="letters" fill="{t["ink"]}" d="{WM_PATH}"/>'
    if rule:
        body += (f'<path data-part="rule" fill="{t["rule"]}" d="{RULE_MINOR}"/>'
                 f'<path data-part="rule-major" fill="{t["jaw"]}" d="{RULE_MAJOR}"/>')
    render = lambda dx, dy: (f'<g data-part="briosa-wordmark" transform="translate({n(left + dx)} {n(baseline + dy)}) '
                             f'scale({n(s)})">{body}</g>')
    bottom = baseline + (RULE_DEPTH * em if rule else WM_BOX[3] * s)
    return Element((x, baseline + WM_BOX[1] * s, x + WM_WIDTH * s, bottom), render)


def place_text(face, value, x, baseline, size, color, align='left', tracking=0.0):
    """Outlined text whose ink starts, centers or ends at x."""
    path, (x0, y0, x1, y1), _, _ = face.layout(value, tracking)
    s = size / face.upm
    left = x - {'left': x0, 'center': (x0 + x1) / 2, 'right': x1}[align] * s
    render = lambda dx, dy: (f'<g transform="translate({n(left + dx)} {n(baseline + dy)}) scale({n(s)})">'
                             f'<path fill="{color}" d="{path}"/></g>')
    return Element((left + x0 * s, baseline + y0 * s, left + x1 * s, baseline + y1 * s), render)


def rect(x, y, w, h, fill, rx=0):
    corner = f' rx="{n(rx)}"' if rx else ''
    return f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}"{corner} fill="{fill}"/>'


def place_rect(x, y, w, h, fill, rx=0):
    return Element((x, y, x + w, y + h), lambda dx, dy: rect(x + dx, y + dy, w, h, fill, rx))


def compose(elements, margin):
    """Fit elements on an integer canvas with at least `margin` around their ink."""
    x0, y0, x1, y1 = union(*(e.box for e in elements))
    width, height = math.ceil(x1 - x0 + 2 * margin), math.ceil(y1 - y0 + 2 * margin)
    dx, dy = (width - (x1 - x0)) / 2 - x0, (height - (y1 - y0)) / 2 - y0
    return width, height, '\n'.join(e.render(dx, dy) for e in elements)


def svg(width, height, content, title, desc=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{n(width)}" height="{n(height)}" '
            f'viewBox="0 0 {n(width)} {n(height)}" role="img" aria-labelledby="title desc">\n'
            f'<title id="title">{html.escape(title)}</title>\n'
            f'<desc id="desc">{html.escape(desc or title)}</desc>\n{content}\n</svg>\n')


def write_asset(folder, filename, width, height, content, title, theme_name, kind, tagline=False, cut=None):
    path = ROOT / folder / (filename + '.svg')
    path.parent.mkdir(parents=True, exist_ok=True)
    desc = ('Briosa. ' + TAGLINE) if tagline else title
    path.write_text(svg(width, height, content, title, desc), encoding='utf-8', newline='\n')
    entry = {'file': path.relative_to(ROOT).as_posix(), 'theme': theme_name, 'kind': kind,
             'width': width, 'height': height, 'tagline': tagline}
    if cut:
        entry['cut'] = cut
    MANIFEST.append(entry)


# ---------------------------------------------------------------- lockups
# Lockups are drawn in mark-grid units. The ruled wordmark block is centered on the
# mark's 256-unit grid with the rule's line running through the measured point, as
# in the approved horizontal lockup. The compact lockup's baseline runs through the
# point, at the proportions of the approved docs navigation (a 17 px wordmark beside
# a 32 px mark).

BLOCK = WORD.cap + RULE_DEPTH
LINE_CENTRE = WORD.cap + RULE['offset'] + RULE['line'] / 2
H_EM = (POINT[1] - GRID / 2) / (LINE_CENTRE - BLOCK / 2)
H_CAP_TOP = GRID / 2 - BLOCK / 2 * H_EM
C_EM = 17 / 32 * GRID
S_EM = 64
S_GAP = 60          # mark to capitals in the stacked lockup
GAP = 0.95          # mark to wordmark, in em
SLOGAN_GAP = 0.9    # rule to slogan capitals, in em of the slogan
LABEL_SIZE = 11 / 17
MARGIN = 32


def slogan_under(word, theme_name, align='left'):
    """The slogan below a ruled wordmark, set to the rule's exact width."""
    _, (x0, _, x1, _), _, _ = SLOGAN.layout(TAGLINE)
    width = word.box[2] - word.box[0]
    size = width / (x1 - x0) * SLOGAN.upm
    x = word.box[0] if align == 'left' else (word.box[0] + word.box[2]) / 2
    baseline = word.box[3] + (SLOGAN_GAP + SLOGAN.cap) * size
    return place_text(SLOGAN, TAGLINE, x, baseline, size, THEMES[theme_name]['ink'], align=align)


def horizontal(theme_name, tagline=False):
    mark = place_mark(0, 0, GRID, theme_name, 'large')
    word = place_wordmark(mark.box[2] + GAP * H_EM, H_CAP_TOP, H_EM, theme_name, rule=True)
    parts = [mark, word] + ([slogan_under(word, theme_name)] if tagline else [])
    return compose(parts, MARGIN)


def stacked(theme_name, tagline=False):
    mark = place_mark(0, 0, GRID, theme_name, 'large')
    width = WM_WIDTH * S_EM / WORD.upm
    word = place_wordmark(GRID / 2 - width / 2, mark.box[3] + S_GAP, S_EM, theme_name, rule=True)
    parts = [mark, word] + ([slogan_under(word, theme_name, 'center')] if tagline else [])
    return compose(parts, MARGIN)


def compact_parts(theme_name, size=GRID / 2, label=None):
    """The small cut beside the plain wordmark, optionally with a product label."""
    k = size / GRID
    em = C_EM * k
    cap_top = (POINT[1] - WORD.cap * C_EM) * k
    mark = place_mark(0, 0, size, theme_name, 'small')
    word = place_wordmark(mark.box[2] + GAP * em, cap_top, em, theme_name)
    parts = [mark, word]
    if label:
        t = THEMES[theme_name]
        middle = cap_top + WORD.cap * em / 2
        x = word.box[2] + 0.8 * em
        parts.append(place_rect(x, middle - 9 / 17 * em, em / 17, 18 / 17 * em, t['divider']))
        label_size = LABEL_SIZE * em
        parts.append(place_text(LABEL, label, x + em / 17 + 0.65 * em, middle + LABEL.cap * label_size / 2,
                                label_size, t['ink2'], tracking=0.16))
    return parts


def compact(theme_name, label=None):
    return compose(compact_parts(theme_name, label=label), MARGIN / 2)


# Application headers are too narrow for a suite lockup's label beside the wordmark,
# so the compact product logo sets the label under BRIOSA, right-aligned with it.
UNDER_SIZE = 0.5    # label size, in em of the wordmark
UNDER_GAP = 0.25    # wordmark baseline to the label's capitals, in em of the wordmark


def compact_product(theme_name, label, size=GRID / 2):
    """The compact logo with a product label under the wordmark. A label wider than
    BRIOSA is set to the wordmark's width, so both ends line up."""
    parts = compact_parts(theme_name, size)
    word = parts[1]
    k = size / GRID
    em = C_EM * k
    _, (x0, _, x1, _), _, _ = LABEL.layout(label, 0.16)
    label_size = min(UNDER_SIZE * em, (word.box[2] - word.box[0]) / (x1 - x0) * LABEL.upm)
    baseline = POINT[1] * k + UNDER_GAP * em + LABEL.cap * label_size
    parts.append(place_text(LABEL, label, word.box[2], baseline, label_size, THEMES[theme_name]['ink2'],
                            align='right', tracking=0.16))
    return compose(parts, MARGIN / 2)


# ---------------------------------------------------------------- icons

def rounded_rect(x, y, w, h, r):
    return (f'M{n(x + r)} {n(y)}H{n(x + w - r)}A{n(r)} {n(r)} 0 0 1 {n(x + w)} {n(y + r)}V{n(y + h - r)}'
            f'A{n(r)} {n(r)} 0 0 1 {n(x + w - r)} {n(y + h)}H{n(x + r)}A{n(r)} {n(r)} 0 0 1 {n(x)} {n(y + h - r)}'
            f'V{n(y + r)}A{n(r)} {n(r)} 0 0 1 {n(x + r)} {n(y)}Z')


def farthest_ink(cut, centre):
    """The largest distance from a grid point to the cut's ink, for mask safe zones."""
    s = SHAPES[cut]
    corners = [p for poly in [*s['ticks'], s['beam'], s['jaw']] for p in poly]
    x, y, r = s['point']
    return max([math.dist(p, centre) for p in corners] + [math.dist((x, y), centre) + r])


ICON = 1024
TILE_RADIUS = 25 / 112 * ICON   # the identity sheet's 112 px tile has 25 px corners
TILE_MARK = 82 / 112 * ICON     # and an 82 px small-cut mark
TILE_EDGE = 1 / 112 * ICON      # inside a 1 px edge
MASK_SAFE = 0.4 * ICON          # maskable safe zone: a centred circle, 80% of the icon wide
FAVICON_INK = 0.8               # favicon ink height, as a share of the tile


def icon(theme_name, ground, edge=None, radius=TILE_RADIUS, mark=TILE_MARK, fit_ink=False):
    parts = rect(0, 0, ICON, ICON, ground, radius)
    if edge:
        inner = TILE_EDGE
        parts += (f'<path data-part="edge" fill="{edge}" fill-rule="evenodd" d="{rounded_rect(0, 0, ICON, ICON, radius)}'
                  f'{rounded_rect(inner, inner, ICON - 2 * inner, ICON - 2 * inner, radius - inner)}"/>')
    s = mark / GRID
    if fit_ink:
        # Center the ink itself, for the tightest legible favicon.
        b = MARK_BOX['small']
        x, y = (ICON - (b[2] + b[0]) * s) / 2, (ICON - (b[3] + b[1]) * s) / 2
    else:
        # Center the 256-unit grid, as the identity sheet does.
        x = y = (ICON - mark) / 2
    return parts + '\n' + place_mark(x, y, mark, theme_name, 'small').render(0, 0)


def make_icons():
    write_asset('icons', 'app-icon', ICON, ICON, icon('inverse', VOID, C['dark-edge']),
                'Briosa application icon', 'inverse', 'icon', cut='small')
    write_asset('icons', 'app-icon-light', ICON, ICON, icon('color', CLEAN_ROOM, C['light-edge']),
                'Briosa application icon — light', 'color', 'icon', cut='small')
    # Full bleed for OS masks: keep all ink well inside the circular safe zone.
    mask_mark = 0.78 * MASK_SAFE / farthest_ink('small', (GRID / 2, GRID / 2)) * GRID
    write_asset('icons', 'app-icon-maskable', ICON, ICON, icon('inverse', VOID, radius=0, mark=mask_mark),
                'Briosa application icon', 'inverse', 'icon', cut='small')
    b = MARK_BOX['small']
    favicon_mark = FAVICON_INK * ICON / (b[3] - b[1]) * GRID
    write_asset('icons', 'favicon', ICON, ICON, icon('inverse', VOID, mark=favicon_mark, fit_ink=True),
                'Briosa favicon', 'inverse', 'icon', cut='small')


# ---------------------------------------------------------------- assets

THEME_ORDER = ('color', 'inverse', 'black', 'white')
SUITE = [('server', 'SERVER'), ('dotnet', '.NET'), ('js', 'JS'), ('python', 'PYTHON'), ('docs', 'DOCS')]
APPS = [('installer', 'INSTALLER', 'Installer'), ('control-center', 'CONTROL CENTER', 'Control Center')]


def make_assets():
    for t in THEME_ORDER:
        for cut, suffix in (('large', ''), ('small', '-small')):
            write_asset('marks', f'briosa-symbol{suffix}-{t}', GRID, GRID,
                        f'<g data-part="briosa-mark">{mark_svg(t, cut)}</g>',
                        f'Briosa symbol{" — small cut" if suffix else ""} — {t}', t, 'symbol', cut=cut)
        w, h, content = compose([place_wordmark(0, 0, 120, t)], 24)
        write_asset('logos', f'briosa-wordmark-{t}', w, h, content, f'Briosa wordmark — {t}', t, 'wordmark')
        w, h, content = compose([place_wordmark(0, 0, 120, t, rule=True)], 24)
        write_asset('logos', f'briosa-wordmark-ruled-{t}', w, h, content,
                    f'Briosa wordmark with vernier rule — {t}', t, 'wordmark')
        for layout, build in (('horizontal', horizontal), ('stacked', stacked)):
            for tagline in (False, True):
                w, h, content = build(t, tagline)
                suffix = '-tagline' if tagline else ''
                write_asset('logos', f'briosa-{layout}{suffix}-{t}', w, h, content,
                            f'Briosa {layout} logo — {t}', t, 'logo', tagline, cut='large')
        w, h, content = compact(t)
        write_asset('logos', f'briosa-horizontal-compact-{t}', w, h, content,
                    f'Briosa compact horizontal logo — {t}', t, 'logo', cut='small')
    for slug, label in SUITE:
        for t in ('color', 'inverse'):
            w, h, content = compact(t, label)
            write_asset('suite', f'briosa-{slug}-{t}', w, h, content, f'Briosa {label} — {t}', t, 'suite', cut='small')
    for slug, label, name in APPS:
        for t in THEME_ORDER:
            w, h, content = compact_product(t, label)
            write_asset('suite', f'briosa-{slug}-compact-{t}', w, h, content,
                        f'Briosa {name} compact logo — {t}', t, 'suite', cut='small')
    make_icons()
    w, h, content = stacked('color', True)
    write_asset('source', 'briosa-master', w, h, content, 'Briosa master identity', 'color', 'master', True, cut='large')
    # A natural-size target for checking the outlines against the font's own rendering.
    (ROOT / 'qa').mkdir(exist_ok=True)
    w, h, content = compose([place_wordmark(0, 0, QA_EM, 'black')], QA_PAD)
    (ROOT / 'qa/wordmark-outline.svg').write_text(svg(w, h, content, 'Briosa wordmark outline check'), encoding='utf-8', newline='\n')


QA_EM, QA_PAD = 200, 4

# ---------------------------------------------------------------- preview

def grid_lines(x, y, w, h, step, color):
    d = ''.join(f'M{n(x + i)} {n(y)}V{n(y + h)}' for i in range(step, int(w), step))
    d += ''.join(f'M{n(x)} {n(y + j)}H{n(x + w)}' for j in range(step, int(h), step))
    return f'<path fill="none" stroke="{color}" stroke-width="1" d="{d}"/>'


def caption(text, x, baseline, color, align='left', size=13):
    return place_text(LABEL, text, x, baseline, size, color, align=align, tracking=0.16).render(0, 0)


def make_preview():
    width, height = 1600, 1560
    dark_grid = flatten((120, 190, 255), .055, VOID)
    out = [rect(0, 0, width, height, VOID)]
    # Hero: the horizontal lockup on void.
    out.append(grid_lines(0, 0, width, 640, 32, dark_grid))
    out.append(caption('BRIOSA / BRAND ASSETS V2', 64, 64, C['dark-ink-2']))
    out.append(caption('CALIPER B · SELECTED IDENTITY', width - 64, 64, C['dark-ink-2'], 'right'))
    lw, lh, logo = horizontal('inverse')
    scale = 1000 / lw
    out.append(f'<g transform="translate({n((width - lw * scale) / 2)} {n(120)}) scale({n(scale)})">{logo}</g>')
    out.append(place_text(SLOGAN, TAGLINE, width / 2, 120 + lh * scale + 44, 34, C['dark-ink'], 'center').render(0, 0))
    out.append(caption('ON VOID · #040B17', 64, 608, C['dark-ink-3']))
    out.append(caption('JAW ON POINT', width - 64, 608, C['dark-ink-3'], 'right'))
    # Second band: stacked on clean room, icons and small sizes on void.
    top = 640
    out.append(rect(0, top, 800, 420, CLEAN_ROOM))
    sw, sh, stack = stacked('color')
    scale = 300 / sh
    out.append(f'<g transform="translate({n(400 - sw * scale / 2)} {n(top + 60)}) scale({n(scale)})">{stack}</g>')
    out.append(caption('ON CLEAN ROOM · #F3F7FB', 64, top + 398, C['light-ink-3']))
    out.append(rect(800, top, 800, 420, flatten((120, 190, 255), .03, VOID)))
    out.append(caption('APP ICON', 864, top + 56, C['dark-ink-3']))
    for i, (t, ground, edge) in enumerate((('inverse', VOID, C['dark-edge']), ('color', CLEAN_ROOM, C['light-edge']))):
        out.append(f'<g transform="translate({n(864 + i * 176)} {n(top + 80)}) scale({n(152 / ICON)})">'
                   f'{icon(t, ground, edge)}</g>')
    out.append(caption('48 · 32 · 24 · 16 PX', 1240, top + 56, C['dark-ink-3']))
    for row, (t, ground) in enumerate((('inverse', VOID), ('color', CLEAN_ROOM))):
        y = top + 80 + row * 84
        out.append(rect(1240, y, 296, 68, ground, 3))
        if t == 'inverse':
            out.append(f'<path fill="none" stroke="{C["dark-edge"]}" d="{rounded_rect(1240.5, y + .5, 295, 67, 3)}"/>')
        x = 1240 + (296 - 120 - 3 * 40) / 2
        for size in (48, 32, 24, 16):
            out.append(place_mark(x, y + (68 - size) / 2, size, t, 'small').render(0, 0))
            x += size + 40
    out.append(caption('DOCS NAV', 864, top + 300, C['dark-ink-3']))
    for i, (t, ground) in enumerate((('inverse', VOID), ('color', CLEAN_ROOM))):
        x, y = 864 + i * 336, top + 320
        out.append(rect(x, y, 320, 64, ground, 3))
        parts = compact_parts(t, size=36, label='DOCS')
        bx = union(*(e.box for e in parts))
        out.append('\n'.join(e.render(x + 20 - bx[0], y + 32 - (bx[1] + bx[3]) / 2) for e in parts))
        scale_colors = list(DEVIATION['dark' if t == 'inverse' else 'light'].values())
        for j, color in enumerate(scale_colors):
            out.append(rect(x + j * 64, y + 62, 64, 2, color))
    # Color.
    top = 1060
    swatches = [('VOID', VOID), ('INK', C['dark-ink']), ('INK 2', C['dark-ink-2']), ('INK 3', C['dark-ink-3']),
                ('JAW', C['dark-jaw']), ('POINT', C['dark-point-small']),
                ('CLEAN ROOM', CLEAN_ROOM), ('INK', C['light-ink']), ('INK 2', C['light-ink-2']), ('INK 3', C['light-ink-3']),
                ('JAW', C['light-jaw']), ('EDGE', C['light-edge'])]
    for i, (name, fill) in enumerate(swatches):
        x = 64 + (i % 6) * 248
        y = top + 48 + (i // 6) * 120
        out.append(rect(x, y, 224, 52, fill, 3))
        if fill in (VOID,):
            out.append(f'<path fill="none" stroke="{C["dark-edge"]}" d="{rounded_rect(x + .5, y + .5, 223, 51, 3)}"/>')
        out.append(caption(name, x, y + 78, C['dark-ink-2'], size=12))
        out.append(place_text(BODY, fill, x + 224, y + 78, 14, C['dark-ink-3'], 'right').render(0, 0))
    for i, color in enumerate(DEVIATION['dark'].values()):
        out.append(rect(64 + i * 294.4, top + 296, 294.4, 6, color))
    out.append(caption('DEVIATION SCALE · −2 TO +2', 64, top + 284, C['dark-ink-3'], size=12))
    # The product suite, then the footer line.
    out.append(rect(64, top + 344, width - 128, 1, C['dark-edge']))
    for i, (_, label) in enumerate(SUITE):
        parts = compact_parts('inverse', size=36, label=label)
        bx = union(*(e.box for e in parts))
        out.append('\n'.join(e.render(64 + i * 300 - bx[0], top + 396 - (bx[1] + bx[3]) / 2) for e in parts))
    out.append(rect(64, top + 444, width - 128, 1, C['dark-edge']))
    out.append(place_text(BODY, 'All logo lettering is outlined vector artwork. No font installation required.',
                          64, top + 478, 15, C['dark-ink-2']).render(0, 0))
    out.append(caption('BRIOSA / 2026', width - 64, top + 478, C['dark-ink-3'], 'right', size=12))
    (ROOT / 'preview.svg').write_text(svg(width, height, '\n'.join(out), 'Briosa brand asset pack', TAGLINE), encoding='utf-8', newline='\n')


# ---------------------------------------------------------------- fonts
# The variable fonts are the sources. The web builds are the same fonts in WOFF2. WPF
# cannot select a variable font's axes, so the desktop builds are static instances at
# the widths and weights the type roles use, each width named as its own family.

VARIABLE_FONTS = [('Saira', SAIRA), ('Inter', INTER), ('JetBrains Mono', JETBRAINS)]
LICENSES = {SAIRA: 'fonts/Saira-OFL.txt', INTER: 'fonts/Inter-OFL.txt', JETBRAINS: 'fonts/JetBrainsMono-OFL.txt'}
DESKTOP_FONTS = [
    ('Saira 106', 'Medium', SAIRA, {'wght': 500, 'wdth': 106}),     # slogan and subheads
    ('Saira 106', 'SemiBold', SAIRA, {'wght': 600, 'wdth': 106}),   # display and headings
    ('Saira 125', 'Medium', SAIRA, {'wght': 500, 'wdth': 125}),     # HUD and product labels
    ('Saira 125', 'SemiBold', SAIRA, {'wght': 600, 'wdth': 125}),   # status pills
    ('Inter', 'Regular', INTER, {'opsz': 14, 'wght': 400}),         # body and interface text
    ('Inter', 'Medium', INTER, {'opsz': 14, 'wght': 500}),
    ('Inter', 'SemiBold', INTER, {'opsz': 14, 'wght': 600}),
    ('JetBrains Mono', 'Regular', JETBRAINS, {'wght': 400}),        # code, paths and versions
    ('JetBrains Mono', 'Medium', JETBRAINS, {'wght': 500}),         # readouts
]
FONTS = []


def rel(path):
    return path.relative_to(ROOT).as_posix()


def font_axes(font):
    num = lambda v: int(v) if float(v).is_integer() else v
    return {a.axisTag: [num(a.minValue), num(a.defaultValue), num(a.maxValue)] for a in font['fvar'].axes}


def desktop_file(family, style):
    return ROOT / 'fonts/desktop' / f'{family.replace(" ", "")}-{style}.ttf'


def web_fonts():
    """WOFF2 copies of the variable fonts, plus @font-face rules for them."""
    rules = ['/* Briosa brand fonts for the web: the variable fonts in WOFF2, with every axis.',
             '   Generated by source/build_brand.py. */']
    for family, source in VARIABLE_FONTS:
        font = TTFont(source, recalcBBoxes=False, recalcTimestamp=False)
        span = font_axes(font)
        path = ROOT / 'fonts/web' / source.with_suffix('.woff2').name
        path.parent.mkdir(parents=True, exist_ok=True)
        font.flavor = 'woff2'
        font.save(path)
        FONTS.append({'file': rel(path), 'family': family, 'format': 'woff2', 'use': 'web', 'source': rel(source),
                      'axes': span, 'license': LICENSES[source]})
        rules += ['@font-face {', f"  font-family: '{family}';", f"  src: url('{path.name}') format('woff2');",
                  f'  font-weight: {span["wght"][0]} {span["wght"][2]};']
        if 'wdth' in span:
            rules.append(f'  font-stretch: {span["wdth"][0]}% {span["wdth"][2]}%;')
        rules += ['  font-display: swap;', '}']
    (ROOT / 'fonts/web/fonts.css').write_text('\n'.join(rules) + '\n', encoding='utf-8', newline='\n')


def desktop_font(family, style, source, location):
    """Pin every axis and name the instance for WPF's weight, width and style model."""
    font = instantiateVariableFont(TTFont(source), location, inplace=False, static=True)
    name = font['name']
    ps = f'{family.replace(" ", "")}-{style}'
    origin = name.getDebugName(16) or name.getDebugName(1)
    at = ', '.join(f'{tag} {value}' for tag, value in location.items())
    records = {1: family if style == 'Regular' else f'{family} {style}', 2: 'Regular',
               3: ';'.join(name.getDebugName(3).split(';')[:-1] + [ps]), 4: f'{family} {style}', 6: ps,
               10: f'Static instance of {origin} at {at}, made with fontTools for the Briosa brand pack.',
               16: family, 17: style}
    for name_id in (*records, 21, 22, 25):
        name.removeNames(nameID=name_id)
    for name_id, text in records.items():
        name.setName(text, name_id, 3, 1, 0x409)
    # The variable font's STAT describes a design space the instance no longer has, and
    # DirectWrite, under WPF, reads it: Saira 106 would report as UltraCondensed. Without
    # it, WPF takes the family from the name table and the width from OS/2.
    for tag in ('STAT', 'DSIG'):
        if tag in font:
            del font[tag]
    name.removeUnusedNames(font)
    os2 = font['OS/2']
    os2.fsSelection = (os2.fsSelection | 1 << 6) & ~(1 << 5 | 1)     # REGULAR, not BOLD or ITALIC
    font['head'].macStyle = 0
    path = desktop_file(family, style)
    path.parent.mkdir(parents=True, exist_ok=True)
    font.recalcTimestamp = False
    font.save(path)
    FONTS.append({'file': rel(path), 'family': family, 'style': style, 'format': 'ttf', 'use': 'desktop',
                  'source': rel(source), 'location': location, 'weight': location['wght'], 'license': LICENSES[source]})


def build_fonts():
    for family, source in VARIABLE_FONTS:
        FONTS.append({'file': rel(source), 'family': family, 'format': 'ttf', 'use': 'source',
                      'axes': font_axes(TTFont(source)), 'license': LICENSES[source]})
    web_fonts()
    for entry in DESKTOP_FONTS:
        desktop_font(*entry)


# ---------------------------------------------------------------- desktop theme
# A WPF resource dictionary for desktop apps to vendor byte-exact: both themes' colors
# and the desktop type families. Font locations are relative to the dictionary, so the
# pack's layout must be kept: desktop/ beside fonts/desktop/.

DESKTOP_FAMILIES = [
    ('BriosaDisplayFontFamily', 'Saira 106', 'Segoe UI'),
    ('BriosaLabelFontFamily', 'Saira 125', 'Segoe UI'),
    ('BriosaBodyFontFamily', 'Inter', 'Segoe UI'),
    ('BriosaMonoFontFamily', 'JetBrains Mono', 'Cascadia Mono, Consolas'),
]


def theme_roles(scheme):
    """Every interface color of a theme under one flat role name."""
    return {**UI[scheme], **{f'deviation-{k}': v for k, v in DEVIATION[scheme].items()},
            **{f'status-{k}': v for k, v in STATUS[scheme].items()}}


def desktop_key(scheme, role):
    return 'Briosa' + scheme.capitalize() + ''.join(part[:1].upper() + part[1:] for part in role.split('-')) + 'Color'


def write_desktop_theme(version):
    lines = ['<!--',
             f'  Briosa brand {version} desktop theme for WPF. Generated by source/build_brand.py.',
             '  Colors for both themes are named Briosa{Dark|Light}{Role}Color. In Windows high',
             '  contrast, use system colors instead. Font locations are relative to this file:',
             '  keep desktop/ beside fonts/desktop/, as in the brand pack.',
             '-->',
             '<ResourceDictionary xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"',
             '                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">']
    for scheme in ('dark', 'light'):
        lines.append(f'  <!-- {scheme.capitalize()} theme -->')
        lines += [f'  <Color x:Key="{desktop_key(scheme, role)}">{value}</Color>' for role, value in theme_roles(scheme).items()]
    lines.append('  <!-- Type families: static instances in ../fonts/desktop/, with system fallbacks -->')
    lines += [f'  <FontFamily x:Key="{key}">../fonts/desktop/#{family}, {fallback}</FontFamily>'
              for key, family, fallback in DESKTOP_FAMILIES]
    lines.append('</ResourceDictionary>')
    path = ROOT / 'desktop/BriosaTheme.xaml'
    path.parent.mkdir(exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')


# ---------------------------------------------------------------- system proof
# Status pills, inks and deviation steps on every surface of both themes, the gauge and
# meter motifs, and a specimen of each desktop font, outlined from the built files.

PILL = Face(SAIRA, wght=600, wdth=118)    # status pill labels, as set on briosa.dev
MONO = Face(JETBRAINS, wght=500)          # readouts
STEPS = {'n2': '−2', 'n1': '−1', '0': '0', 'p1': '+1', 'p2': '+2'}
SEVERITY = [('INFO', 'unavailable'), ('NOTE', 'next'), ('TIP', 'current'), ('CAUTION', 'uncommitted'),
            ('DANGER', 'excluded')]
METER = {0: [], 1: ['uncommitted'], 2: ['next'] * 2, 3: ['current'] * 3}
SPECIMENS = {'Saira 106': 'SpatialAnalyzer integration, simplified.', 'Saira 125': 'CONTROL CENTER · SERVER 0.9.0',
             'Inter': 'An open-source gRPC bridge to the SpatialAnalyzer SDK.',
             'JetBrains Mono': 'SetVariable("X", 331.512) → OK'}


def tint(color, alpha, ground):
    return flatten(tuple(int(color[i:i + 2], 16) for i in (1, 3, 5)), alpha, ground)


def pill(x, y, label, color, ground):
    """A 24 px status pill: a dot and an uppercase label in the color, on an 11% tint."""
    size, tracking = 10.5, 0.1
    _, _, _, advance = PILL.layout(label, tracking)
    width = 1 + 9 + 6 + 7 + advance * size / PILL.upm + tracking * size + 9 + 1
    out = (f'<rect x="{n(x + .5)}" y="{n(y + .5)}" width="{n(width - 1)}" height="23" rx="3" '
           f'fill="{tint(color, .11, ground)}" stroke="{tint(color, .42, ground)}"/>'
           f'<circle cx="{n(x + 13)}" cy="{n(y + 12)}" r="3" fill="{color}"/>')
    out += place_text(PILL, label, x + 23, y + 12 + PILL.cap * size / 2, size, color, tracking=tracking).render(0, 0)
    return out, width


def make_system_proof():
    width, top, row = 1600, 72, 116
    out = []
    for column, scheme in enumerate(('dark', 'light')):
        ui, x0 = UI[scheme], column * 800
        out.append(rect(x0, 0, 800, top, ui['ground']))
        out.append(caption(f'{scheme.upper()} · STATUS, INKS AND DEVIATION ON EVERY SURFACE', x0 + 32, 44, ui['ink-3'], size=11))
        for i, surface in enumerate(SURFACES):
            ground, y = ui[surface], top + i * row
            out.append(rect(x0, y, 800, row, ground))
            out.append(caption(f'{surface.upper()} · {ground}', x0 + 32, y + 28, ui['ink-3'], size=11))
            x = x0 + 32
            for status, color in STATUS[scheme].items():
                markup, w = pill(x, y + 42, status.upper(), color, ground)
                out.append(markup)
                x += w + 10
            x = x0 + 32
            for role in ('ink', 'ink-2', 'ink-3', 'link'):
                text = place_text(BODY, role.replace('-', ' ').capitalize(), x, y + 96, 14, ui[role])
                out.append(text.render(0, 0))
                x = text.box[2] + 20
            for step, color in DEVIATION[scheme].items():
                text = place_text(MONO, STEPS[step], x + 12, y + 96, 14, color)
                out.append(text.render(0, 0))
                x = text.box[2] + 4
        y = top + 4 * row
        out.append(rect(x0, y, 800, 88, ui['panel']))
        out.append(caption('SEVERITY GAUGES · EVIDENCE METERS', x0 + 32, y + 28, ui['ink-3'], size=11))
        x = x0 + 32
        for level, (label, status) in enumerate(SEVERITY, 1):
            for j, color in enumerate(DEVIATION[scheme].values()):
                out.append(rect(x + j * 8, y + 50, 6, 11, color if j + 1 == level else tint(color, .18, ui['panel']), 1))
            text = place_text(LABEL, label, x + 48, y + 60, 10.5, STATUS[scheme][status], tracking=0.16)
            out.append(text.render(0, 0))
            x = text.box[2] + 22
        unlit = flatten(DARK_TINT if scheme == 'dark' else LIGHT_TINT, .26 if scheme == 'dark' else .24, ui['panel'])
        for level, lit in METER.items():
            for j in range(3):
                out.append(rect(x + j * 6, y + 50, 4, 12, STATUS[scheme][lit[j]] if j < len(lit) else unlit, 1))
            out.append(place_text(MONO, str(level), x + 24, y + 61, 12, ui['ink-2']).render(0, 0))
            x += 52
    y = top + 4 * row + 88
    height = y + 96 + 44 * len(DESKTOP_FONTS)
    out.append(rect(0, y, width, height - y, CLEAN_ROOM))
    out.append(caption('DESKTOP FONTS · STATIC INSTANCES FOR WPF, OUTLINED FROM FONTS/DESKTOP', 32, y + 44, C['light-ink-3'], size=11))
    for i, (family, style, _, _) in enumerate(DESKTOP_FONTS):
        baseline = y + 100 + i * 44
        out.append(caption(f'{family} {style}'.upper(), 32, baseline - 6, C['light-ink-3'], size=11))
        out.append(place_text(Face(desktop_file(family, style)), SPECIMENS[family], 360, baseline, 26, C['light-ink']).render(0, 0))
    (ROOT / 'qa/system-proof.svg').write_text(svg(width, height, '\n'.join(out), 'Briosa system layer proof'),
                                               encoding='utf-8', newline='\n')


# ---------------------------------------------------------------- records

def records(version):
    mark = {
        'description': 'Caliper b: a lowercase b drawn as a caliper. The beam carries vernier ticks; '
                       'the jaw slides down the beam and closes on the measured point.',
        'grid': GRID, 'point': POINT,
        'cuts': {cut: {'use': '64 px and up' if cut == 'large' else '16 to 48 px, app icons and favicons',
                       'translate': [c['dx'], 0],
                       'ticks': {'d': c['ticks'], 'stroke_width': c['tick'], 'linecap': 'butt'},
                       'beam': {'points': c['beam'], 'stroke_width': c['stroke'], 'linecap': 'square', 'linejoin': 'miter'},
                       'jaw': {'points': c['jaw'], 'stroke_width': c['stroke'], 'linecap': 'square', 'linejoin': 'miter'},
                       'point_radius': c['point'],
                       'ink_bounds': [round(v, 2) for v in MARK_BOX[cut]]}
                 for cut, c in CUTS.items()},
        'glow': {'inverse': {'r': 26, 'opacity': .2, 'color': CYAN},
                 'color': {'r': 24, 'opacity': .16, 'color': CYAN}, 'cut': 'large'},
        'colors': {t: {'beam': THEMES[t]['ink'], 'jaw': THEMES[t]['jaw'], 'ticks': THEMES[t]['tick'],
                       'point': THEMES[t]['point']} for t in THEME_ORDER},
        'motion': MOTION,
    }
    (ROOT / 'source/mark.json').write_text(json.dumps(mark, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    word = {
        'description': 'The Briosa wordmark: BRIOSA in Saira, outlined. The SVGs need no font.',
        'text': WORDMARK,
        'font': {'family': 'Saira', 'file': 'fonts/Saira-Variable.ttf', 'axes': WORD.axes,
                 'units_per_em': WORD.upm, 'cap_height': round(WORD.cap * WORD.upm),
                 'ascent': round(WORD.ascent * WORD.upm), 'descent': round(WORD.descent * WORD.upm)},
        'tracking_em': TRACKING,
        'units': 'font units, y down, baseline at 0',
        'pen_positions': [round(p, 2) for p in WM_PEN],
        'ink_box': [round(v, 2) for v in WM_BOX],
        'advance': round(WM_ADVANCE, 2),
        'path': WM_PATH,
        'rule': {**{k: round(v, 4) if isinstance(v, float) else v for k, v in RULE.items()},
                 'units': 'em below the baseline; ticks hang from the line', 'minor_path': RULE_MINOR, 'major_path': RULE_MAJOR},
        'qa_em': QA_EM,
    }
    (ROOT / 'source/wordmark.json').write_text(json.dumps(word, indent=2) + '\n', encoding='utf-8', newline='\n')
    palette = {k: v for k, v in COLORS.items()}
    system = [{'file': 'colors.css', 'kind': 'css-custom-properties'}, {'file': 'colors.json', 'kind': 'color-tokens'},
              {'file': 'fonts/web/fonts.css', 'kind': 'css-font-faces'},
              {'file': 'desktop/BriosaTheme.xaml', 'kind': 'wpf-resource-dictionary'}]
    (ROOT / 'manifest.json').write_text(json.dumps({'brand': 'Briosa', 'version': version, 'tagline': TAGLINE,
                                                    'description': DESCRIPTION, 'palette': palette, 'assets': MANIFEST,
                                                    'fonts': FONTS, 'system': system},
                                                   indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    themes = {scheme: {**UI[scheme], 'deviation': DEVIATION[scheme], 'status': STATUS[scheme]} for scheme in UI}
    (ROOT / 'colors.json').write_text(json.dumps({'brand': 'Briosa', 'version': version, 'colors': COLORS,
                                                  'themes': themes, 'mark': mark['colors'],
                                                  'translucent': {'dark-edge': 'rgba(120,190,255,.26) on void',
                                                                  'light-line': 'rgba(0,56,117,.24) on clean room'}},
                                                 indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    css = [':root {']
    css += [f'  --briosa-{k}: {v};' for k, v in COLORS.items()]
    css += [f'  --briosa-{scheme}-dev-{k}: {v};' for scheme, values in DEVIATION.items() for k, v in values.items()]
    css += [f'  --briosa-{scheme}-status-{k}: {v};' for scheme, values in STATUS.items() for k, v in values.items()]
    (ROOT / 'colors.css').write_text('\n'.join(css) + '\n}\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    build_fonts()
    make_assets()
    make_preview()
    make_system_proof()
    write_desktop_theme(version)
    records(version)
    print(f'Built {len(MANIFEST)} outlined SVG assets, {len(FONTS)} font files, the desktop theme, '
          'the brand preview and the system proof.')
