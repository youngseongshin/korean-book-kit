"""Hand-built SVG illustrations: flat gouache shapes with a slightly
mis-registered ink line, like a two-colour risograph print."""
import math

INK = '#2F2A24'
PAPER = '#FBF7EF'
CREAM = '#F4EAD8'
TERRA = '#C0603F'
TERRA_L = '#E5A98C'
SAGE = '#8A9B74'
SAGE_D = '#5E6E4E'
SAGE_L = '#C9D3B8'
OCHRE = '#E2AE4F'
OCHRE_L = '#F2D9A6'
TANG = '#EE8C3A'
TANG_D = '#CF6E26'
INDIGO = '#3F5170'
INDIGO_L = '#8FA3BE'
SKY = '#BFD0DC'
WOOD = '#C08D61'
WOOD_D = '#946240'
WOOD_L = '#DDB58C'
TEA = '#C7843A'
ROSE = '#E9C2B2'
WHITE = '#FFFDF8'


def ink(d, fill, sw=2.2, off=(1.4, 1.1), op=0.9, extra=''):
    """Filled shape + offset ink outline."""
    out = ''
    if fill and fill != 'none':
        out += f'<path d="{d}" fill="{fill}" {extra}/>'
    out += (f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round" '
            f'stroke-linecap="round" opacity="{op}" transform="translate({off[0]} {off[1]})"/>')
    return out


def line(d, sw=2.2, color=INK, op=0.9):
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round" opacity="{op}"/>')


def circ(cx, cy, r, fill, sw=2.2, off=(1.4, 1.1), stroke=True):
    s = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'
    if stroke:
        s += (f'<circle cx="{cx + off[0]}" cy="{cy + off[1]}" r="{r}" fill="none" stroke="{INK}" '
              f'stroke-width="{sw}" opacity="0.9"/>')
    return s


def ell(cx, cy, rx, ry, fill, sw=2.2, stroke=True, op=1):
    s = f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" opacity="{op}"/>'
    if stroke:
        s += (f'<ellipse cx="{cx + 1.4}" cy="{cy + 1.1}" rx="{rx}" ry="{ry}" fill="none" stroke="{INK}" '
              f'stroke-width="{sw}" opacity="0.9"/>')
    return s


def g(x, y, s, content, rot=0):
    return f'<g transform="translate({x} {y}) rotate({rot}) scale({s})">{content}</g>'


# ---------------------------------------------------------------- motifs
def cup(color=WHITE, band=None, tea=True):
    """Handleless Korean tea cup, origin at rim centre, ~60 wide, 46 tall."""
    body = 'M -30 0 L 30 0 Q 28 32 14 40 L -14 40 Q -28 32 -30 0 Z'
    s = ink(body, color)
    if band:
        s += f'<path d="M -29 12 L 29 12 L 27.5 19 L -27.5 19 Z" fill="{band}" opacity="0.85"/>'
    s += ink('M -12 40 L 12 40 L 11 45 L -11 45 Z', color, sw=2)
    s += ell(0, 0, 30, 6.5, '#F7EFE3', sw=2)
    if tea:
        s += f'<ellipse cx="0" cy="1.3" rx="25.5" ry="4.6" fill="{TEA}"/>'
        s += f'<ellipse cx="-8" cy="0.4" rx="7" ry="1.3" fill="#E8B77A" opacity="0.8"/>'
    return s


def mug(color=TERRA, tea=True):
    """Mug with handle, origin at rim centre, ~52 wide, 50 tall."""
    s = line('M 25 10 C 44 8 44 36 25 34', sw=7, color=color, op=1)
    s += line('M 26 10 C 45 8 45 36 26 34', sw=2, op=0.9)
    s += ink('M -26 0 L 26 0 L 25 44 Q 25 50 19 50 L -19 50 Q -25 50 -25 44 Z', color)
    s += ell(0, 0, 26, 5.5, '#F2E2D2', sw=2)
    if tea:
        s += f'<ellipse cx="0" cy="1.2" rx="22" ry="3.8" fill="{TEA}"/>'
    s += f'<path d="M -18 10 L -18 40" stroke="{WHITE}" stroke-width="4" opacity="0.35" stroke-linecap="round"/>'
    return s


def teapot(color=SAGE):
    """Teapot, origin roughly at belly centre; ~140 wide incl. spout."""
    s = line('M -38 -2 C -66 -8 -66 32 -36 28', sw=8, color=color, op=1)
    s += line('M -37 -2 C -65 -8 -65 32 -35 28', sw=2, op=0.9)
    s += ink('M 34 4 C 52 0 58 -14 70 -22 L 75 -17 C 64 -6 60 16 38 26 Z', color)
    s += ink('M -42 18 C -46 -14 46 -14 42 18 C 40 44 -40 44 -42 18 Z', color)
    s += f'<path d="M -26 2 C -22 -6 -10 -9 0 -9" stroke="{WHITE}" stroke-width="5" fill="none" opacity="0.35" stroke-linecap="round"/>'
    s += ell(0, -8, 24, 6, SAGE_L if color == SAGE else WOOD_L, sw=2)
    s += circ(0, -16, 5.5, color, sw=2)
    s += f'<path d="M -40 24 L 40 24" stroke="{INK}" stroke-width="1.2" opacity="0.35"/>'
    return s


