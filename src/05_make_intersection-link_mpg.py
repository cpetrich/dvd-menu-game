import os, shutil
import subprocess

if False:
    from fontTools.ttLib import TTFont
    import glob

    char = 0x23cf # eject. seguiemj.ttf, seguisym.ttf
    char = 0x1F929 # smiley with star eyes. seguiemj.ttf
    
    print("Looking for U+%X (%c)" % (char, chr(char)))

    args = glob.glob('c:\\windows\\Fonts\\*.ttf')
    for arg in args:
        try:
            font = TTFont(arg)

            for cmap in font['cmap'].tables:
                if cmap.isUnicode():
                    if char in cmap.cmap:
                        print("Found in", arg)
                        break
        except Exception as e:
            print("Failed to read", arg)
            print(e)
    sdfsdf # stop here

path_out = 'dvd-mpg'

path_in_video = 'movies-org'
try: os.mkdir(path_out)
except: pass

with open('01_video_sources.txt') as f:
    lines = f.read().strip().split('\n')

eject_disc_text = None # no text, just the icon on error page
eject_disc_text = 'Eject Disc' # text in English.

framerate = 30
ntsc_fr = 30*1000/1001

total_duration = 0
clips = {}
for line in lines:
    if line.startswith('i') or line.startswith('k'):
        key, fn, start, end = line.split('\t')[:4]
        if len(line.split('\t')) >= 5:
            flags_str = line.split('\t')[4]
        else:
            flags_str = ''
        flags = flags_str.split(',')
        duration = round(float(end)-float(start),3)
        clips[key] = [fn, float(start), duration, flags]
        total_duration += duration
print(f'Total Duration: {round(total_duration,3)} s')

if False:
    # make 10ms long blank to separate chapters (obsolete):
    args='ffmpeg -y -f lavfi -i color=c=black:s=720x480:r=30000/1001 -f lavfi -i anullsrc=cl=mono:r=48000 -t 0.01 -aspect 16:9 -target ntsc-dvd'.split()
    args += [os.path.join(path_out,'screen_blank-10ms.mpg')]
    print(' '.join(args))
    r = subprocess.run(args, capture_output=True)
    print(str(r.stderr, encoding='utf-8'))

    # make black separator:
    args='ffmpeg -y -f lavfi -i color=c=black:s=720x480:r=30000/1001 -f lavfi -i anullsrc=cl=mono:r=48000 -t 0.2 -aspect 16:9 -target ntsc-dvd'.split()
    args += [os.path.join(path_out,'screen_black.mpg')]
    print(' '.join(args))
    r = subprocess.run(args, capture_output=True)
    print(str(r.stderr, encoding='utf-8'))

if False:
    #make blue screen of death:
    period_s = 4
    # this adds an eject symbol
    # we need to put non-ascii characters into a separate text file
    with open('c:\\temp\\textfile.txt','w',encoding='utf-8') as f:
        f.write('\u23CF')
    if False:
        # just show the eject sign
        args = 'ffmpeg -y -f lavfi -i color=c=blue:s=720x480:r=30000/1001 -f lavfi -i anullsrc=cl=mono:r=48000 -t 2 -vf drawtext=fontfile=/windows/Fonts/seguisym.ttf:textfile=/temp/textfile.txt:fontcolor=white:fontsize=96:x=(w-text_w)/2:y=(h-text_h)/2 -aspect 16:9 -target ntsc-dvd'.split()
    else:
        # show the eject sign, potentially with text in the line below
        args = f'ffmpeg -y -f lavfi -i color=c=blue:s=720x480:r=30000/1001 -f lavfi -i anullsrc=cl=mono:r=48000 -t {period_s}'.split()
        draw_cmd = '''drawtext=fontfile='/windows/Fonts/seguisym.ttf':textfile='/temp/textfile.txt':fontcolor=white:fontsize=96:x=(w-text_w)/2:y=(h-text_h)/2'''
        if eject_disc_text is not None:
            draw_cmd += f''',drawtext=fontfile='/windows/Fonts/verdana.ttf':text='{eject_disc_text}':fontcolor=white:fontsize=32:x=(w-text_w)/2:y=72+(h-text_h)/2'''

        args += ['-vf', f'[in]{draw_cmd}[out]']
        args += '-aspect 16:9 -target ntsc-dvd'.split()
    args += [os.path.join(path_out,'screen_blue.mpg')]
    print(' '.join(args))
    r = subprocess.run(args, capture_output=True)
    print(str(r.stderr, encoding='utf-8'))



