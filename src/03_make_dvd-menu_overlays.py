#!/usr/bin/env python3
import os
import numpy as np
from PIL import Image, ImageDraw
# need pil >= 9.2 or else the arrow may not render properly
import PIL
assert PIL.__version__ >= '9.2'

try: os.mkdir('menu-data')
except: pass

fn_transparent = 'menu-data/men_169_transparent.png'

proper_name, toggle_menu_name = "Skistuas stjerner", 'innstillinger'

fn_logo = 'pngkey.com-ntsc-logo-png-3816534.png'
fn_logo = 'dvd-video-2-logo-black-and-white.png'

if True:
    bkg = (0,255,0,0)
    im = Image.new('RGBA',(720,480),bkg)
    im.save(fn_transparent)

def draw_smiley(xc, yc, scale=60):
    c1 = (192,127,0)
    c2 = (255,255,0)
    width = int(.5+0.1 * scale)
    draw.ellipse((xc-scale, yc-scale, xc+scale, yc+scale), fill=c2, outline=c1, width=width)
    y_eye = int(.5+yc-0.25*scale)
    dx_eye = int(.5+0.39*scale)
    w_eye = width
    draw.ellipse((xc-dx_eye-w_eye, y_eye-w_eye, xc-dx_eye+w_eye, y_eye+w_eye), fill=c1, width=0)
    draw.ellipse((xc+dx_eye-w_eye, y_eye-w_eye, xc+dx_eye+w_eye, y_eye+w_eye), fill=c1, width=0)    
    w_mouth = width
    o_m = dx_eye+w_eye
    draw.arc((xc-o_m, yc, xc+o_m, yc+o_m), 0, 180, fill=c1, width=w_mouth)


def make_star_path(n_arms=8, r_inner=0.61, angle_top_deg = 0):
    pts = []
    r_arm = 1
    d_angle = 360 / n_arms
    a0 = angle_top_deg
    for arm in range(n_arms):
        xp = -r_arm * np.sin((a0+arm*d_angle)*np.pi/180)
        yp = r_arm * np.cos((a0+arm*d_angle)*np.pi/180)

        x0 = -r_inner * np.sin((a0+(arm-0.5)*d_angle)*np.pi/180)
        y0 = r_inner * np.cos((a0+(arm-0.5)*d_angle)*np.pi/180)

        pts += [(x0,y0),(xp,yp)]
    return np.array(pts)

star = make_star_path()

def rotate(pts, angle):
    c = np.cos(angle * np.pi/180)
    s = np.sin(angle * np.pi/180)
    out = []
    for x,y in pts:
        xp = c*x + s*y
        yp = -s*x + c*y
        out.append((xp,yp))
    return np.array(out)

def i(pts):
    # return list rather than Numpy array
    return [(int(np.round(x)), int(np.round(y))) for x, y in pts]

def expand(pts, d):
    out = []
    for x,y in pts:
        x1 = x+ d * (1.1 if x > 0.09 else -1)
        y1 = y+ d * np.sign(y) * (1 + (1 if (x > 0) else -0.2))
        out.append((x1,y1))
    return np.array(out)
    

def trans(pts, v):
    return np.array([(x+v[0], y+v[1]) for x,y in pts])

make_fig = ['disclaimer','sub-menu','main-menu','cover']

if 'disclaimer' in make_fig:
    print('disclaimer')
    # make disclaimer / legal notice
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(12.8, 7.20))
    ax.set_position([0,0,1,1])
    ax.set_frame_on(False)
    fig.patch.set_color((0,0,0))
    ax.set_xlim(0,1)
    ax.set_ylim(0,1)
    text = '\n'.join(line.strip() for line in f"""
    {proper_name}, Copyright \u00a9 Christian Petrich, 2023
    Permission is granted to share, reproduce, and modify
    this work under the Creative Commons CC BY 4.0 License.
    The full license text is available at
    https://creativecommons.org/licenses/by/4.0/legalcode
    """.strip().split('\n'))
    ax.annotate(text, (0.5, 0.5),
                xycoords='axes fraction',
                ha='center', va='center',
                fontsize = 18,
                color='w')
    fig.savefig('views/view_disclaimer.jpg', dpi=100,
                pil_kwargs={'quality': 95})
    plt.close(fig)