def tangerine(r=20, leaf=True, rot=0):
    s = circ(0, 0, r, TANG, sw=2)
    s += f'<ellipse cx="{-r * 0.35}" cy="{-r * 0.35}" rx="{r * 0.28}" ry="{r * 0.16}" fill="#FFC27E" opacity="0.8" transform="rotate(-35 {-r * 0.35} {-r * 0.35})"/>'
    for (dx, dy) in [(0.3, 0.2), (0.5, -0.1), (-0.1, 0.5), (0.15, 0.6), (0.55, 0.35), (-0.4, 0.25)]:
        s += f'<circle cx="{dx * r}" cy="{dy * r}" r="{r * 0.035 + 0.3}" fill="{TANG_D}" opacity="0.6"/>'
    s += circ(0, -r + 1.5, r * 0.09 + 0.8, SAGE_D, stroke=False)
    if leaf:
        lr = r * 0.9
        s += ink(f'M 0 {-r + 1} Q {lr * 0.45} {-r - lr * 0.75} {lr * 1.15} {-r - lr * 0.35} '
                 f'Q {lr * 0.55} {-r + lr * 0.2} 0 {-r + 1} Z', SAGE, sw=1.8)
        s += line(f'M 1 {-r} Q {lr * 0.5} {-r - lr * 0.3} {lr * 1.05} {-r - lr * 0.33}', sw=1.2, op=0.5)
    return g(0, 0, 1, s, rot) if rot else s


def peel(color=TANG):
    """A tangerine peel stripped off in one long ribbon (the ribbon 정호 broke)."""
    d = 'M 0 0 C 20 -18 46 -10 52 6 C 58 22 40 34 24 28 C 10 22 14 6 28 8 C 40 10 40 22 30 22'
    s = line(d, sw=11, color=color, op=1)
    s += line(d, sw=11, color='#FFD3A0', op=0.0)
    s += f'<path d="{d}" fill="none" stroke="#FCE3C4" stroke-width="5" stroke-linecap="round" opacity="0.7" transform="translate(-1 -1)"/>'
    s += f'<g transform="translate(1.3 1.1)">' + line(d, sw=1.6, op=0.6) + '</g>'
    return s


def steam(h=40, n=2, gap=12, op=0.45):
    s = ''
    for k in range(n):
        x = (k - (n - 1) / 2) * gap
        s += line(f'M {x} 0 C {x - 8} {-h * 0.25} {x + 8} {-h * 0.5} {x} {-h * 0.7} '
                  f'C {x - 6} {-h * 0.85} {x + 4} {-h * 0.95} {x} {-h}', sw=2, op=op)
    return s


def umbrella_closed(color=INDIGO, h=1.0):
    s = line('M 0 -70 L 0 -98 Q 0 -112 -12 -112 Q -23 -112 -23 -101', sw=5, color=WOOD_D, op=1)
    s += line('M 1 -70 L 1 -98 Q 1 -112 -11 -112 Q -22 -112 -22 -101', sw=1.6, op=0.8)
    s += ink('M 0 -72 C 13 -50 15 10 3 48 L -3 48 C -15 10 -13 -50 0 -72 Z', color)
    s += f'<path d="M -2 -60 C -6 -30 -6 10 -2 40" stroke="{WHITE}" stroke-width="2.4" fill="none" opacity="0.35"/>'
    s += ink('M -9 -12 L 9 -12 L 9 -5 L -9 -5 Z', OCHRE, sw=1.6)
    s += line('M 0 48 L 0 60', sw=3)
    return s


def umbrella_open(color=TERRA, w=70):
    r = w / 2
    sc = ' '.join(f'Q {-r + (k + 0.5) * w / 5} {-6} {-r + (k + 1) * w / 5} 0' for k in range(5))
    s = ''
    d = f'M {-r} 0 C {-r} {-r * 1.05} {r} {-r * 1.05} {r} 0 '
    pts = [-r + k * w / 5 for k in range(6)][::-1]
    for k in range(5):
        d += f'Q {(pts[k] + pts[k + 1]) / 2} -7 {pts[k + 1]} 0 '
    d += 'Z'
    s = ink(d, color)
    for k in range(1, 5):
        x = -r + k * w / 5
        s += line(f'M 0 {-r * 0.78} Q {x * 0.6} {-r * 0.5} {x} 0', sw=1.2, op=0.4)
    s += line(f'M 0 {-r * 0.78} L 0 {-r * 0.92}', sw=2.4)
    s += line(f'M 0 0 L 0 {r * 0.9} Q 0 {r * 1.15} -9 {r * 1.15} Q -16 {r * 1.15} -16 {r * 0.98}', sw=3.2, color=WOOD_D, op=1)
    return s


