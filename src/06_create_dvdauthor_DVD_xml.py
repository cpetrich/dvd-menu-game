import os

import importlib
make_ts_switch_code = importlib.import_module('02b_identify_best_direction')

copyright_notice = 'menu_disclaimer.mpg' # traditional method
copyright_notice = 'startup.mpg' # use this if we have two notification screens.

path_out = './'
path_dvd_ts = 'dvd/'
path_in = 'dvd-mpg'
indent = 2
def a(*args):
    return '/'.join(args)
os.path.join = a

# It is important to set g0/g1 before starting the title/chapter. That way, the title reduces to eye candy between the menus,
#   and if the user skips around chapters or titles, so be it. Looks ugly but does not affect the integrity of the game.

# We don't need the dummy blanks anymore. They were introduced to make
#   it possible to jump from one chapter/title directly to another
#   to connect intersection clips with link clips directly, before entering a
#   proper menu. However, since the blank introduced a black-out period,
#   this approach was abandoned in favor of merging intersection with links
#   offline, so we always alternate between a proper menu and a proper title,
#   (or at least a title in a different titleset), so no blanks need to be
#   inserted.
#   Another option I did not implement might have been to store the link
#   sequences in titles before before the intersection sequences as this
#   would lead to a jump backward in time.
#   However, this would still introduce a seek delay.
add_dummy_blank = False

with open('01_video_sources.txt') as f:
    lines = f.read().strip().split('\n')

# we include pre-merged intersection/link combinations
#   as this is the only way to avoid a seek time break in the
#   flow

if True:
    # figure out 
    no_links = []
    all_segs = []
    segs = {}
    for line in lines:
        val = line.split('\t')
        if line.startswith('i'):
            segs[val[0]] = [val[0]]
            all_segs.append(val[0])
            if 'ignoreLink' in val[4]:
                no_links.append(val[0])
                

    for line in lines:
        val = line.split('\t')
        if line.startswith('k'):
            all_segs.append(val[0])
            x, z = val[0][1:].split('-')
            for key in segs:
                xx,yy,zz = key[1:].split('-')
                if xx==x and zz==z:
                    segs[key].append(val[0])
    
    fn_menu = {} # key: 2-3
    fn_menu_star = {} # key: 2-3
    menus = {}
    for line in lines:
        val = line.split('\t')
        if line.startswith('m'):
            key = val[0][1:]
            inter = int(key.split('-')[0])
            mapping = val[1].split('-')
            order = val[2].split('-')
            if inter not in menus: menus[inter] = []
            menus[inter].append((key, mapping, order))
            fn_menu[key] = os.path.join(path_in,f'menu_{key}.mpg')
            fn_menu_star[key] = os.path.join(path_in,f'menu_{key}_star.mpg')

if True:
    fn_seg = {} # key: "2-3-4"
    
    for key, segments in segs.items():
        assert key[0] == 'i'
        if len(segments) == 1 or key in no_links:
            fn_seg[key[1:]] = os.path.join(path_in, f'{key}.mpg')
        elif len(segments) >= 2:
            fn_base = '_'.join(segments)
            fn_seg[key[1:]] = os.path.join(path_in, f'{fn_base}.mpg')
        else:
            raise NotImplementedError(f'for {key}: {segments}')

    # we need to define for each intersection
    #  * which titleset it is in (menu and title)
    #  * which menu number it is within that titleset
    #  * which title number/chapter number is to be played for a transition in that titleset

    include_view_chapters = True

    titleset = 2
    max_titles_per_ts = 90
    max_intersections_per_ts = 1 # we need many menus per intersection: with and without star, and with guiding stars
    intersections = sorted(menus.keys())
    max_intersection = max(intersections)
    tsd = {titleset:{'intersections':[], 'title_no':{}, 'chapter_no':{}} }
    intersection = 0
    title_no, menu_no = 1, 2
    while intersection < max_intersection:
        intersection += 1
        if intersection not in menus or len(menus[intersection]) == 0: continue # no menu in this intersection
        if len(tsd[titleset]['intersections']) >= max_intersections_per_ts:
            titleset += 1
            tsd[titleset] = {'intersections':[], 'title_no':{}, 'chapter_no':{}}
            title_no = 1
        tsd[titleset]['intersections'].append(intersection)
        all_menus = [menu for menu, _, _ in menus[intersection]] # e.g., ['3-2', '3-4', '3-5', '3-14']

        tsd[titleset]['title_no'][intersection] = title_no   # always 1
        title_no += 1        
        all_chapters = [key for key in fn_seg.keys() if int(key.split('-',1)[0]) == intersection]
        chapter_no = 2 # we start with chapter #2 since chapter #1 is the entry point if VCR performs 'resume' operation from a menu
        if include_view_chapters:
            chapter_no += len(all_menus)
        for chapter in all_chapters:
            val = tuple(int(i) for i in chapter.split('-'))
            tsd[titleset]['chapter_no'][val] = chapter_no
            chapter_no += 1

    del no_links
    del all_segs
    del segs

