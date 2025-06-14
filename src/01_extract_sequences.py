import os, glob, json

path_out = os.path.join('.','stills')
try: os.mkdir(path_out)
except: pass

path_in = os.path.join('.','movies-org')

# (i): at intersection - looking from intersection - leaving toward intersection
# (k): from intersection - to intersection

sequences = """
pt3.mp4
4-15.6 i3-4-5 .
25-38 i3-5-4 .
44-50 i3-4-4 .
58-1:06.2 i3-4-2 .
1:13-1:21 i3-2-4 .
1:40-1:44 i3-2-2 .
1:55-2:06.6 i3-2-5 .
2:12-2:18 i3-5-5 .
2:23-2:37.6 i3-5-2 .

pt2-a.mp4
1-6 i2-1-3 .
6-19 k2-3  .
33.4-44.4 k3-2 .
48-53 i2-3-1 .
48-53 i2-13-1 .
56-1:01 i1-2-2 .
1:04-1:10 i2-1-6 *.
1:10-1:19 i6-2-5 .*

pt2-b.mp4
3-7.2 i2-6-3 .
20-24 i2-3-6 .
20-24 i2-13-6 .
33-37 i2-6-1 .

pt2-c.mp4
2-5.6 i2-3-3 .
2-5.6 i2-13-3 .
24-29 i2-6-6 .

pt1-a.mp4
3.2-9 i2-1-1 .

pt5-a.mp4
2-12 i5-3-4 .
21-33 i5-4-6 .
42-52 i5-6-3 .

pt5-b.mp4
3-8 i5-3-3 .
14-24.2 i5-3-6 .
32.6-37 i5-6-6 .
43.6-57 i5-6-4 .
1:05-1:10 i5-4-4 .
1:18-1:31 i5-4-3 .

pt6-a.mp4
3-13 i6-9-2 *.
19-30 i6-2-5 .
38.5-43.4 i6-5-9 *.
44-52.2 k6-9 .*
56.8-1:10 k9-7 .*

pt6-b.mp4
2.4-8.5 i6-9-5 .
19-27 i6-5-2 .
33-42 i6-2-9 .
48-58.2 i6-9-2 .
1:03-1:12 i6-2-5 .
1:17-1:25 i6-5-9 .

pt6-c.mp4
3.4-6.4 i6-9-9 .
27.4-33 i6-2-2 .
50.2-55 i6-5-5 . # finger briefly in view

pt7-a.mp4
3-11 i7-9-8 .
11-22 k7-8 .
28-46 i8-7-7 . # includes proper link 32-46 k8-7
48-51 i7-8-4 .
1:03.2-1:10 i7-4-9 .
1:20.4-1:24 i7-9-9 .
1:31-1:39 i7-9-4 .
1:49-1:51 i7-4-4 .
2:02-2:05 i7-4-8 .
2:21-2:24.2 i7-8-8 .

pt7-b.mp4
8-20.5 k7-9 .

pt7-c.mp4
4-12 i7-8-9 .

pt8-b.mp4
2.6-7 i8-7-4 .
7-27 k8-4 .

pt8-c.mp4
4-20 i8-4-7 . # includes proper link k8-7

pt8-d.mp4
3-6 i8-4-4 .

pt4-a.mp4
1-13 i4-3-8 .
20-30.5 i4-8-3 .

pt4-b.mp4
1-17 i4-3-7 *.
30-44.5 i4-7-3 .

pt4-c.mp4
1-12 i4-3-8 *.
18-30 i4-8-7 .
37-50 i4-7-5 .
1:05-1:14 i4-5-3 .

pt4-d.mp4
2-6 i4-3-3 *.

pt4-e.mp4
2-7 i4-3-3 . # not ckecked
13-22 i4-3-5 .
36-43 i4-5-5 .
48-1:02 i4-5-7 .
1:10-1:18 i4-7-7 .

pt4-f.mp4
1-14.5 i4-7-3 *.    # <-- use this
22-36 i4-3-7 .

pt4-g.mp4
2-12.6 i4-8-5 .
19-31 i4-5-8 .

pt4-h.mp4
10-23 k4-3 .

pt4-i.mp4 # night
3.4-17 k3-4 .

pt4-j.mp4 # night
2-14 i4-7-8 .
14-42 k4-8 .

pt4-k.mp4 # night
2-8 i4-8-8 .

pt9-a.mp4
2.5-10 i9-6-7 . # needs a custom link to 7

pt9-b.mp4
3-13 i9-7-10 .
3-13 i9-11-10 .

pt9-d.mp4
2-17 i9-10-6 .

pt9-e.mp4
2.8-9.5 i9-6-10 .

pt9-f.mp4
2.5-12.7 i9-10-7 . # needs a custom link to 7

pt9-g.mp4
3-21 i9-7-11 .
3-21 i9-11-11 .

pt9-h.mp4
3.3-6.4 i9-10-10 .

pt9-i.mp4
2.5-13.2 i9-6-6 .

pt9-j.mp4
3.2-7.7 i9-7-7 .* # needs a link
3.2-7.7 i9-11-7 .* # needs a link

pt9-k.mp4
2.5-19 i9-7-7 . # includes the link, not checked since the others need a link
2.5-19 i9-11-7 . # includes the link

pt9-l.mp4
2.5-6 i9-10-10 . # not checked

pt9-m.mp4
2-13 k6-9 . # not processed, using crop of old k6-7 instead

pt9-n.mp4
2-15 i9-7-6 .
2-15 i9-11-6 .

pt10-a.mp4
3.5-10 i10-9-12 .

pt10-b.mp4
4-16.2 i10-12-11 .

pt10-c.mp4
3-13.5 i10-9-11 .

pt10-d.mp4
3.8-5.5 i10-12-12 .

pt10-e.mp4
2-8 i10-9-9 . # not used, has fig 8 start

pt10-f.mp4
3.5-32 i10-9-13 .X # includes Link

pt10-h.mp4
2.8-27.5 i10-12-13 .X # includes link
10-27.5 k10-13 . # only to be used by i10-13-13

pt10-i.mp4
3-6 i10-13-12 .

pt10-j.mp4
3.5-9 i10-13-13 . # needs a link

pt10-k.mp4
2-8.5 i10-13-9 .

pt10-l.mp4
4-17 i10-13-11 .

pt10-m.mp4
1.7-6.2 i10-9-9 *.

pt10-n.mp4
2-8 i10-12-9 .

pt11-a.mp4
3-23.5 i11-9-9 .  # has hand in view, final fov not so nice, slower than -b
3-23.5 i11-10-9 .

pt11-b.mp4
2.5-18.5 i11-9-9 .*
2.5-18.5 i11-10-9 .*

pt12-a.mp4
3-8 i12-10-10 .

pt13-a.mp4
2.7-26 i13-10-10 .

pt13-b.mp4
3.2-14 i13-10-2 .

pt13-c.mp4
2-11 i2-3-13 .
2-11 i2-13-13 .

pt13-d.mp4
2.8-23 i13-2-10 . # there is something odd here

pt13-e.mp4
3.2-15 i2-6-13 *.

pt13-f.mp4
1.5-12 i2-1-13 .

pt13-g.mp4
3-14 i2-6-13 . # could also work

pt13-h.mp4
2.8-12 i13-2-2 .

pt14-b.mp4
#6-11 i14-15-3 . # not used
13-13.5 i3-14-0 . # I forgot to record the connectors i3-14-x

pt3-b.mp4
2.5-10 i3-2-14 .

pt3-c.mp4
5-16 i3-5-14 .

pt3-d.mp4
4-9 i3-4-14 *.

pt3-e.mp4
2.5-9.7 i3-4-14 . # poor starting position and slow movement

pt3-f.mp4
3-6 i3-14-14 .

pt3-g.mp4
2.5-23 i3-14-2 .X # includes link

pt3-h.mp4
3.7-14 i3-14-5 .

pt14-d.mp4
7.3-10 i14-3-3 .
16.5-21 i3-14-4 .

""".strip()