def stand(color=OCHRE):
    s = ink('M -34 0 L 34 0 L 30 80 Q 30 86 24 86 L -24 86 Q -30 86 -30 80 Z', color)
    s += ell(0, 0, 34, 7, '#F5D79A', sw=2)
    s += f'<ellipse cx="0" cy="1" rx="28" ry="4.5" fill="{INK}" opacity="0.55"/>'
    s += f'<path d="M -31 30 L 31 30" stroke="{INK}" stroke-width="1.4" opacity="0.4"/>'
    s += f'<path d="M -31 60 L 30.5 60" stroke="{INK}" stroke-width="1.4" opacity="0.4"/>'
    return s


def kettle(color='#E0B34E'):
    """Korean yellow aluminium kettle (양은주전자)."""
    s = line('M -30 -18 C -30 -58 30 -58 30 -18', sw=4, color='#9B7A33', op=1)
    s += line('M -29 -17 C -29 -57 31 -57 31 -17', sw=1.4, op=0.7)
    s += ink('M 30 0 C 46 -6 52 -20 62 -28 L 66 -24 C 58 -12 56 10 36 22 Z', color)
    s += ink('M -38 -12 L 38 -12 L 46 34 Q 47 42 39 42 L -39 42 Q -47 42 -46 34 Z', color)
    s += f'<path d="M -40 8 L 42 8" stroke="{INK}" stroke-width="1.3" opacity="0.35"/>'
    s += ell(0, -12, 38, 7, '#F1D388', sw=2)
    s += ell(0, -16, 18, 4.5, color, sw=1.8)
    s += circ(0, -22, 4, '#9B7A33', sw=1.6)
    s += f'<path d="M -28 0 L -32 32" stroke="{WHITE}" stroke-width="5" opacity="0.35" stroke-linecap="round"/>'
    return s


def radio(color=SAGE):
    s = line('M 22 -36 L 40 -70', sw=2.6)
    s += circ(40.5, -70.5, 2.6, INK, stroke=False)
    s += ink('M -48 -36 Q -48 -40 -44 -40 L 44 -40 Q 48 -40 48 -36 L 48 22 Q 48 26 44 26 L -44 26 Q -48 26 -48 22 Z', color)
    s += circ(-20, -7, 20, '#EADFC9', sw=2)
    for k in range(-3, 4):
        s += f'<path d="M {-20 + k * 5} {-7 - (19 ** 2 - (k * 5) ** 2) ** 0.5 * 0.92} L {-20 + k * 5} {-7 + (19 ** 2 - (k * 5) ** 2) ** 0.5 * 0.92}" stroke="{INK}" stroke-width="1.2" opacity="0.45"/>'
    s += ink('M 8 -28 L 40 -28 L 40 -14 L 8 -14 Z', '#F6E7B6', sw=1.6)
    s += f'<path d="M 22 -27 L 22 -15" stroke="{TERRA}" stroke-width="2"/>'
    s += circ(15, 6, 6, WOOD_D, sw=1.6)
    s += circ(33, 6, 6, WOOD_D, sw=1.6)
    s += line('M -40 26 L -40 32 M 40 26 L 40 32', sw=3)
    return s


def bicycle(frame=TERRA):
    s = ''
    for cx in (-52, 52):
        s += f'<circle cx="{cx}" cy="0" r="34" fill="none" stroke="{INK}" stroke-width="4" opacity="0.92"/>'
        s += f'<circle cx="{cx + 1.2}" cy="1" r="30" fill="none" stroke="{INK}" stroke-width="1" opacity="0.35"/>'
        for a in range(0, 180, 30):
            dx, dy = 30 * math.cos(math.radians(a)), 30 * math.sin(math.radians(a))
            s += f'<path d="M {cx - dx} {-dy} L {cx + dx} {dy}" stroke="{INK}" stroke-width="0.8" opacity="0.4"/>'
        s += circ(cx, 0, 3.5, INK, stroke=False)
    fr = 'M -52 0 L -10 0 L 22 -42 L -24 -42 Z M -10 0 L -28 -52 M 52 0 L 26 -54'
    s += line(fr, sw=6, color=frame, op=1)
    s += f'<g transform="translate(1.2 1)">' + line(fr, sw=1.4, op=0.6) + '</g>'
    s += line('M -36 -54 L -18 -54', sw=6, color=INK)            # saddle
    s += line('M 26 -54 L 22 -64 L 34 -66', sw=3.5)               # handlebar
    s += line('M -52 -2 L -60 -36 M -66 -36 L -40 -36', sw=3, color=WOOD_D)  # rear rack
    s += circ(-10, 0, 7, frame, sw=1.6)
    return s