def render(xml):
    out = []
    starting_level = 0
    level = starting_level
    for raw_line in xml:
        line = raw_line # todo: consider removing comments
        if line.strip().startswith('<!--'):
            # assume that comment will also end this line
            out.append(' '*(indent*level) + raw_line)
            continue

        if True:
            # NB: it is assumed that no commands follow a
            #   comment, even after the end of a comment
            # Also, braces are not allowed in the same row as a tag
            # also, there is at most one opening bracket and one closing bracket on a line
            val = line.split('<!--')[0].split('/*')[0]
            if '<' in val or '>' in val:
                assert '{' not in val and '}' not in val
            
        if line.strip().startswith('</'):
            level -= 1

        pre_subtracted = 0
        if True:            
            test = line.split('/*',1)[0].strip()
            #test = line.strip()
            idx = 0
            while idx < len(test) and test[idx] == '}':
                pre_subtracted += 1
                idx += 1
            level -= pre_subtracted
            
        out.append(' '*(indent*level) + raw_line)
        if line.strip().startswith('<') and not line.strip().startswith('</'):
            if not '/>' in line and not '</' in line:
                level += 1
        else:
            if '/>' in line:
                level -= 1
        level += line.count('{') - (line.count('}')-pre_subtracted)
    if level != starting_level:
        # just a simple check to catch obvious errors
        raise ValueError('braces or tags do not balance')
    return out

# state how many steps one needs to make before a smiley
#   appears, depending on the number of stars allready collected.
#   (Set to 0 to disable, set to 1 for immediate effect.)
g7_0found = 7
g7_1found = 6
g7_2found = 5

############################################
# titleset

def make_titleset(titleset):
    print(f'Generating titleset {titleset}')
    if titleset == 1: return make_titleset_1()
    out = []
    out.append(f'<titleset> <!-- ts {titleset} -->')
    out += make_titleset_menus(titleset)
    out += make_titleset_titles(titleset)
    out.append(f'</titleset> <!-- end ts {titleset} -->')
    return out

def make_titleset_menus(titleset):
    out = []
    out.append('<menus>')

    root_menu, linked_menus = make_ts_root_menu(titleset) # this is menu 1 and possibly 2    
    out += root_menu
    #linked_menus: list of [menu_number, (intersection, view_from),'smiley'|'star'|'sposXXX']
    # create one menu pgc for each view, in the correct order
    for menu_no, (intersection, prev_intersection), group in linked_menus:
        fn_menu = f'dvd-mpg/menu_{intersection}-{prev_intersection}_{group}.mpg'
        out.append(f'<pgc> <!-- ts {titleset}, menu {menu_no} for {intersection}-{prev_intersection} with {group} -->')
        out.append(f'<vob file="{fn_menu}" pause="inf" />')
        # add button actions:
        menu_tag = f'{intersection}-{prev_intersection}'
        mapping, order = [(mapping, order) for men, mapping, order in menus[intersection] if men == menu_tag][0]
        for button_name in order:
            new_intersection = button_dest(mapping, button_name)
            itag = '-'.join(str(x) for x in (intersection, prev_intersection, new_intersection))
            try:
                title_no = tsd[titleset]['title_no'][intersection]
                chapter_no = tsd[titleset]['chapter_no'][(intersection, prev_intersection, new_intersection)]
                assert chapter_no is not None # this is a way to get into the Exception
                out.append(f'<button name="{button_name}">g0 = (g0 &amp; 0xFF) * 256 + {new_intersection}; jump title {title_no} chapter {chapter_no};</button> <!-- play {itag} and continue at intersection {new_intersection} -->')
            except Exception as e:
                print(f'no title/chapter for intersection {itag}, performing jump')
                out.append(f'<button name="{button_name}">g0 = (g0 &amp; 0xFF) * 256 + {new_intersection}; jump vmgm menu 1;</button> <!-- no movie for {itag}, jump directly to intersection {new_intersection} -->')
            # define a default reaction in case one button does not jump elsewhere
        if group == 'star': # make star button
            out.append(f'<button name="s">g2=0x0010; jump vmgm menu 1;</button> <!-- process star, play special effect, and come back to this menu -->')
        if group == 'smiley': # make star button
            out.append(f'<button name="s">g9 &amp;= 0x00FF; g4 &amp;= 0x7F; g2=0; jump vmgm menu 1;</button> <!-- take and remove smiley, clear flag to indicate that we want help, and come back to this menu -->')
            
        # force button=1024 since the VCR may remember the star/smiley button which may not exist anymore
        out.append('<pre>g2=0; button=1024;</pre> <!-- normal jumppad distribution according to content of g0 -->')
        out.append('<post>jump pgc top;</post>')
        out.append('</pgc>')
        
    out.append('</menus>')
    return out
    