def get_sec(txt):
    def check(x):
        return int(x) if int(x) == float(x) else float(x)
        
    
    if ':' in txt:
        mins, secs = txt.split(':')
        return check(float(secs) + 60*int(mins))
    return check(float(txt))


seq = {}
not_processed = {}
fn = None
for line_idx, line in enumerate(sequences.split('\n')):
    line = line.split('#',1)[0].strip()
    if not len(line): continue
    if '.mp4' in line:
        # start of new file
        fn = line
        continue
    if line[0] in '0123456789':
        val = line.split()
        if len(val) not in (2,3):
            raise ValueError('Cannot parse line', line_idx+1, line)
        if len(val) == 3 and any(c not in '.*X' for c in val[2].strip()):
            raise ValueError('Cannot parse line', line_idx+1, line)
        
        start, end = get_sec(val[0].split('-')[0]), get_sec(val[0].split('-')[1])
        name = val[1]
        try:
            preferred = '*' in val[2]
        except:
            preferred = False

        try:
            processed = '.' in val[2]
        except:
            processed = False
        if len(val) == 2: val.append('') # no flags given

        flags = '*' if preferred else ''
        flags += 'X' if 'X' in val[2] else '' # do not attach link even if it exists
        
        if name not in seq: seq[name] = []
        seq[name].append((fn, start, end, flags))
        
        if not processed:
            if name not in not_processed: not_processed[name] = []
            not_processed[name].append((fn, start, end, preferred))
            