if True:
    # make fading copyright notification and possibly dedication
    # by alpha-blending the text

    text0 = '\n'.join(line.strip() for line in f"""
    This work is copyright \u00a9 Christian Petrich, 2023
    Permission is granted to share, reproduce, and modify
    this work under the Creative Commons CC BY 4.0 License.
    The full license text is available at
    https://creativecommons.org/licenses/by/4.0/legalcode
    """.strip().split('\n'))

    text1 = 'dedication line with emojis'
    text2 = 'dedication line text'

    pages = []
    pages.append({'delay':0.2, 'fade-in': 1, 'show': 3, 'fade-out':1})
    pages.append({'delay':0.5})

    content = []
    content.append({'layout': 1, 'fs0': 18, 'text0': text0})
    content.append({}) # blank page

    # write text content to disk in case it contains non-ASCII characters
    fn_cnt = 0
    for idx, c in enumerate(content):
        if 'layout' not in c:
            # this page is empty
            continue
        for part in range(c['layout']):
            fn_cnt += 1
            fn_disk = f'c:\\temp\\textfile{fn_cnt}.txt'
            fn_ref = f'/temp/textfile{fn_cnt}.txt'
            content[idx][f'fn{part}'] = fn_ref
            with open(fn_disk,'w',encoding='utf-8') as f:
                f.write(c['text'+str(part)])
        if c['layout'] == 1:
            content[idx]['font0'] = '/windows/Fonts/verdana.ttf'
        elif c['layout'] == 2:
            content[idx]['font0'] = '/windows/Fonts/seguisym.ttf'
            content[idx]['font1'] = '/windows/Fonts/verdana.ttf'            

    t0 = 0
    for idx, p in enumerate(pages):
        for key in ('delay', 'show', 'fade-in', 'fade-out'):
            if key not in pages[idx]: pages[idx][key] = 0
        fake_fade_in = p["fade-in"] if p["fade-in"] > 0 else 1
        fake_fade_out = p["fade-out"] if p["fade-out"] > 0 else 1
        pages[idx]['start'] = t0
        pages[idx]['alpha'] = ''.join([
            f'if(lt(t,{t0+p["delay"]}),0,',
            f'if(lt(t,{t0+p["delay"]+p["fade-in"]}),(t-{t0+p["delay"]})/{fake_fade_in},',
            f'if(lt(t,{t0+p["delay"]+p["fade-in"]+p["show"]}),1,',
            f'if(lt(t,{t0+p["delay"]+p["fade-in"]+p["show"]+p["fade-out"]}),1-(t-{t0+p["delay"]+p["fade-in"]+p["show"]})/{fake_fade_out},0',
            '))))'])
        t0 = t0+p.get("delay",0)+p.get("fade-in",0)+p.get("show",0)+p.get("fade-out",0)
        pages[idx]['end'] = t0
        
    draw_cmd = []
    draw_cmd.append('setpts=N/FRAME_RATE/TB')
    for p, c in zip(pages, content):
        if 'layout' not in c:
            # this is a blank page, no need to emit commands
            continue
        for idx in range(c['layout']):
            x = '(w-text_w)/2'
            y = '(h-text_h)/2'
            if (c['layout'] == 2):
                if idx == 0:
                    y = '0.15*h'
                else:
                    y = f'0.15*h+{c["fs0"]+c["fs1"]}'
            draw_cmd.append(f'''drawtext=fontfile='{c["font"+str(idx)]}':textfile='{c["fn"+str(idx)]}':line_spacing={-c["fs"+str(idx)]//2}:fontcolor=white:fontsize={c["fs"+str(idx)]}:x={x}:y={y}:alpha='{p["alpha"]}':enable='between(t,{p["start"]},{p["end"]})' '''.strip())

    # NTSC is 720x480 but anamorphic, i.e. approximate 16:9 as 854x480
    args = f'ffmpeg -y -f lavfi -i color=c=black:s=854x480:r=30000/1001 -f lavfi -i anullsrc=cl=mono:r=48000 -t {pages[-1]["end"]}'.split()            
    args += ['-filter_complex', f'{",".join(draw_cmd)}']
    args += '-aspect 16:9 -target ntsc-dvd'.split()
    args += [os.path.join(path_out,'startup.mpg')]
    print(' '.join(args))
    r = subprocess.run(args, capture_output=True)
    print(str(r.stderr, encoding='utf-8'))

    sdfsd # stop here


if False:
    #make red screen of death:
    args = 'ffmpeg -y -f lavfi -i color=c=red:s=720x480:r=30000/1001 -f lavfi -i anullsrc=cl=mono:r=48000 -t 2 -aspect 16:9 -target ntsc-dvd'.split()
    args += [os.path.join(path_out,'screen_red.mpg')]
    print(' '.join(args))
    r = subprocess.run(args, capture_output=True)
    print(str(r.stderr, encoding='utf-8'))

    if False:
        #make applause
        args = 'ffmpeg -y -f lavfi -i color=c=green:s=720x480:r=30000/1001 -f lavfi -i anullsrc=cl=mono:r=48000 -t 2 -aspect 16:9 -target ntsc-dvd'.split()
        args += [os.path.join(path_out,'special_applause.mpg')]
        print(' '.join(args))
        r = subprocess.run(args, capture_output=True)
        print(str(r.stderr, encoding='utf-8'))