if 'sub-menu' in make_fig:
    # make subtitle menu
    #  that allows to choose from:
    #  - show/skip transition/link movies
    #  - place a smiley at current (or next possible) intersection / turn off star help
    #  - continue (resume)
    char_run = 0x1f3c3 # person running. seguiemj.ttf, seguisym.ttf
    char_eyes = 0x1F929 # smiley with star eyes. seguiemj.ttf
    import matplotlib.pyplot as plt
    from PIL import ImageFilter
    import matplotlib.font_manager as fm
    from matplotlib import ft2font
    from matplotlib.font_manager import ttfFontProperty
    fpath = 'c:/windows/fonts/seguiemj.ttf'
    fprop = fm.FontProperties(fname=fpath)
    c1 = (192/255,127/255,0)
    c2 = (255/255,255/255,0)

    fig, ax = plt.subplots(figsize=(12.8,7.2))
    ax.axis('off')
    ax.set_position([0,0,1,1])

    img = Image.open('views/view_2-1.jpg')
    im = np.array(img)
    DX = im.shape[1]
    DY = im.shape[0]
    fs = 72
    xc = DX/2
    y1 = DY/2 - 1.5*fs
    y2 = DY/2 + 1.5*fs
    
    img_blurred = img.filter(ImageFilter.GaussianBlur(10))
    draw = ImageDraw.Draw(img_blurred)
    draw_smiley(xc, y1, scale=60)
    
    im = np.array(img_blurred)
    ax.imshow(im)
    
    ax.set_xlim(0,DX)
    ax.set_ylim(DY,0)

    ax.annotate(toggle_menu_name,(0.5,0.85),(2,-3),
                    xycoords='axes fraction',textcoords='offset points',
                    ha='center', va='center',
                    fontsize=64,color='black')

    ax.annotate(toggle_menu_name,(0.5,0.85),
                    xycoords='axes fraction',
                    ha='center', va='center',
                    fontsize=64,color='gold')
    
    ax.text(xc+4, y2+4, chr(char_run),
                fontproperties=fprop,
                fontsize=fs, ha='center',va='center',
            color=c1)
    ax.text(xc, y2, chr(char_run),
                fontproperties=fprop,
                fontsize=fs, ha='center',va='center',
            color=c2)

    fig.savefig('views/view_toggle.jpg', dpi=100)

    screen_format, screen = 'NTSC', (720,480)
    sdraw = (1280,720)

    def proj(xx,yy):
        x = int(.5+xx/1280 * 720)
        y = int(.5+yy/720 * 480)
        y = (y//2)*2 # ensure even
        return (x,y)

    s = 37
    R = 1.4*fs

    c1 = (192,127,0)
    c2 = (255,255,0)
    c3 = (255,0,0)
    
    bkg = (0,255,0,0)
    im = Image.new('RGBA',sdraw,bkg)
    draw = ImageDraw.Draw(im)
    fns = {}
    for mode in 'hs':
        draw.rectangle((0,0,im.width,im.height),fill=bkg)
        circle =list(make_star_path(n_arms=36, r_inner=1))
        circle.append(circle[0])
        circle = np.array(circle)

        bbs = []
        for y in (y1, y2):
            pcirc = i(trans(2*s*1.2*circle,(xc,y)))
            col = c1 if mode == 'h' else c3
            draw.line(pcirc, fill=col, width=int(.5+s*0.25))
            bbs.append([*proj(xc-R,y-R), *proj(xc+R,y+R)])

        im2 = im.resize(screen, resample=False)
        fn = f'men_169_toggle_{mode}.png'
        fns[mode] = f'menu-data/{fn}'
        im2.save(fns[mode],format='PNG')

    spu = f"""
<subpictures format="NTSC">
   <stream>
      <spu start="0" image="{fn_transparent}"
           highlight="{fns['h']}" select="{fns['s']}"
           force="yes" >
           <button name="smiley" x0="{bbs[0][0]}" y0="{bbs[0][1]}" x1="{bbs[0][2]}"
                y1="{bbs[0][3]}" down="run" />
           <button name="run" x0="{bbs[1][0]}" y0="{bbs[1][1]}" x1="{bbs[1][2]}"
                y1="{bbs[1][3]}" up="smiley" />
      </spu>
   </stream>
</subpictures>""".strip()
    with open('menu-data/spu_169_toggle.xml','w') as f:
        f.write(spu)

if 'main-menu' in make_fig or 'cover' in make_fig:
    import matplotlib.patches
    from matplotlib.offsetbox import AnnotationBbox, OffsetImage
    
    
    for run in ('menu','cover'):
        if run == 'menu' and 'main-menu' not in make_fig: continue
        if run == 'cover' and 'cover' not in make_fig: continue
        print('menu', run)
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(12.8,7.2))

        ax.axis('off')
        ax.set_position([0,0,1,1])
        

        img = Image.open('views/view_2-1.jpg')
        im = np.array(img)
        ax.imshow(im)

        DX = im.shape[1]
        DY = im.shape[0]

        ax.set_xlim(0,DX)
        ax.set_ylim(DY,0)

        fs = 60 if run == 'cover' else 64

        ax.annotate(proper_name,(0.5,0.85),(2,-3),
                    xycoords='axes fraction',textcoords='offset points',
                    ha='center', va='center',
                    fontsize=fs,color='black')

        ax.annotate(proper_name,(0.5,0.85),
                    xycoords='axes fraction',
                    ha='center', va='center',
                    fontsize=fs,color='gold')
        

        if run == 'menu':
            ax.annotate('Start',(0.5,0.61),
                        xycoords='axes fraction',
                        ha='center', va='center',
                        fontsize=32,
                        bbox=dict(boxstyle="round,pad=0.5",
                              fc="beige", ec="gold", lw=2))

        elif run == 'cover':
            c1 = (192/255,127/255,0)
            c2 = (255/255,255/255,0)
            xc, yc = DX/2, DY/2
            s = 50
            pstar = i(trans(2*s*1.1*star,(xc,yc)))
            pp = matplotlib.patches.Polygon(pstar, lw=0, color=c1)
            ax.add_patch(pp)
                            
            pstar = i(trans(2*s*star,(xc,yc)))
            pp = matplotlib.patches.Polygon(pstar, lw=0, color=c2)
            ax.add_patch(pp)

            if True:
                # add logo
                img = Image.open(fn_logo).convert('RGBA')
                height, width = img.height, img.width
                zoom = 0.1 * DY/height
                imagebox = OffsetImage(img, zoom=zoom)
                ab = AnnotationBbox(imagebox, (DX/2 + DY/2-zoom*1*width, DY-zoom*0.5*height), xybox=(0,0), xycoords='data', boxcoords='offset points', frameon=False )
                ax.add_artist(ab)
            # set dpi such that a print at 300 dpi will be 12 cm high
            want_pix_vertical = 300 * 12.0/2.54
            dpi = want_pix_vertical / fig.get_size_inches()[1]
            
            fig.savefig('views/view_cover.jpg', dpi=dpi)
            
        plt.close(fig)

    if 'main-menu' in make_fig:
        for mode, color, lw in [('n','gold',3),('h','gold',5),('s','red',5)]:
            fig, ax = plt.subplots(figsize=(12.8,7.2))
        
            ax.axis('off')
            ax.set_position([0,0,1,1])
            ax.set_xlim(0,DX)
            ax.set_ylim(DY,0)
            ax.annotate('Start',(0.5,0.61),
                    xycoords='axes fraction',
                    ha='center', va='center',
                    fontsize=32, color='white',
                    bbox=dict(boxstyle="round,pad=0.2",
                          fc="white", ec=color, lw=lw))

            fn_full = f'menu-data/full_men_169_main_{mode}.png'
            fig.savefig(fn_full, dpi=100)
            plt.close(fig)
            
            img = Image.open(fn_full)
            if True:
                # add transparent channel
                x = np.array(img.copy())
                for i in range(3):
                    x[:,:,i] = np.where(x[:,:,i] > 250, 0, 255)
                mask = Image.fromarray(x[:,:,1],'L')
                img.putalpha(mask)
                img.save(fn_full)
            
            im2 = img.resize((720,480), resample=False) # NTSC

            x = np.array(im2.copy())
            for i in range(3):
                x[:,:,i] = np.where(x[:,:,i] > 250, 255, 0)
            mask = Image.fromarray(255-x[:,:,1],'L')
            im3 = Image.fromarray(x)
            im3.putalpha(mask)
            
            im3.save(fn_full.replace('full_',''))
            # autooutline="infer"
    spu = """
<subpictures format="NTSC">
   <stream>
      <spu start="0" image="menu-data/men_169_main_n.png"
           highlight="menu-data/men_169_main_h.png" select="menu-data/men_169_main_s.png"
           force="yes" >
           <button name="1" x0="316" y0="158" x1="400"
                y1="210" down="1" />
      </spu>
   </stream>
</subpictures>""".strip()
    with open('menu-data/spu_169_main.xml','w') as f:
        f.write(spu)