for key in seq.keys():
    if len(seq[key]) > 1:
        for idx in range(len(seq[key])):
            if '*' in seq[key][idx][3]:
                preferred_idx = idx
                break
        else:
            preferred_idx = 0
            # nothing preferred
        seq[key] = [seq[key][preferred_idx]] + seq[key][:preferred_idx] + seq[key][preferred_idx+1:]

def keysortcode(key):
    def char(code):
        code = int(code)
        assert code >= 0
        if 0<=code <=9: return str(code)
        return chr(ord('a')+code-10)

    return key[0] + ''.join([char(num) for num in key[1:].split('-')])
    

if False:
    for key in sorted(seq.keys(), key=lambda x: keysortcode(x)):
        print(key, seq[key])
else:
    print('UNPROCESSED')
    for key in sorted(not_processed.keys(), key=lambda x: keysortcode(x)):
        print(key, not_processed[key])

with open('01_sequence_options.json','w') as f:
    json.dump({key:seq[key] for key in sorted(seq.keys(), key=lambda x: keysortcode(x))}, f)

if False:
    # extract stills of initial image
    out = []
    for key in sorted(seq.keys(), key=lambda x: keysortcode(x)):
        for idx, (fn_in, start, end, preferred) in enumerate(seq[key]):
            if len(seq[key]) == 1 or preferred:
                pref = '1'
            else:
                # secondary or as yet undecided
                pref = '0'

            index = chr(ord('a') + idx)
            if not key.startswith('i'): continue
            #fn_out = os.path.join(path_out,f'start_{key}_{index}.jpg')
            tag = os.path.basename(fn_in).rsplit('.',1)[0]+f'@{start}'
            fn_out = os.path.join(path_out,f'start_{key}_{pref}_{tag}.jpg')
            fn = os.path.join(path_in, fn_in)
            cmd = f'ffmpeg -y -ss {start} -i {fn} -frames:v 1 -q:v 2 {fn_out}'
            out.append(cmd)
    with open('01_make-start-stills.bat','w') as f:
        f.write('\n'.join(out))
    print('written .bat file for stills')