def get_clip_length(filename):
    # https://stackoverflow.com/questions/3844430/how-to-get-the-duration-of-a-video-in-python
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

if False:
    # **run this**
    # extract sequence, fix audio, and convert to mng
    # there is an issue with non-monotonous audio frames that won't
    #  work for the DVD. Either set audio frames manually, or convert
    #  audio to mp3, then replace in current file.
    # ffmpeg -i v.mp4 -i a.wav -c:v copy -map 0:v:0 -map 1:a:0 new.mp4
    # or try this (although, this could lead to video and audio getting out of sync)
    # vsetpts, asetpts = 'setpts=N/FR/TB,', 'asetpts=NB_CONSUMED_SAMPLES/SR/TB,'
    # vsetpts, asetpts = 'setpts=PTS-STARTPTS,', 'asetpts=PTS-STARTPTS,'
    test_only = False # True: do not override file
    test_length_before_convert = False # process only if clip lengths differ
    for idx, (key, (fn_in, start, duration, flags)) in enumerate(clips.items()):
        print(idx+1, '/', len(clips), key, start, duration)
        dur = round(duration, 3)
        fn = os.path.join(path_in_video, fn_in)
        fn_out_true = os.path.join(path_out, f'{key}.mpg')
        if test_only:
            fn_out = 'c:\\temp\\i-crop.mpg'
        else:
            fn_out = fn_out_true
        if test_length_before_convert:
            if abs(duration - get_clip_length(fn_out_true)) < 0.1:
                # the clip length is close to specified, continue without
                #   processing
                continue
            else:
                print('expected', duration, 'found', get_clip_length(fn_out_true))
                
        # FFMPEG default is 6 MBit/s, while industry typical uses 4-5 MBit/s (wikipedia)
        # NB: on RECENT version of ffmpeg, the audio produced is too short...
        if True:
            # dvdauthor emits warnings from
                
if True:
    # merge i with k, do this properly
    fn_tmp = 'C:\\temp\\_mov_tmp.mp3'
    fn_tmp_video = 'C:\\temp\\_mov_tmp.mp4'
    for key in clips.keys():
        if key.startswith('k'):
            # create copies for all related i's
            i_keys = [ik for ik in clips.keys() if ik.startswith('i') and ik[1:].split('-')[::2] == key[1:].split('-') and 'ignoreLink' not in clips[ik][3]]
            for i_key in i_keys:
                
                fn_out = os.path.join(path_out, f'{i_key}_{key}.mpg')

                # we should not double-count frames at the edge if we concat two video
                #   sequences that originated from the same video. We need to shorten the duration by one frame
                #   as it will otherwise be included twice.
                fn_base_in1, start1, duration1, flags1 = clips[i_key]
                assert 'ignoreLink' not in flags1
                fn_in1 = os.path.join(path_in_video, fn_base_in1)
                dur1 = round(duration1 - 1/ntsc_fr, 3) # NB actual frame rate has already been set to 29.97 rather than 30

                fn_base_in2, start2, duration2, flags2 = clips[key]
                fn_in2 = os.path.join(path_in_video, fn_base_in2)
                dur2 = round(duration2, 3)

                # this is slow presumably at least in part because of the high resolution
                # NB: we need a -vsync vfr again, e.g. for 'k3-2'
                args=f'ffmpeg -y -ss {start1} -t {dur1} -i {fn_in1} -ss {start2} -t {dur2} -i {fn_in2} -filter_complex [0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a] -map [v] -map [a] -vsync vfr {fn_tmp_video}'.split()
                print(' '.join(args))
                r = subprocess.run(args, capture_output=True)
                print(str(r.stderr, encoding='utf-8'))

                args = f'ffmpeg -y -i {fn_tmp_video} -vn -acodec mp3 {fn_tmp}'.split()
                print(' '.join(args))
                r = subprocess.run(args, capture_output=True)
                print(str(r.stderr, encoding='utf-8'))

                args=f'ffmpeg -y -i {fn_tmp_video} -i {fn_tmp} -filter_complex [1:0]apad[audio] -map 0:v:0 -map [audio] -shortest -b:v 4M -aspect 16:9 -target ntsc-dvd {fn_out}'.split()
                print(' '.join(args))
                r = subprocess.run(args, capture_output=True)
                print(str(r.stderr, encoding='utf-8'))