if False:
    # stop here
    sdfdf

aspect = 16/9 # adjust for DVD 16:9
# arrow head length ahl
ahl = 0.6
# arrow head width, ahw
ahw = 1.0
# arrow stem length, asl
asl = 0.6
# arrow stem width, asw
asw = 0.3

"""
PAL
width: 720
height: 576
x-axis: 75dpi
y-axis: 80dpi
"""

"""
NTSC
width: 720
height: 480
x-axis: 81dpi
y-axis: 72dpi
"""

# arrow pointing right
arrow_rt = np.array([(0,asw/2), (0.0001,ahw/2), (ahl,0), (0.0001,-ahw/2), (0,-asw/2), (-asl,-asw/2), (-asl,asw/2), (0,asw/2)])

ctr = 's'

selections = {
        ctr:{'left':'l ul dl'.split(),
             'right':'r ur dr'.split(),
             'up':'u ul ur'.split(),
             'down':'d dr dl'.split(),
             },
        'u':{'left':'ul l dl'.split(),
             'right':'ur r dr'.split(),
             'up': [],
             'down':'d dl dr'.split(),
             },
        'd':{'left':'dl l ul'.split(),
             'right':'dr r ur'.split(),
             'up': 'u ul ur'.split(),
             'down':[],
             },
        'l':{'left':[],
             'right':'r ur dr'.split(),
             'up': 'ul u'.split(),
             'down':'dl d'.split(),
             },
        'r':{'left':'l ul dl'.split(),
             'right':[],
             'up': 'ur u'.split(),
             'down':'dr d'.split(),
             },
        'ul':{'left':['l'],
             'right':'u ur r dr'.split(),
             'up': ['u'],
             'down':'l dl d'.split(),
             },
        'dl':{'left':['l'],
             'right':'d dr r ur'.split(),
             'up': 'l ul u'.split(),
             'down':['d'],
             },
        'ur':{'right':['r'],
             'left':'u ul l dl'.split(),
             'up': ['u'],
             'down':'r dr d'.split(),
             },
        'dr':{'right':['r'],
             'left':'d dl l ul'.split(),
             'up': 'r ur u'.split(),
             'down':['d'],
             },
        }