def bowl(color=WHITE, band=INDIGO):
    s = ink('M -40 0 L 40 0 Q 38 30 16 36 L -16 36 Q -38 30 -40 0 Z', color)
    s += f'<path d="M -38.5 9 L 38.5 9 L 37 14 L -37 14 Z" fill="{band}" opacity="0.8"/>'
    s += ink('M -14 36 L 14 36 L 13 41 L -13 41 Z', color, sw=1.8)
    s += ell(0, 0, 40, 8, '#F3E6CF', sw=2)
    s += f'<ellipse cx="0" cy="1.5" rx="35" ry="5.6" fill="#E9C489"/>'
    for k in range(5):
        s += line(f'M {-26 + k * 11} -1 C {-20 + k * 11} -7 {-14 + k * 11} 6 {-8 + k * 11} 0', sw=1.4, color='#F8E9C8', op=1)
    s += line('M 6 -26 L 52 6 M 12 -30 L 56 2', sw=2.6, color=WOOD_D, op=1)
    return s


def chair(color=SAGE, flip=False):
    sx = -1 if flip else 1
    s = ink('M -18 0 L 22 0 L 22 7 L -18 7 Z', color)
    s += ink('M -18 0 L -18 -52 L -11 -52 L -11 0 Z', color, sw=1.8)
    s += ink('M -18 -50 L -11 -50 L -11 -30 L -18 -30 Z', WOOD_L if color != WOOD else OCHRE, sw=1.4)
    s += line('M -16 7 L -18 44 M 20 7 L 22 44 M -12 7 L -10 40 M 16 7 L 14 40', sw=3.4, color=WOOD_D, op=1)
    return f'<g transform="scale({sx} 1)">{s}</g>'


def newspaper():
    s = ink('M -50 -30 L 46 -36 L 54 30 L -42 36 Z', '#F3EDE1')
    s += line('M -4 -33 L 4 33', sw=1.2, op=0.5)
    s += f'<path d="M -42 -20 L -12 -22 L -10 -6 L -40 -4 Z" fill="{INK}" opacity="0.18"/>'
    for k in range(6):
        y = -18 + k * 7.5
        s += line(f'M 10 {y - 1} L 44 {y - 3.4}', sw=1.4, op=0.35)
    for k in range(4):
        y = 4 + k * 7.5
        s += line(f'M -40 {y} L -10 {y - 2}', sw=1.4, op=0.35)
    return s


def glasses():
    s = f'<circle cx="-17" cy="0" r="13" fill="{SKY}" opacity="0.45"/><circle cx="17" cy="0" r="13" fill="{SKY}" opacity="0.45"/>'
    s += line('M -30 0 A 13 13 0 1 0 -4 0 A 13 13 0 1 0 -30 0 M 4 0 A 13 13 0 1 0 30 0 A 13 13 0 1 0 4 0', sw=2.4)
    s += line('M -4 -2 Q 0 -6 4 -2 M -30 -2 L -44 -10 M 30 -2 L 42 -12', sw=2.2)
    return s


def fish():
    """조기 on an oval plate."""
    s = ell(0, 6, 62, 18, '#F7F1E6', sw=2)
    s += ink('M -42 4 C -24 -16 18 -14 34 2 C 18 16 -22 18 -42 4 Z', '#D9A75E')
    s += ink('M 34 2 L 52 -10 L 48 3 L 52 14 Z', '#C9924A', sw=1.8)
    s += f'<path d="M -30 0 C -10 -10 14 -8 26 1" stroke="#F4D49C" stroke-width="3" fill="none" opacity="0.7"/>'
    s += circ(-32, 1, 2.6, INK, stroke=False)
    s += line('M -24 -4 Q -22 4 -24 10', sw=1.4, op=0.5)
    return s


def spool(color=TERRA):
    s = ink('M -18 -30 L 18 -30 L 18 -24 L -18 -24 Z', WOOD_L, sw=1.8)
    s += ink('M -18 24 L 18 24 L 18 30 L -18 30 Z', WOOD_L, sw=1.8)
    s += ink('M -13 -24 L 13 -24 L 13 24 L -13 24 Z', color, sw=1.8)
    for k in range(9):
        y = -20 + k * 5
        s += f'<path d="M -12 {y} L 12 {y + 2}" stroke="{INK}" stroke-width="0.8" opacity="0.3"/>'
    s += line('M 13 10 C 34 18 44 -10 30 -24 C 22 -32 36 -44 50 -36', sw=1.6, color=color, op=1)
    s += line('M 38 -52 L 62 -20', sw=2)
    s += f'<ellipse cx="40" cy="-49" rx="1.4" ry="3" fill="{PAPER}" transform="rotate(-37 40 -49)"/>'
    return s