def make_titleset_titles(titleset):
    out = []
    out.append('<titles>')
    for idx, (intersection, title_no) in enumerate(sorted(tsd[titleset]['title_no'].items(), key=lambda x: x[1])):
        assert idx+1 == title_no
        out.append(f'<pgc> <!-- ts {titleset}, title {title_no}. Intersection {intersection} -->')
        fn = os.path.join(path_in, 'screen_blank-10ms.mpg')
        out.append(f'<vob file="{fn}"> <!-- cell 1 is entry point when resume is called from a menu -->')
        out.append(f'<cell start="0" chapter="yes">jump pgc tail;</cell>')
        out.append('</vob>')
        if include_view_chapters:
            orgs = sorted(int(m.split('-')[1]) for m, _, _ in menus[intersection])
            for idx, org in enumerate(orgs):
                fn = os.path.join(path_in, f'view_{intersection}-{org}.mpg')
                out.append(f'<vob file="{fn}"> <!-- cell {idx+2} is view of {intersection}-{org}, shown at start of game -->')
                out.append(f'<cell start="0" chapter="yes">jump pgc tail;</cell>')
                out.append('</vob>')
                
        for idxc, (info, chapter_no) in enumerate(sorted([(a,b) for a,b in tsd[titleset]['chapter_no'].items() if a[0]==intersection], key=lambda x: x[1])):
            if not include_view_chapters:
                assert idxc+2 == chapter_no
            else:
                assert idxc+2+len(menus[intersection]) == chapter_no
            inter, prev, new = info
            itag = '-'.join(str(x) for x in info)
            out.append(f'<vob file="{fn_seg[itag]}"> <!-- ts {titleset}, title {title_no}, chapter {chapter_no}: {itag} -->')
            out.append(f'<cell start="0" chapter="yes">jump pgc tail;</cell>')
            out.append('</vob>')
        out.append('<pre>')
        out.append('if ((g12 &amp; 0x0020) != 0) {call vmgm menu 3 resume 1;} <!-- stay in error menu -->')
        out.append('if ((g12 &amp; 0x0100) == 0) {call vmgm menu entry title resume 1;} <!-- game has yet to be started (however, note that VCR remote resume does not execute "pre") -->')
        out.append('if ((g12 &amp; 0x8000) != 0) {call vmgm menu 1 resume 1;} <!-- skip playing transition and go straight to new intersection -->')
        out.append('g12 |= 0x0200; <!-- indicate that a title has ever been plaied, i.e. resume is pointing to a valid cell -->')
        out.append('g12 |= 0x0010; <!-- indicate that title is playing and can be resumed -->')
        out.append('</pre>')
        out.append('<post>')
        out.append('g12 &amp;= 0xFFEF; <!-- indicate that no title is playing if we should not "resume" play -->')
        out.append('call vmgm menu 1; <!-- jump to intersection according to g0 (typically g2==0) (implied resume point is cell 1) -->')
        out.append('</post>')
        out.append(f'</pgc>')
    out.append('</titles>')
    return out

def button_dest(mapping, button):
    for entry in mapping:
        name = ''.join(s for s in entry if s not in '0123456789')
        if button == name:
            return int(''.join(s for s in entry if s in '0123456789'))
    return None