if True:
    selections['u']['down'].insert(0,ctr)
    selections['d']['up'].insert(0,ctr)
    selections['l']['right'].insert(0,ctr)
    selections['r']['left'].insert(0,ctr)
    selections['ul']['right'].insert(selections['ul']['right'].index('r'),ctr)
    selections['dl']['right'].insert(selections['dl']['right'].index('r'),ctr)
    selections['ur']['left'].insert(selections['ur']['left'].index('l'),ctr)
    selections['dr']['left'].insert(selections['dr']['left'].index('l'),ctr)
    selections['ul']['down'].insert(selections['ul']['down'].index('d'),ctr)
    selections['ur']['down'].insert(selections['ur']['down'].index('d'),ctr)
    selections['dl']['up'].insert(selections['dl']['up'].index('u'),ctr)
    selections['dr']['up'].insert(selections['dr']['up'].index('u'),ctr)



screen_format, screen = 'PAL', (720,576)
screen_format, screen = 'NTSC', (720,480)

if aspect != 1:
    #sdraw = (int(.5+screen[0]*aspect ), int(.5+screen[1]*81/72))
    sdraw = (1280,720)
else:
    sdraw = screen


def draw_arrow(x, y, rot, scale=30, exp=None, c_arrow=(192,127,0), c_frame=(255,255,0)):
    exp = 0.13 if exp is None else exp
    scale = 60
    pgo = i(trans(scale*rotate(expand(arrow_rt,exp), rot),(x,y)))
    pgi = i(trans(scale*rotate(arrow_rt, rot), (x,y)))
    draw.polygon(pgo, fill=c_frame)
    draw.polygon(pgi, fill=c_arrow)