def recorder():
    s = ink('M -50 -26 Q -50 -30 -46 -30 L 46 -30 Q 50 -30 50 -26 L 50 28 Q 50 32 46 32 L -46 32 Q -50 32 -50 28 Z', INDIGO_L)
    s += ink('M -36 -20 L 36 -20 L 36 6 L -36 6 Z', '#EDE6D7', sw=1.8)
    for cx in (-16, 16):
        s += circ(cx, -7, 8, WHITE, sw=1.6)
        s += circ(cx, -7, 2.6, INK, stroke=False)
    s += line('M -8 -1 L 8 -1', sw=1.2, op=0.6)
    for k in range(5):
        col = TERRA if k == 0 else '#D9D1C2'
        s += ink(f'M {-38 + k * 16} 14 L {-26 + k * 16} 14 L {-26 + k * 16} 24 L {-38 + k * 16} 24 Z', col, sw=1.4)
    s += circ(42, -22, 2.4, TERRA, stroke=False)
    return s


def shoes():
    one = 'M -30 0 C -30 -14 -18 -16 -8 -14 C 2 -12 8 -6 20 -4 C 30 -2 34 4 32 8 L -30 8 Z'
    s = g(-14, 6, 1, ink(one, '#5A3E2B') + line('M -24 -10 Q -14 -6 -6 -12', sw=1.4, color=WHITE, op=0.4))
    s += g(16, 0, 1, ink(one, '#6E4C35') + line('M -24 -10 Q -14 -6 -6 -12', sw=1.4, color=WHITE, op=0.4))
    return s


def pot():
    s = ''
    for a, l, c in [(-60, 46, SAGE), (-20, 54, SAGE_D), (20, 50, SAGE), (55, 40, SAGE_D)]:
        x2 = l * math.sin(math.radians(a * 0.6))
        s += line(f'M 0 0 Q {x2 * 0.3} {-l * 0.6} {x2} {-l}', sw=2, color=SAGE_D, op=1)
        s += g(x2, -l, 1, ink('M 0 0 C 10 -6 18 -2 22 6 C 12 10 4 8 0 0 Z', c, sw=1.4), a)
    s += circ(-6, -50, 5, TERRA_L, sw=1.4)
    s += ink('M -26 0 L 26 0 L 20 40 L -20 40 Z', TERRA)
    s += ink('M -29 -6 L 29 -6 L 29 4 L -29 4 Z', TERRA, sw=1.8)
    return s


def notebook():
    s = ink('M -36 -46 L 34 -46 L 34 46 L -36 46 Z', '#EEE3CC')
    s += f'<path d="M -36 -46 L -26 -46 L -26 46 L -36 46 Z" fill="{TERRA}" opacity="0.85"/>'
    for k in range(9):
        y = -32 + k * 8
        s += line(f'M -18 {y} L 26 {y}', sw=1, color=INDIGO, op=0.25)
    for k in range(4):
        y = -32 + k * 8 - 2
        s += line(f'M -16 {y} Q -6 {y - 3} 4 {y} T {14 + k * 3} {y}', sw=1.3, color=INDIGO, op=0.7)
    s += line('M 20 34 L 58 -18', sw=5, color=INDIGO)
    s += line('M 20 34 L 17 39', sw=2)
    return s


# ---------------------------------------------------------------- compositions
def svg(w, h, body, extra_defs=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%" '
            f'preserveAspectRatio="xMidYMid slice"><defs>{extra_defs}</defs>{body}</svg>')


