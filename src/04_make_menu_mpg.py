#!/usr/bin/env python3

import os
import subprocess

make_special = True
only_special = not False
make_views = False # make short clips of each view into an intersection

path_final = 'dvd-mpg' # used for disclaimer
try: os.mkdir(path_final)
except: pass

path_out = 'menu-data'
try: os.mkdir(path_out)
except: pass

# force linux convention
def a(*args):
    return '/'.join(args)
os.path.join = a


with open('01_video_sources.txt') as f:
    lines = f.read().strip().split('\n')

views = {}
for line in lines:
    if line.startswith('m'):
        view, _, pattern = line.split('\t')
        views[view[1:]] = pattern

with_star = True

framerate = 30 # consistent with .mp4 from camera

def get_patterns(pattern):
    out = []
    N = len(pattern.split('-'))
    for i in range(2**N):
        binary = bin(i).split('0b')[1]
        binary = '0' * (N-len(binary)) + binary
        out.append(binary[-1::-1])
    return out

if True:
    commands = []
    # convert menu stills to mpg with buttons
    length = 0.2
    disclaimer_length = 3
    args0 = f'ffmpeg -y -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000 -loop 1 -framerate {framerate}'.split()
    # ffmpeg will round up the duration, no need to add to this manually...
    args1 = f'-t {round(length, 3)} -filter_complex [1][2]overlay=x=0:y=0 -aspect 16:9 -target ntsc-dvd'.split()
    args1_simple_still_long = f'-t {round(disclaimer_length, 3)} -aspect 16:9 -target ntsc-dvd'.split()
    args1_simple_still_short = f'-t {round(length, 3)} -aspect 16:9 -target ntsc-dvd'.split()
    for view, pattern in views.items():
        #if int(view.split('-')[0]) >= 3: continue
        for star in ('', 'star','smiley'):
            if star and not with_star: continue
            stag = '_star' if star == 'star' else '_smiley' if star == 'smiley' else ''
            spat = '-s' if star != '' else ''
            if len(star):
                star_pats = [None]
            else:
                star_pats = get_patterns(pattern)
            for star_pat in star_pats:
                selector = f'_spos{star_pat}' if star_pat is not None else ''
                
                fn_still = os.path.join('views',f'view_{view}.jpg')
                fn_buttons = os.path.join('menu-data', f'full_men_169{stag}_{pattern}{spat}{selector}_n.png')
                fn_out = os.path.join(path_out, f'frame_{view}{stag}{selector}.mpg')
                args = args0 + ['-i', fn_still, '-i', fn_buttons] + args1 + [fn_out]
                commands.append(args)
    if make_views:
        for key in sorted(views.keys()):
            fn_still = os.path.join('views',f'view_{key}.jpg')
            fn_out = os.path.join(path_final, f'view_{key}.mpg')
            args = args0 + ['-i', fn_still] + args1_simple_still_short + [fn_out]
            commands.append(args)
            
    if make_special:
        if only_special: commands = []
        for tag in ('main',):
            fn_still = os.path.join('views',f'view_{tag}.jpg')
            fn_buttons = os.path.join('menu-data', f'full_men_169_{tag}_n.png')
            fn_out = os.path.join(path_out, f'frame_{tag}.mpg')
            args = args0 + ['-i', fn_still, '-i', fn_buttons] + args1 + [fn_out]
            commands.append(args)
            
        for tag in ('toggle',):
            fn_still = os.path.join('views',f'view_{tag}.jpg')
            fn_out = os.path.join(path_out, f'frame_{tag}.mpg')
            args = args0 + ['-i', fn_still] + args1_simple_still_short + [fn_out]
            commands.append(args)
            
        for tag in ('disclaimer',):
            fn_still = os.path.join('views',f'view_{tag}.jpg')
            fn_out = os.path.join(path_final, f'menu_{tag}.mpg')
            args = args0 + ['-i', fn_still] + args1_simple_still_long + [fn_out]
            commands.append(args)

    for idx, command in enumerate(commands):
        print(idx+1, '/', len(commands))
        print(' '.join(command))
        r = subprocess.run(command,capture_output=True)
        print(str(r.stderr, encoding='utf-8'))

if True:
    out = []
    out.append('#!/usr/bin/bash')
    for view, pattern in views.items():
        for star in ('', 'star','smiley'):
            if star and not with_star: continue
            stag = '_star' if star == 'star' else '_smiley' if star == 'smiley' else ''
            spat = '-s' if star != '' else ''

            if star:
                star_pats = [None]
            else:
                star_pats = get_patterns(pattern)
            for star_pat in star_pats:
                selector = f'_spos{star_pat}' if star_pat is not None else ''

                fn_xml = os.path.join(path_out,f'spu_169{stag}_{pattern}{spat}{selector}.xml')
                fn_from = os.path.join(path_out,f'frame_{view}{stag}{selector}.mpg')
                fn_to = os.path.join('./dvd-mpg',f'menu_{view}{stag}{selector}.mpg')
                cmd = f'spumux -v 5 {fn_xml} < {fn_from} > {fn_to}'
                out.append(f'echo "{cmd}"')
                out.append(cmd)
    if make_special:
        if only_special:
            out = []
            out.append('#!/usr/bin/bash')
        for tag in ('main','toggle'):
            fn_xml = os.path.join(path_out,f'spu_169_{tag}.xml')
            fn_from = os.path.join(path_out,f'frame_{tag}.mpg')
            fn_to = os.path.join('./dvd-mpg',f'menu_{tag}.mpg')
            cmd = f'spumux -v 5 {fn_xml} < {fn_from} > {fn_to}'
            out.append(f'echo "{cmd}"')
            out.append(cmd)
    with open('04_make_menu.sh','bw') as f:
        # write this as binary to force \n rather than \r\n
        f.write(('\n'.join(out)).encode('utf-8'))
        
    print('written bash file')
    