def draw_marker_star(x_ref, y_ref, rot, scale):
    c1 = (192,127,0)
    c2 = (255,255,0)
    #c3 = (255,0,0)

    star_scale = 0.3 * scale

    f_dx, f_dy = {0: (-1, 0),
                  45: (-1, 1),
                  90: (0, 1),
                  135: (1, 1),
                  180: (1, 0),
                  -135: (1, -1),
                  -90: (0, -1),
                  -45: (-1, -1)}[rot]

    if f_dx == 0 or f_dy == 0:
        dx = f_dx * scale * 1.8
        dy = f_dy * scale * 1.8
    else:
        dx = f_dx * scale * 1.4
        dy = f_dy * scale * 1.4
    
    xctr = x_ref + dx
    yctr = y_ref + dy
                  

    pstar = i(trans(2*star_scale*1.1*star,(xctr,yctr)))
    draw.polygon(pstar, fill=c1)
                        
    pstar = i(trans(2*star_scale*0.9*star,(xctr,yctr)))
    draw.polygon(pstar, fill=c2)

bkg = (0,255,0,0)
im = Image.new('RGBA',sdraw,bkg)
draw = ImageDraw.Draw(im)

def get_cheats(choices):
    out = []
    N = len(choices)
    for i in range(2**N):
        binary = bin(i).split('0b')[1]
        binary = '0' * (N-len(binary)) + binary
        out.append(binary[-1::-1])
    return out