def cover_art():
    W, H = 1480, 2100
    b = f'<rect width="{W}" height="{H}" fill="#F3E7D3"/>'
    # late-afternoon light falling on the wall
    b += f'<circle cx="1060" cy="1060" r="420" fill="{OCHRE_L}"/>'
    b += f'<circle cx="1060" cy="1060" r="420" fill="none" stroke="#EBC98A" stroke-width="3"/>'
    # window frame shadow
    b += f'<path d="M 230 640 L 560 640 L 560 1250 L 230 1250 Z" fill="#E9DAC0"/>'
    b += f'<path d="M 395 640 L 395 1250 M 230 945 L 560 945" stroke="#F3E7D3" stroke-width="16"/>'
    # table
    b += f'<path d="M 0 1470 L {W} 1470 L {W} {H} L 0 {H} Z" fill="{WOOD}"/>'
    b += f'<path d="M 0 1470 L {W} 1470 L {W} 1500 L 0 1500 Z" fill="{WOOD_L}"/>'
    for k in range(5):
        y = 1560 + k * 110
        b += f'<path d="M 0 {y} C 400 {y - 14} 900 {y + 16} {W} {y - 6}" stroke="{WOOD_D}" stroke-width="3" fill="none" opacity="0.35"/>'
    # table runner
    b += f'<path d="M 120 1490 L 1360 1490 L 1420 {H} L 60 {H} Z" fill="#F6EEDF"/>'
    b += f'<path d="M 120 1490 L 1360 1490 L 1420 {H} L 60 {H} Z" fill="none" stroke="{INK}" stroke-width="5" opacity="0.6" transform="translate(4 3)"/>'
    for k in range(8):
        y = 1520 + k * 75
        b += f'<path d="M {120 - (y - 1490) * 0.1} {y} L {1360 + (y - 1490) * 0.1} {y}" stroke="{TERRA_L}" stroke-width="5" opacity="0.6"/>'
    # tea pouring
    b += g(400, 1360, 4.2, teapot(SAGE))
    b += f'<path d="M 712 1270 C 760 1258 790 1310 800 1440" stroke="{TEA}" stroke-width="12" fill="none" stroke-linecap="round"/>'
    b += g(810, 1450, 3.7, cup(WHITE, band=INDIGO))
    b += g(1130, 1420, 3.6, mug(TERRA))
    b += g(1130, 1360, 3.6, steam(46, 2, 12))
    
    b += g(1250, 1720, 4.2, tangerine(20, True, 10))
    b += g(1050, 1750, 3.9, tangerine(20, False))
    b += g(290, 1720, 4.0, tangerine(20, True, -20))
    b += g(560, 1660, 3.6, peel())
    return svg(W, H, b)


def endpaper():
    tile = 380
    t = ''
    t += g(90, 100, 1.9, tangerine(18, True, -10))
    t += g(280, 80, 1.5, cup(WHITE, INDIGO))
    t += g(275, 280, 1.8, tangerine(16, True, 25))
    t += g(100, 280, 1.4, mug(TERRA))
    t += g(190, 190, 1.4, ink('M 0 0 C 10 -6 18 -2 22 6 C 12 10 4 8 0 0 Z', SAGE, sw=1.4), 30)
    defs = (f'<pattern id="ep" width="{tile}" height="{tile}" patternUnits="userSpaceOnUse">'
            f'<rect width="{tile}" height="{tile}" fill="#E4E8D8"/>{t}</pattern>')
    return svg(1480, 2100, '<rect width="1480" height="2100" fill="url(#ep)"/>', defs)


def part1_art():
    """Three cups and tangerines from above, on a round table."""
    b = f'<rect width="1000" height="1000" fill="#FBF1E2"/>'
    b += f'<circle cx="500" cy="500" r="420" fill="{WOOD}"/>'
    b += f'<circle cx="505" cy="506" r="420" fill="none" stroke="{INK}" stroke-width="4" opacity="0.8"/>'
    b += f'<circle cx="500" cy="500" r="370" fill="none" stroke="{WOOD_D}" stroke-width="3" opacity="0.4"/>'
    b += f'<path d="M 160 520 C 300 500 700 540 840 500" stroke="{WOOD_D}" stroke-width="3" opacity="0.25" fill="none"/>'

    def top_cup(x, y, r, color, fill_ratio=0.82, tea_c=TEA):
        s = circ(x, y, r, color, sw=3.5, off=(3, 2.5))
        s += f'<circle cx="{x}" cy="{y}" r="{r * fill_ratio}" fill="{tea_c}"/>'
        s += f'<ellipse cx="{x - r * 0.3}" cy="{y - r * 0.3}" rx="{r * 0.25}" ry="{r * 0.1}" fill="#EBC086" opacity="0.8" transform="rotate(-40 {x - r * 0.3} {y - r * 0.3})"/>'
        return s
    b += top_cup(330, 360, 78, WHITE)
    b += top_cup(610, 300, 72, INDIGO_L)
    # half-filled cup: thinner tea ring shows it is only half full
    b += top_cup(560, 600, 80, ROSE, 0.82, '#D69A55')
    b += f'<circle cx="560" cy="600" r="40" fill="{TEA}" opacity="0.9"/>'
    # teapot from above
    b += circ(310, 650, 95, SAGE, sw=4, off=(3, 2.5))
    b += circ(310, 650, 52, SAGE_L, sw=3, off=(2, 2))
    b += circ(310, 650, 14, SAGE_D, sw=2.5, off=(2, 2))
    b += ink('M 395 610 L 470 570 L 480 590 L 405 640 Z', SAGE, sw=3.5, off=(3, 2.5))
    b += line('M 220 690 C 170 700 170 610 220 610', sw=16, color=SAGE, op=1)
    # tangerines + peel
    b += g(780, 520, 3.4, tangerine(20, True, 30))
    b += g(740, 700, 3.0, tangerine(20, False))
    b += g(460, 830, 2.6, peel(), 20)
    return svg(1000, 1000, b)