views = {
    '1-2': ('start_i1-2-2_1_pt2-a@55.jpg','d2'),
    '2-1': ('start_i2-1-6_1_pt2-a@63.jpg','l6-ur3-dr13-d1'),
    '2-3': ('start_i2-3-6_1_pt2-b@17.jpg','l1-u6-d3-dl13'),
    '2-6': ('start_i2-6-1_1_pt2-b@32.jpg','ur13-l3-r1-d6'),
    '2-13':('start_i2-3-6_1_pt2-b@17.jpg','l1-u6-dr3-d13'),
    '3-2': ('start_i3-2-5_1_pt3@113.jpg','u4-ur14-l5-d2'),
    '3-4': ('start_i3-4-5_1_pt3@1.jpg','u2-l14-r5-d4'),
    '3-5': ('start_i3-5-2_1_pt3@143.jpg','u14-l4-r2-d5'),
    '3-14':('start_i3-14-4_1_pt14-d@14.5.jpg','u5-r4-l2-d14'),
    '4-3': ('start_i4-3-5_1_pt4-e@13.jpg','u7-l5-r8-d3'),
    '4-5': ('start_i4-5-8_1_pt4-g@19.jpg','u8-l7-r3-d5'),
    '4-7': ('start_i4-7-3_1_pt4-f@1.jpg','u3-l8-ur5-d7'),
    '4-8': ('start_i4-8-5_1_pt4-g@1.jpg','ul5-l3-r7-d8'),
    '5-3': ('start_i5-3-6_1_pt5-b@13.jpg','l6-r4-d3'),
    '5-4': ('start_i5-4-4_1_pt5-b@64.jpg','u6-l3-d4'),
    '5-6': ('start_i5-6-4_1_pt5-b@42.jpg','u4-r3-d6'),
    '6-2': ('start_i6-2-5_0_pt2-a@70.jpg','l9-r5-d2'),
    '6-5': ('start_i6-5-7_0_pt6-a@37.jpg', 'ur9-l2-d5'),
    '6-9': ('start_i6-7-5_1_pt6-b@1.jpg','ul5-ur2-d9'),
    '7-4': ('start_i7-4-4_1_pt7-a@108.jpg','ul9-dr8-d4'),
    '7-9': ('start_i7-6-4_1_pt7-a@90.jpg','ur4-l8-d9'),
    '7-8': ('start_i7-8-4_1_pt7-a@47.jpg','l4-ur9-d8'),
    '8-4': ('start_i8-4-7_1_pt8-c@3.jpg','l7-d4'),
    '8-7': ('start_i8-7-4_1_pt8-b@1.jpg','r4-d7'),
    '9-6': ('start_i9-6-10_1_pt9-e@2.5.jpg','u7-l10-d6'),
    '9-7': ('start_i9-7-11_1_pt9-g@2.5.jpg','ul6-u10-r11-d7'),
    '9-10': ('start_i9-10-7_1_pt9-f@2.5.jpg','ur6-ul7-d10'),
    '9-11': ('start_i9-11-11_1_pt9-g@2.5.jpg','ul6-u10-dl7-d11'),  # different button layout as 9-7 to have "down" go back to where we came from
    '10-9': ('start_i10-9-12_1_pt10-a@2.5.jpg','ul13-l12-r11-d9'), # maybe better: u13-ul12-r11-d9
    '10-12': ('start_i10-12-13_1_pt10-h@1.5.jpg','l11-u9-dl13-d12'),
    '10-13': ('start_i10-13-9_1_pt10-k@2.jpg','l11-u9-r12-d13'),
    '11-9': ('start_i11-9-9_0_pt11-b@2.5.jpg','u9'),  # same as 11-10
    '11-10': ('start_i11-10-9_0_pt11-b@2.5.jpg','u9'),
    '12-10': ('start_i12-10-10_1_pt12-a@2.jpg','d10'),
    '13-2': ('start_i13-2-10_1_pt13-d@1.5.jpg','u10-d2'),
    '13-10': ('start_i13-10-2_1_pt13-b@2.2.jpg','u2-d10'),
    '14-3': ('start_i14-3-3_1_pt14-d@7.jpg','d3'),
    #'14-15': ('start_i14-15-3_1_pt14-b@6.jpg','r3'),
    }

if False:
    import shutil
    try: os.mkdir('./views')
    except: pass
    for view, (src,_) in views.items():
        fn_view = f'view_{view}.jpg'
        shutil.copy2(os.path.join('stills',src), os.path.join('views',fn_view))