def make_ts_root_menu(titleset):
    # this is menu 1 and possibly menu 2, designated root for entry from vmgm,
    #  which contains the jumppad to the menu based on g0
    assert len(tsd[titleset]['intersections']) == 1
    intersection = tsd[titleset]['intersections'][0]
    
    # make_ts_switch_code.make_ts_code_block(intersection)
    codes, linked_menus = make_ts_switch_code.make_ts_code_block(intersection)
    out = []
    for idx, code in enumerate(codes):
        if idx == 0: out.append(f'<pgc entry="root"> <!-- ts {titleset}, menu {idx+1} (root) -->')
        else: out.append(f'<pgc> <!-- ts {titleset}, menu {idx+1} (continues root) -->')
        
        out.append('<pre>')
        out += code
        out.append('</pre>')
        out.append(f'</pgc> <!-- end ts {titleset}, menu {idx+1} -->')
        
    return out, linked_menus

def make_ts_subtitle_menu(titleset):
    # catch the subtitle key to place the smiley at the current
    #   intersection, if possible
    # if star hints are currently active, deactivate them
    # 'subtitle' works on VLC but not on the stand-alone DVD player.
    # try 'audio'
    out = []
    out.append('<pgc entry="audio"> <!-- Audio menu -->')
    # while VLC does, VCR does not call up this menu if there's only code in <pre> and nothing else.
    #  Same problem if we have a vob and put the code in the post.
    #
    # --> would need to create an extra menu that is called from a menu button and gives the choice
    #     to toggle the smiley.
    out.append('<pre>')
    intersection = tsd[titleset]['intersections'][0]
    check = 2**(intersection-1)
    out.append('if ((g4 &amp; 0x80) == 0) { g4 |= 0x80; } <!-- deactivate star hints -->')
    out.append('else { <!-- not currently showing star hints, place smiley if possible -->')
    out.append(f'if ((g3 &amp; 0x{check:04X}) == 0) {{ <!-- no star at current position -->')
    out.append('g9 = g9 &amp; 0x00FF;')
    out.append('g9 += (g0 &amp; 0x00FF) * 256; <!-- put smiley at current position -->')
    out.append('}}')
    out.append('if (g7 gt 1) {g7 += 1;} <!-- compensate automated smiley placement for repeatedly entering the intersection menu -->')
    out.append('g2 = 0; <!-- in case we interrupted something -->')
    out.append("jump vmgm menu 1; <!-- re-enter intersection's menu -->")
    out.append('</pre>')
    out.append('</pgc>')
    return out