def part2_art():
    """A bicycle by the river, a radio riding in the rack."""
    b = f'<rect width="1000" height="1000" fill="{OCHRE_L}"/>'
    b += f'<circle cx="760" cy="300" r="120" fill="#F7E8C6"/>'
    b += f'<path d="M 0 600 C 250 570 600 640 1000 590 L 1000 1000 L 0 1000 Z" fill="{SKY}"/>'
    for k in range(4):
        y = 680 + k * 60
        b += line(f'M {80 + k * 40} {y} q 30 -12 60 0 t 60 0 M {560 - k * 30} {y + 20} q 30 -12 60 0 t 60 0', sw=4, color=WHITE, op=0.7)
    b += f'<path d="M 0 560 C 300 540 640 590 1000 560 L 1000 640 C 640 660 300 610 0 640 Z" fill="{SAGE}"/>'
    for x in range(40, 1000, 46):
        h = 40 + (x * 37 % 50)
        b += line(f'M {x} 600 q 6 {-h * 0.6} {(x % 3 - 1) * 10} {-h}', sw=4, color=SAGE_D, op=0.9)
    b += g(500, 560, 3.6, bicycle(TERRA))
    b += g(306, 397, 1.4, radio(SAGE))
    return svg(1000, 1000, b)


def part3_art():
    """Three couples' chairs pulled close around one long table under a lamp."""
    b = f'<rect width="1000" height="1000" fill="#F1E2DE"/>'
    b += line('M 500 0 L 500 230', sw=4)
    b += ink('M 400 300 C 400 210 600 210 600 300 Z', OCHRE, sw=4, off=(3, 2.5))
    b += f'<path d="M 360 300 L 640 300 L 820 760 L 180 760 Z" fill="#FFF3CF" opacity="0.55"/>'
    b += f'<path d="M 0 840 L 1000 840 L 1000 1000 L 0 1000 Z" fill="#E1CDC6"/>'
    b += ink('M 120 560 L 880 560 L 880 590 L 120 590 Z', WOOD, sw=4, off=(3, 2.5))
    b += line('M 150 590 L 150 840 M 850 590 L 850 840', sw=14, color=WOOD_D, op=1)
    # cups on the table
    b += g(300, 545, 1.5, cup(WHITE, INDIGO))
    b += g(390, 545, 1.5, cup(ROSE))
    b += g(560, 543, 1.4, mug(TERRA))
    b += g(640, 543, 1.4, mug(INDIGO_L))
    b += g(470, 530, 1.3, tangerine(20, True))
    b += g(760, 540, 1.3, kettle())
    # three pairs of chairs
    for x, c in [(240, TERRA), (500, SAGE), (760, INDIGO_L)]:
        b += g(x - 62, 700, 2.8, chair(c, flip=False))
        b += g(x + 62, 700, 2.8, chair(c, flip=True))
    return svg(1000, 1000, b)


def part4_art():
    """Two big umbrellas in the stand; a kettle still warm."""
    b = f'<rect width="1000" height="1000" fill="#F5F1E8"/>'
    b += f'<path d="M 0 760 L 1000 760 L 1000 1000 L 0 1000 Z" fill="#D3DCE4"/>'
    for k in range(5):
        b += line(f'M 0 {800 + k * 45} L 1000 {800 + k * 45}', sw=2, color='#B3C0CC', op=1)
    b += g(300, 600, 3.7, umbrella_closed(INDIGO), -6)
    b += g(375, 590, 3.7, umbrella_closed(TERRA), 7)
    b += g(338, 530, 3.2, stand(OCHRE))
    # side table
    b += ink('M 560 600 L 900 600 L 900 625 L 560 625 Z', WOOD, sw=4, off=(3, 2.5))
    b += line('M 590 625 L 600 790 M 870 625 L 860 790', sw=12, color=WOOD_D, op=1)
    b += g(720, 520, 2.1, kettle())
    b += g(620, 590, 1.6, cup(WHITE, INDIGO))
    b += g(840, 585, 1.5, mug(SAGE))
    b += g(720, 410, 2.0, steam(36, 2, 12))
    return svg(1000, 1000, b)