if False:
    # test patch the segments so we can adjust the timining of individual
    #   segments to optimize time limits
    import subprocess
    # render
    for key in sorted(seq.keys()):
        if key != 'i3-14-14': continue
        for idx, (fn_in, start, end, flags) in enumerate(seq[key]):
            if idx == 0:   # or 1, or 2 if there are multiple options for a sequence
                break
        else:
            raise ValueError('did not find index requested')
        break
    at, arr, dep = key[1:].split('-')    
    
    ckey = f'k{at}-{dep}'
    if ckey in seq.keys():
        fn_link, start_link, end_link, _ = seq[ckey][0]
    else:
        fn_link, start_link, end_link = None, None, None

    if fn_link is not None and not 'X' in flags:
        fn_link = os.path.join(path_in, fn_link)
    else:
        fn_link = None
    fn_in = os.path.join(path_in, fn_in)

    fn_init = 'stills\\'+views[key[1:].rsplit('-',1)[0]][0]
    fn_final = 'stills\\'+views['-'.join(key[1:].rsplit('-')[2::-2])][0]
    dt_still = 1
    fr = 30 # input frame rate (defaults to 25), should be the same as .mp4 (note that some .mp4 may report 30.02, that needs to be corrected)
    dt_off = 0.5*(1/fr)
    # 2s initial still
    # ix-y-z
    # kx-z if exists
    # 2s final still

    # NB: double the audio source with [0]asplit=3[s1][s2][s3];  https://stackoverflow.com/questions/38611059/how-to-add-additional-5-seconds-duration-time-to-wav-file-using-ffmpeg-in-c-shar
    
    args = ['ffmpeg','-y']
    args += ['-f','lavfi','-t',f'{dt_still}','-i','anullsrc=channel_layout=stereo:sample_rate=48000'] # silent audio
    args += ['-loop','1','-t',f'{dt_still}','-framerate',str(fr),'-i',fn_init]

    dt = round(dt_off + end-start,3) # we get errors in 1e-16s frequently
    # NB: some videos log a framerate of 30.02, which means we have to -vsync vfr at the end to clean this up.
    #    since we know we've shot 30fps videos, we override the framerate detection with -r so everything is in sync
    args += ['-ss', str(start), '-t', str(dt),'-r',str(fr), '-i', fn_in]
    if fn_link is not None:
        dt_link = round(dt_off + end_link-start_link,3) # we get errors in 1e-16s frequently
        # NB: some videos log a framerate of 30.02, which means we have to -vsync vfr at the end to clean this up.
        #    since we know we've shot 30fps videos, we override the framerate detection with -r so everything is in sync
        args += ['-ss', str(start_link), '-t', str(dt_link),'-r',str(fr), '-i', fn_link]
    args += ['-f','lavfi','-t',f'{dt_still}','-i','anullsrc=channel_layout=stereo:sample_rate=48000'] # silent audio
    args += ['-loop','1','-t',f'{dt_still}','-framerate',str(fr),'-i',fn_final]

    if fn_link is None:
        args += ['-filter_complex', '[1:v][0:a][2:v][2:a][4:v][3:a]concat=n=3:v=1:a=1']
    else:
        f_scale = ';'.join(f'[{i}:v]scale=320:-1[v{i}]' for i in (1,2,3,5))

        args += ['-filter_complex', f_scale+';'+'[v1][0:a][v2][2:a][v3][3:a][v5][4:a]concat=n=4:v=1:a=1']

    args +=['-aspect','16:9','-target','ntsc-dvd']  # we need to output this at NTSC frame rate since the reduction from 30 to 25 fps gives jerky motion
    args += ['01_out.mpg']

    print(' '.join(args))

    r = subprocess.run(args,capture_output=True)
    print(str(r.stderr, encoding='utf-8'))

# note recording with different frame rate
# i3-4-4 (day): Video: h264 (High) (avc1 / 0x31637661), yuv420p(tv, bt709), 1280x720, 9833 kb/s, 30 fps, 30 tbr, 90k tbn, 180k tbc
# k3-4 (night): Video: h264 (High) (avc1 / 0x31637661), yuv420p(tv, bt709), 1280x720, 11387 kb/s, 30.02 fps, 120 tbr, 90k tbn, 180k tbc (default)

# fps: average frame rate = total frames / total seconds. A variable frame rate video may have an fps of 57.16
# tbr: user-friendly, target frame rate. The same variable frame rate video above could have a tbr of 60.

def button_pattern_layout(button_pattern):
    # make standardized layout
    def clean(name):
        s=''
        for c in name:
            if c in '0123456789': break
            s += c
        if len(s) == 0:
            raise ValueError('Received Empty Button Name', button_pattern)
        return s
    choices = sorted([clean(b) for b in button_pattern.split('-')], key=lambda x:(
        'ud'.index(x[0])*10 if x[0]!=x[-1] else 0 + 'ulrd'.index(x[-1]))) # sort u l r d ul ur dl dr

    return '-'.join(choices)

        
if True:
    # output main result of this script
    out = []
    # mx-y: at-from menu-link information
    # sequences of ix-y-z: src file and timing
    # sequences of kx-z: src file and timing
    for view, (_,lnk) in views.items():
        layout = button_pattern_layout(lnk)
        out.append(f'm{view}\t{lnk}\t{layout}')
    
    for key in sorted(seq.keys(), key=lambda x: keysortcode(x)):
        for idx, (fn_in, start, end, flags) in enumerate(seq[key]):
            out_flags = []
            if 'X' in flags: out_flags.append('ignoreLink') # do not use link even if link exists
            if True or '*' in flags or len(seq[key]) == 1:
                # actually, if there is a '*' then this is listed in
                #  first position, i.e. always use first position
                break
        else:
            raise ValueError(f'Intersection {key} not uniquely defined.')
        out.append(f'{key}\t{os.path.basename(fn_in)}\t{round(start,3)}\t{round(end,3)}\t{",".join(out_flags)}')

    print('\n'.join(out))
    fn_vs = '01_video_sources.txt'
    with open(fn_vs,'w') as f:
        f.write('\n'.join(out))
    print('written', fn_vs)