def make_titleset_1():
    out = []
    out.append('<titleset> <!-- titleset 1, special sequences selected by value in g2 (!=0). Return with g2 == 0 -->')
    out.append('<menus>')
    out.append('<pgc entry="root">')
    # dummy blank is not necessary since we're coming from a different titleset
    fn = os.path.join(path_in, 'screen_blank-10ms.mpg')
    if add_dummy_blank: out.append(f'<vob file="{fn}"/>')
    out.append('<post>')
    out.append('if ((g12 &amp; 0x0020) != 0) {jump vmgm menu 3;} <!-- stay in error menu -->')

    out.append('if ((g12 &amp; 0x01) != 0) {jump vmgm menu 9;} <!-- we got here because player pushed menu button -->')
    out.append('g12 |= 0x01; <!-- set flag to make next call into this menu (DVD remote) divert to main menu -->')

    out.append('if (g2 == 0x0010) { <!-- got a star: remove star location entry -->')
    out.append('  if ((g0 &amp; 0xFF) == (g8 &amp; 0xFF)) {g8 &amp;= 0xFF00;}')
    out.append('  if ((g0 &amp; 0xFF) == (g8 / 256)) {g8 &amp;= 0x00FF;}')
    out.append('  if ((g0 &amp; 0xFF) == (g9 &amp; 0xFF)) {g9 &amp;= 0xFF00;}')
    out.append('  g2 = 0; <!-- count the number of stars we found -->')
    out.append('  if ((g8 &amp; 0x00FF) == 0) {g2 += 1;}')
    out.append('  if ((g8 &amp; 0xFF00) == 0) {g2 += 1;}')
    out.append('  if ((g9 &amp; 0x00FF) == 0) {g2 += 1;}')
    # we set g2 before entering the title to prevent player from changing the
    #   program flow path by simply skipping to a different chapter
    out.append('  if ((g8 == 0) and ((g9 &amp; 0xFF) == 0)) { <!-- found all stars -->')
    out.append('    <!-- play final trailer and game over -->')
    out.append('    g2 = random(4);')
    out.append('    <!-- set g2 to 1 to indicate that we are supposed to enter the main menu afterwards -->')
    out.append('    if (g2 == 1) {g2 = 1; jump title 1 chapter 6;}')
    out.append('    if (g2 == 2) {g2 = 1; jump title 1 chapter 7;}')
    out.append('    if (g2 == 3) {g2 = 1; jump title 1 chapter 8;}')
    out.append('    if (g2 == 4) {g2 = 1; jump title 1 chapter 9;}')
    out.append('    g2 = 1; jump title 1 chapter 5;')
    out.append('  }');
    out.append('  if (g2 == 0) {g2=0; jump vmgm menu 6;} <!-- update g3 and skip play -->')
    out.append(f'  if (g2 == 1) {{g7={g7_1found}; g4 |= 0x80; g2=0; jump title 1 chapter 2;}} <!-- set g7 counter for smiley to appear -->')
    out.append(f'  if (g2 == 2) {{g7={g7_2found}; g4 |= 0x80; g2=0; jump title 1 chapter 3;}} <!-- set g7 counter for smiley to appear -->')
    out.append(f'  if (g2 == 3) {{g7={g7_2found}; g4 |= 0x80; g2=0; jump title 1 chapter 4;}} <!-- this cannot be called, consider removing -->')
    out.append('  jump vmgm menu 3; <!-- this cannot be right -->')
    out.append('}')
    out.append('jump vmgm menu 3; <!-- error, unknown g2 -->')
    out.append('</post>')
    out.append('</pgc>')
    
    out.append('</menus>')
    out.append('<titles>')
    out.append('<pgc> <!-- title 1: got a star, then continue at same location -->')
    fn = os.path.join(path_in,"screen_blank-10ms.mpg")
    out.append(f'<vob file="{fn}"> <!-- chapter 1 is to capture resume called from menu -->')
    out.append(f'<cell start="0" chapter="yes">jump pgc tail;</cell>')
    out.append('</vob>')
    for i in range(3):
        fn = os.path.join(path_in, f'special_stars_{i+1}.mpg')
        out.append(f'<vob file="{fn}">')
        out.append(f'<cell start="0" chapter="yes">jump pgc tail;</cell>')
        out.append('</vob>')
    fn = os.path.join(path_in, 'special_stars.mpg')
    out.append(f'<vob file="{fn}">')
    out.append(f'<cell start="0" chapter="yes">jump pgc tail;</cell>')
    out.append('</vob>')
    for i in range(4):
        fn = os.path.join(path_in, f'special_stars_col{i+1}.mpg')
        out.append(f'<vob file="{fn}">')
        out.append(f'<cell start="0" chapter="yes">jump pgc tail;</cell>')
        out.append('</vob>')
    out.append('<pre>')
    out.append('if ((g12 &amp; 0x0020) != 0) {call vmgm menu 3 resume 1;} <!-- stay in error menu -->')
    out.append('if ((g12 &amp; 0x0100) == 0) {call vmgm menu entry title resume 1;} <!-- game has yet to be started -->')
    out.append('g12 |= 0x0200; <!-- indicate that a title has ever been plaied, i.e. resume is pointing to a valid cell -->')
    out.append('g12 |= 0x0010; <!-- now playing a clip -->')
    out.append('</pre>')
    out.append('<post>')
    out.append('g12 &amp;= 0xFFEF; <!-- not playing a clip -->')
    if True:
        out.append('  if (g2 == 0) {call vmgm menu 6;} <!-- update g3 and go to vmgm menu 1 -->')
        out.append('  if (g2 == 1) {g2 = 0; g12 &amp;= 0xFCFF; call vmgm menu entry title;}')
        out.append('  call vmgm menu 3;')
    else:
        out.append('g2=0; call vmgm menu 6; <!-- update g3 and go to vmgm menu 1 -->');
    out.append('</post>')
    out.append('</pgc>')
    out.append('</titles>')
    out.append('</titleset>')
    return out