def part5_art():
    """Morning on the maru: newspaper, glasses, barley tea, a notebook."""
    b = f'<rect width="1000" height="1000" fill="{WOOD_L}"/>'
    for k in range(9):
        y = k * 125
        b += f'<path d="M 0 {y} L 1000 {y}" stroke="{WOOD_D}" stroke-width="5" opacity="0.5"/>'
        b += f'<path d="M 0 {y + 60} C 300 {y + 50} 600 {y + 72} 1000 {y + 58}" stroke="{WOOD}" stroke-width="3" fill="none" opacity="0.6"/>'
    b += f'<path d="M 0 0 L 1000 0 L 1000 1000 L 0 1000 Z" fill="#FFF6E0" opacity="0.18"/>'
    b += g(430, 470, 5.0, newspaper(), -8)
    b += g(470, 400, 4.2, glasses(), -14)
    b += g(770, 680, 3.2, cup(WHITE, SAGE))
    b += g(770, 610, 2.6, steam(42, 2, 12))
    b += g(240, 760, 3.0, notebook(), 8)
    b += g(760, 270, 2.4, fish(), 4)
    return svg(1000, 1000, b)


def vignette(name):
    parts = {
        'tangerine': (130, 110, g(62, 64, 1.7, tangerine(20, True, -10))),
        'cup': (130, 110, g(65, 46, 1.4, cup(WHITE, INDIGO)) + g(65, 38, 1.0, steam(26, 2, 10))),
        'shoes': (150, 70, g(72, 42, 1.3, shoes())),
        'teapot': (160, 100, g(80, 58, 0.95, teapot(SAGE))),
        'radio': (130, 130, g(65, 88, 1.0, radio(SAGE))),
        'spool': (150, 110, g(55, 60, 1.2, spool(TERRA))),
        'bowl': (150, 100, g(68, 52, 1.15, bowl())),
        'bicycle': (200, 120, g(100, 78, 0.95, bicycle(TERRA))),
        'chairs': (140, 110, g(46, 60, 1.0, chair(TERRA)) + g(96, 60, 1.0, chair(SAGE, True))),
        'recorder': (140, 90, g(70, 46, 1.0, recorder())),
        'mug': (130, 110, g(60, 44, 1.2, mug(TERRA)) + g(60, 36, 0.9, steam(24, 2, 10))),
        'umbrella': (120, 140, g(62, 84, 1.0, umbrella_open(TERRA, 76))),
        'kettle': (160, 130, g(76, 82, 1.05, kettle())),
        'pot': (130, 130, g(65, 80, 1.0, pot())),
        'glasses': (150, 80, g(75, 46, 1.4, glasses())),
        'fish': (160, 70, g(78, 32, 1.0, fish())),
        'newspaper': (160, 110, g(78, 56, 1.0, newspaper(), -6) + g(82, 44, 0.9, glasses(), -10)),
        'notebook': (150, 120, g(66, 62, 0.95, notebook())),
    }
    w, h, body = parts[name]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w * 0.2:.1f}mm" height="{h * 0.2:.1f}mm">{body}</svg>')


PART_ART = {1: part1_art, 2: part2_art, 3: part3_art, 4: part4_art, 5: part5_art}


# ------------------------------------------------------------------ registry
# 설정 파일(book.toml)에서 이름으로 고른다.
COMPOSITIONS = {
    'cover': cover_art,          # 표지 전면: 식탁 위 찻잔·귤·주전자
    'endpaper': endpaper,        # 면지 패턴
    'part1': part1_art,          # 귤과 찻잔 (따뜻한 오렌지)
    'part2': part2_art,          # 라디오와 실패 (세이지)
    'part3': part3_art,          # 마주 놓인 의자 (테라코타)
    'part4': part4_art,          # 우산과 주전자 (인디고)
    'part5': part5_art,          # 안경·신문·생선 (나무색)
}
VIGNETTE_NAMES = ['tangerine', 'cup', 'shoes', 'teapot', 'radio', 'spool', 'bowl', 'bicycle', 'chairs',
                  'recorder', 'mug', 'umbrella', 'kettle', 'pot', 'glasses', 'fish', 'newspaper', 'notebook']


def color(name_or_hex):
    """'TANG_D' 같은 팔레트 이름이나 '#RRGGBB'를 받아 hex를 돌려준다."""
    if name_or_hex.startswith('#'):
        return name_or_hex
    return globals()[name_or_hex]


if __name__ == '__main__':
    # python3 engine/art.py gallery.html  → 모든 그림을 한 장에 모아 본다
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else 'art_gallery.html'
    cells = ''.join(f'<figure><div class="big">{f()}</div><figcaption>{k}</figcaption></figure>'
                    for k, f in COMPOSITIONS.items())
    cells += ''.join(f'<figure>{vignette(n)}<figcaption>{n}</figcaption></figure>' for n in VIGNETTE_NAMES)
    open(out, 'w').write('<!doctype html><meta charset="utf-8"><style>body{background:#FBF7EF;font-family:sans-serif;'
                         'display:flex;flex-wrap:wrap;gap:16px;padding:16px}figure{margin:0;text-align:center}'
                         '.big svg{width:220px;height:auto}</style>' + cells)
    print('wrote', out)