def make_files(button_pattern):

    choices = button_pattern.split('-')

    modification = 'star' if 'star' in choices else 'smiley' if 'smiley' in choices else None
    if modification is not None:
        choices[choices.index(modification)] = 's'

    mod_tag = '' if modification is None else '_star' if modification == 'star' else '_smiley' if modification == 'smiley' else asasddsf

    if modification is not None:
        cheats = [None]
    else:
        cheats = get_cheats(choices)
        

    s = 50
    margin = 0.07
    y0 = im.height * margin + s
    y1 = im.height - y0
    yc = (y0+y1) // 2
    x0 = im.width * margin + s
    x1 = im.width - x0
    xc = (x0+x1) // 2


    try: os.mkdir('menu-data')
    except: pass

    ar = '43' if aspect == 1 else '169'
    c1 = (192,127,0)
    c2 = (255,255,0)
    c3 = (255,0,0)
    
    for star_cheat in cheats:
        if star_cheat is None:
            sc_tag = ''
        else:
            sc_tag = f'_spos{star_cheat}'
                

        fns = {}
        for mode in ('n','s','h'):
            
            if mode == 'n':
                carrow, cframe = c1, c2
            if mode == 'h':
                carrow, cframe = c2, c1
            if mode == 's':
                carrow, cframe = c2, c3


            draw.rectangle((0,0,im.width,im.height),fill=bkg)
            dirs = {}
            r = int(1+1.1*(1+0.13)*s)  # radius of interaction
            for ad in (('u',(xc,y0,90)),('d',(xc,y1,-90)),('l',(x0,yc,180)),('r',(x1,yc,0)),
                       ('ul',(x0,y0,135)),('ur',(x1,y0,45)),('dl',(x0,y1,-135)),('dr',(x1,y1,-45)),('s',(xc,yc,0))):
                       
                xx,yy,_ = ad[1]

                def proj(xx,yy):
                    x = int(.5+xx/1280 * 720)
                    y = int(.5+yy/720 * 480)
                    y = (y//2)*2 # ensure even
                    return (x,y)
                x,y = proj(xx, yy)
                
                if ad[0] in choices and ad[0] != 's':
                    # use a thinner frame in normal case since it
                    #   may be superimposed on background image
                    #   which widens its size due to compression.
                    exp = None if mode != 'n' else 0.09
                    
                    draw_arrow(*ad[1], scale=s, exp=exp, c_arrow=carrow, c_frame=cframe)

                    if star_cheat is not None:
                        if star_cheat[choices.index(ad[0])] == '1':
                            draw_marker_star(*ad[1], scale=s)
                    
                    # store bounding box
                    # ensure even y-coordinates
                    dirs[ad[0]] = [*proj(xx-r,yy-r), *proj(xx+r,yy+r)]
                if ad[0] in choices and ad[0] == 's':
                    if modification is not None:
                        if mode != 'n':
                            # draw a circle
                            circle =list(make_star_path(n_arms=36, r_inner=1))
                            circle.append(circle[0])
                            circle = np.array(circle)
                            
                            pcirc = i(trans(2*s*1.2*circle,(xc,yc)))

                            col = c1 if mode == 'h' else c3

                            draw.line(pcirc, fill=col, width=int(.5+s*0.25))

                        R = 2*s*1.2 + 0.5+s*0.25 + 5
                        if modification == 'star':
                            pstar = i(trans(2*s*1.1*star,(xc,yc)))
                            draw.polygon(pstar, fill=c1)
                            
                            pstar = i(trans(2*s*star,(xc,yc)))
                            draw.polygon(pstar, fill=c2)
                        elif modification == 'smiley':
                            draw_smiley(xc, yc, R/1.5)
                        
                        dirs['s'] = [*proj(xx-R,yy-R), *proj(xx+R,yy+R)]
                                
            im2 = im.resize(screen, resample=False)
            arrs = '-'.join(dirs.keys())
            fn = f'men_{ar}{mod_tag}_{"-".join(choices)}{sc_tag}_{mode}.png'

            fns[mode] = f'menu-data/{fn}'
            im2.save(fns[mode],format='PNG')
            if mode == 'n':
                im.save(f'./menu-data/full_{fn}',format='PNG')
        
        buttons = []
        for but in choices:  # this ensures button 0 will be UP and default selected if it exists
            (xx0,yy0,xx1,yy1) = dirs[but]
            ct = []
            for key, targets in selections[but].items():
                for target in targets:
                    if target in dirs:
                        break
                else:
                    # there is no arrow control the 'key' button
                    #   could lead to
                    continue
                ct.append(f'{key}="{target}"')
            ctrl = ' '.join(ct)
            buttons.append('           '+f"""
            <button name="{but}" x0="{xx0}" y0="{yy0}" x1="{xx1}"
                    y1="{yy1}" {ctrl} />
            """.strip())
        button_str = '\n'.join(buttons)
        fn_n = fn_transparent # dummy slide since 'n' is placed directly onto the image
        xml = f"""
    <subpictures format="{screen_format}">
       <stream>
          <spu start="0" image="{fn_n}"
               highlight="{fns['h']}" select="{fns['s']}"
               force="yes">
    {button_str}
          </spu>
       </stream>
    </subpictures>""".strip()
        
        with open(f'./menu-data/spu_{ar}{mod_tag}_{"-".join(choices)}{sc_tag}.xml','w') as f:
            f.write(xml)

if __name__ == '__main__':
    with open('01_video_sources.txt') as f:
        lines = f.read().strip().split('\n')
    # make sure we generate each layout only once
    patterns = set([])
    for line in lines:
        if not line.startswith('m'): continue
        patterns.add(line.split('\t')[2])
    for pattern in sorted(patterns):
        print(pattern)
        make_files(pattern)
        if '-star' not in pattern:
            pattern2 = pattern + '-star'
            print(pattern2)
            make_files(pattern2)
        if '-smiley' not in pattern:
            pattern2 = pattern + '-smiley'
            print(pattern2)
            make_files(pattern2)