def make_vmgm():
    code = ["if (g2 == 0x0000) {"]
    code.append('  g2 = random(255); <!-- help randomize state -->')
    code.append('  g2 = 0;')
    code.append('  g12 &amp;= 0xFFFE; <!-- clear flag so ts root will not jump back to main menu -->')
    code.append('  g12 &amp;= 0xFFEF; <!-- clear flag to indicate that no title is playing and there is nothing to resume -->')
    for ts, data in tsd.items():
        max_inter = max(data['intersections'])
        min_inter = min(data['intersections'])
        code.append(f'  if ((g0 &amp; 0xff) le 0x{max_inter:02X}) {{jump titleset {ts} menu entry root;}} <!-- intersections {min_inter} - {max_inter} are in ts {ts} -->')
    code.append('  jump menu 3; <!-- error -->')
    code += """
} else {
  <!-- jump to titleset containing special effects -->
  <!-- the actual special effect is selected by g2 -->
  g12 &amp;= 0xFFFE; <!-- clear flag so ts 1 root will not immediately jump back to main menu -->
  jump titleset 1 menu entry root;
}
""".strip().split('\n')
    ind = ' '*4
    code = '\n'.join([ind + line for line in code])

    fn_blank = os.path.join(path_in,"screen_blank-10ms.mpg") # in this case, remove pause="inf"
    fn_main_menu = os.path.join(path_in,"menu_main.mpg")
    fn_toggle_menu = os.path.join(path_in,"menu_toggle.mpg")

    #max_intersection_id = 13 # choose random star locations from 1 to 13 inclusive
    #max_intersection_id = 4

    # jump menu entry title;
    vmgm = [line.strip() for line in f"""
    <vmgm>
    <fpc>
      g0 = 0x0403; <!-- start at intersection 3, coming from intersection 4 -->
      g2 = 0; <!-- important, otherwise we'll end up in special effects -->
      g10 = 0; <!-- used for star distribution algorithm -->
      g8 = 0x0108; <!-- stars at 1 and 8 -->
      g9 = 0x0005; <!-- star at 5, no smiley -->
      g3 = 0x0091; <!-- bit flag of star locations -->
      g4 = 0x80; <!-- no smiley hints -->
      g7 = {g7_0found}; <!-- count down steps until smiley hint appears -->
      g12 = 0x01; <!-- clear bits 15, 4, and set bit 0 flag so the toggle menu appears if the user pushes the titleset menu button -->
      <!-- the above define the state used if the player interrupts the disclaimer -->
      <!-- with the title menu and then leaves that menu through "resume", i.e. -->
      <!-- plays titleset 1 title 1 chapter 1 (dummy) and jumps to the jumppad -->
      <!-- (this can happen only after the first title in a titleset had been played, -->
      <!-- before that, calling the root menu is simply disabled) -->
      <!-- jump menu 8; : show disclaimer, then call jump menu entry title; -->
      <!--g2 = 0xABCD;-->
      <!-- jump titleset 1 menu entry root; - this will play a dummy clip, set g2 := 0, before calling vmgm menu 8 to ensure that resume registers are set -->
      jump menu 8; <!-- show disclaimer, then jump menu entry title; -->
    </fpc>
    <menus>
    <pgc> <!-- vmgm menu 1: jumppad to select relevant titleset -->
    <pre>
    if ((g12 &amp; 0x0020) != 0) {{jump menu 3;}} <!-- stay in error menu -->
    if ((g12 &amp; 0x0100) == 0) {{jump menu entry title;}} <!-- not actually in game: we must have gotten here through VCR remote resume -->
    <!-- g2==0: titleset according to g0. g2 != 0: special effects in titleset 1 -->
    @@code
    </pre>
    </pgc>
    <pgc entry="title"> <!-- restart menu -->
    <vob file="{fn_main_menu}" pause="inf" />
    <button name="1">g12 = 0x0100; g4=0x80; g7={g7_0found}; g10=0; jump menu 5;</button> <!-- set do-not-help flag, get new stars and remove smiley and set g3, and continue at g0 in menu 1 (via menu 5 and menu 6)-->
    <pre>
    <!-- note that there are situations not caught in PRE -->
    <!-- where the player is able to show the menu after a crash -->
    <!-- in spite of the test for 0x0020. -->
    if ((g12 &amp; 0x0020) != 0) {{jump menu 3;}} <!-- stay in error menu -->
    g2 = 0; button = 1024;
    </pre>
    <post>jump pgc top;</post>
    </pgc>
    <pgc> <!-- error handler menu 3 -->
    <!-- we may end up here if the player presses the titleset menu button during the very first showing of the main menu -->
    <vob file="{os.path.join(path_in,"screen_blue.mpg")}" pause="inf" /> <!-- blue screen of death -->
    <pre>g12 |= 0x0020;</pre> <!-- set a flag to try to ensure that player MUST eject the disk rather than continue game in an ill-defined state -->
    </pgc>
    <pgc> <!-- error handler menu 4, used for debugging/tracing -->
    <vob file="{os.path.join(path_in,"screen_red.mpg")}" pause="inf" /> <!-- red screen of death -->
    </pgc>
    <pgc> <!-- menu 5: distribute stars randomly -->
    <!-- g10: state pointer. Set to 0 before calling this menu. -->
    <!-- g2: group of candidate intersections -->
    <!-- g0: current location (no stars placed there) -->
    <!-- g8/g9: stars (output) -->
    <pre>
      g10 += 1;
      if (g10 == 1) {{
        g2 = random(4);
        jump menu 7;
      }}
      if (g10 == 2) {{
        g8 = g9;
        if (g8 == g0 &amp; 0x00FF) {{g10 -= 1;}}
        jump menu 7;
      }}
      if (g10 == 3) {{
        if ((g9 == g0 &amp; 0xFF) ||
            (g9 == g8)) {{g10 -= 1; jump menu 7;}}
        g8 += g9 * 256;
        jump menu 7;
      }}
      if (g10 == 4) {{
        if ((g9 == g0 &amp; 0xFF) ||
            (g9 == g8 &amp; 0xFF) ||
            (g9 == (g8 &amp; 0xFF00) / 256)) {{g10 -= 1; jump menu 7;}}
        <!-- successfully distributed stars randomly -->
        g2 = 0;
        g10 = 0;
        jump menu 6; /* now update g3 and jump to menu 1 */
      }}
      jump vmgm menu 3;
    </pre>
    </pgc>
    <pgc> <!-- menu 6: set g3 based on stars -->
    <pre>
    <!-- map location to bit pattern -->
    g3 = 0;
    g2 = g9 &amp; 0x00FF;
    if (g2 == 1) {{g3 |= 0x0001;}}
    if (g2 == 2) {{g3 |= 0x0002;}}
    if (g2 == 3) {{g3 |= 0x0004;}}
    if (g2 == 4) {{g3 |= 0x0008;}}
    if (g2 == 5) {{g3 |= 0x0010;}}
    if (g2 == 6) {{g3 |= 0x0020;}}
    if (g2 == 7) {{g3 |= 0x0040;}}
    if (g2 == 8) {{g3 |= 0x0080;}}
    if (g2 == 9) {{g3 |= 0x0100;}}
    if (g2 ==10) {{g3 |= 0x0200;}}
    if (g2 ==11) {{g3 |= 0x0400;}}
    if (g2 ==12) {{g3 |= 0x0800;}}
    if (g2 ==13) {{g3 |= 0x1000;}}
    if (g2 ==14) {{g3 |= 0x2000;}}
    if (g2 ==15) {{g3 |= 0x4000;}}
    if (g2 ==16) {{g3 |= 0x8000;}}
    g2 = g8 &amp; 0x00FF;
    if (g2 == 1) {{g3 |= 0x0001;}}
    if (g2 == 2) {{g3 |= 0x0002;}}
    if (g2 == 3) {{g3 |= 0x0004;}}
    if (g2 == 4) {{g3 |= 0x0008;}}
    if (g2 == 5) {{g3 |= 0x0010;}}
    if (g2 == 6) {{g3 |= 0x0020;}}
    if (g2 == 7) {{g3 |= 0x0040;}}
    if (g2 == 8) {{g3 |= 0x0080;}}
    if (g2 == 9) {{g3 |= 0x0100;}}
    if (g2 ==10) {{g3 |= 0x0200;}}
    if (g2 ==11) {{g3 |= 0x0400;}}
    if (g2 ==12) {{g3 |= 0x0800;}}
    if (g2 ==13) {{g3 |= 0x1000;}}
    if (g2 ==14) {{g3 |= 0x2000;}}
    if (g2 ==15) {{g3 |= 0x4000;}}
    if (g2 ==16) {{g3 |= 0x8000;}}
    g2 = (g8 &amp; 0xFF00) / 256;
    if (g2 == 1) {{g3 |= 0x0001;}}
    if (g2 == 2) {{g3 |= 0x0002;}}
    if (g2 == 3) {{g3 |= 0x0004;}}
    if (g2 == 4) {{g3 |= 0x0008;}}
    if (g2 == 5) {{g3 |= 0x0010;}}
    if (g2 == 6) {{g3 |= 0x0020;}}
    if (g2 == 7) {{g3 |= 0x0040;}}
    if (g2 == 8) {{g3 |= 0x0080;}}
    if (g2 == 9) {{g3 |= 0x0100;}}
    if (g2 ==10) {{g3 |= 0x0200;}}
    if (g2 ==11) {{g3 |= 0x0400;}}
    if (g2 ==12) {{g3 |= 0x0800;}}
    if (g2 ==13) {{g3 |= 0x1000;}}
    if (g2 ==14) {{g3 |= 0x2000;}}
    if (g2 ==15) {{g3 |= 0x4000;}}
    if (g2 ==16) {{g3 |= 0x8000;}}
    g2 = 0;
    jump menu 1; /* jump to jumppad */
    </pre>
    </pgc>
    <pgc> <!-- menu 7, selective random number groups -->
    <!-- input: g2: random number group -->
    <!-- output g9: random intersection -->
    <pre>
      <!-- 3 and 13 have only half the chance of a star than the others -->
      if (g2 == 1) {{ <!-- 1,2,3,4,5,6,14 -->
        g9 = random(7);
        if (g9 ge 7) {{g9 += 7;}}
      }}
      if (g2 == 2) {{ <!-- 4,5,6,7,8,9 -->
        g9 = 3+random(6);
      }}
      if (g2 == 3) {{ <!-- 10,11,12,13,1,2 -->
        g9 = 9+random(6);
        if (g9 ge 14) {{g9 -= 13;}}
      }}
      if (g2 == 4) {{ <!-- 7,8,9,10,11,12 -->
        g9 = 6+random(6);
      }}
      jump menu 5;
    </pre>
    </pgc>
    <pgc> <!-- menu 8, disclaimer -->
    <vob file="{os.path.join(path_in,copyright_notice)}" />
    <pre>
    if ((g12 &amp; 0x0020) != 0) {{jump menu 3;}} <!-- stay in error menu -->
    </pre>
    <post>jump menu entry title;</post>
    </pgc>
    <pgc> <!-- menu 9, common titleset menu -->
    <vob file="{fn_toggle_menu}" pause="inf" />
    <button name="smiley">
      if ((g4 &amp; 0x80) == 0) {{ g4 |= 0x80; }} <!-- deactivate star hints -->
      else {{ <!-- not currently showing star hints, place smiley if possible -->
      if ( ((g0 &amp; 0x00FF) != (g8 &amp; 0x00FF)) and
           ((g0 &amp; 0x00FF) != (g9 &amp; 0x00FF)) and
           ((g0 &amp; 0x00FF) != (g8 &amp; 0xFF00)/256) ) {{
           <!-- no star at current position -->
        g9 = g9 &amp; 0x00FF;
        g9 += (g0 &amp; 0x00FF) * 256; <!-- put smiley at current position -->
      }} <!-- optionally, we could say: else g7 = 1; to place smiley at the next opportunity, but that would interfere with ordinary game play in the form of counter g7 -->
      }}      
      resume; <!-- exit through resume so the VCR does not get confused -->
      <!-- g2 = 0; jump menu 1; - go straight to current intersection (typically, the first one in a game) -->
    </button>
    <button name="run">
      <!-- toggle run flag -->
      g12 ^= 0x8000;
      resume; <!-- exit through resume so the VCR does not get confused -->
      g2 = 0; jump menu 1; <!-- go straight to current intersection (typically, the first one in a game) -->
    </button>
    <pre>
    if ((g12 &amp; 0x0020) != 0) {{jump menu 3;}} <!-- stay in error menu -->
    if ((g12 &amp; 0x0100) == 0) {{jump menu entry title;}} <!-- game has yet to be started -->
    if ((g12 &amp; 0x0200) == 0) {{jump menu entry title;}} <!-- VCR resume point may be nonsense, or VM resume stack may be undefined -->
    <!-- compensate for smiley here in case we were in a menu and the player uses the remote to resume: in that case Chapter 1 would be played, decreasing the g7 counter -->
    if ((g12 &amp; 0x0010) == 0) {{ <!-- calling this menu from another menu -->
        <!-- increase g7 since we will leve by resuming to Cell 1, which will then call the jumppad and reduce the g7 counter -->
        if (g7 gt 1) {{g7 += 1;}} <!-- compensate automated smiley placement for repeatedly entering the intersection menu -->
    }}
    button = 1024;
    </pre>
    <post>jump pgc top;</post>
    </pgc>
    </menus> 
    </vmgm>
    """.strip().replace('@@code',code).split('\n')]
    
    return vmgm


xml = []
xml.append(f'<dvdauthor dest="{path_dvd_ts}">')
xml += make_vmgm()
xml += make_titleset(1)
for ts in tsd:
    xml += make_titleset(ts)
xml.append('</dvdauthor>')

text = '\n'.join(render(xml))

with open('06_dvd.xml','w') as f:
    f.write(text)

print(text)
print('run: dvdauthor -x 06_dvd.xml')
print('run: mkisofs -dvd-video -o dvd.iso dvd/')

