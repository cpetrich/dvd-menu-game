# include with
# import importlib
# make_ts_code = importlib.import_module('02b_identify_best_direction.py')

include_view_chapters = True

with open('01_video_sources.txt') as f:
    lines = f.read().strip().split('\n')

def get_number(info):
    s = ''
    pre = ''
    for i in range(len(info)-1,-1,-1):
        if info[i] in '0123456789': s = info[i] + s

    for i in range(len(info)):
        if info[i] not in '0123456789': pre += info[i]
        
    return pre, int(s)

# we could introduce link lengths to break ties in which route
#   is to be prefered for equal number of steps

intersections = set([])
routes = {}
orders = {}
origins = {}
for line in lines:
    if not line.startswith('m'): continue
    rkey, val, oval = line.split('\t')
    key = tuple(int(i) for i in rkey[1:].split('-')) # e.g. 4-3 => (4,3) (intersection 4 coming from 3)
    # get the destination intersection in consistent order
    #  i.e. in order of preference (prefer waling straight)
    #  (and in order of binary bit pattern)
    vals = val.split('-')
    dest = {get_number(s)[0]:get_number(s)[1] for s in vals}
    order = oval.split('-')
    destinations = [dest[d] for d in order]
    routes[key] = destinations
    orders[key] = order
    intersections.add(key[0])
    try: origins[key[0]] = sorted( set(origins[key[0]] + [key[1]]) )
    except Exception: origins[key[0]] = [key[1]]
intersections = sorted(intersections)


def trace(field, origin, levels_to_go=1, route_key=None):
    if levels_to_go <= 0: return
    at, prev = origin
    level = field[at][0]
    for idx, following in enumerate(routes[(at, prev)]):
        r_key = route_key if route_key is not None else idx
        if field[following] == (None, None):
            field[following] = (level+1, r_key)
        else:
            trace(field, (following, at), levels_to_go-1, r_key)


def bitmask_fields(destinations):
    assert len(intersections) <= 16
    # bit 0 == intersection 1
    # bit 1 == intersection 2 etc
    idx0 = min(intersections)
    mask = ['0' for _ in range(16)]
    for d in destinations:
        mask[d-idx0] = '1'
    return ''.join(mask[-1::-1])


# g0: 16 bit position and view
# g1:
# g2: 8 bit special effects override of g0 jumppad,
#     temp buffer outside of that: random number group,
#                                  count current number of stars
#                                  convert star locations to distribution flag
# g3: 16 bit star distribution flags
# g4: 1+7 bit hint flag and temp menu distribution register
# g5:
# g6:
# g7: 8 bit backward move counter until smiley is set (updated when star is either found or distributed)
# g8: 16 bit location of two stars
# g9: 8+8 bit location of one star, ad-hoc location of smiley
# g10: 8/16 bit temp. counter / state register 
# g11:
# g12: bits:
#       bit  0:   0 if root menu is called from vmgm (i.e. normal processing), 1 if root menu is to jump to menu (i.e. root menu entered by user).
#       bit  4:   0 while in intersection menu, 1 while chapter is playing. Can be used in titleset menu to determine resume action. Not used and not well tested
#       bit  5:   0 usually. 1 after error occurred to prevent user from re-entering game un undefined state through menu keys.
#       bit  8:   0 prior to start of game, 1: game active (prevents titleset menu from being executed)
#       bit  9:   1: any chapter has ever played, i.e. VCR has valid resume stack for resume command (reset on start of game)
#       bit 15:   0 if transition movies between intersections are to be played, 1 if they are to be skipped


def _make_view_jumppad(intersection):
    origins = sorted([origin for inter, origin in routes.keys() if inter == intersection])
    out = []
    for idx, org in enumerate(origins):
        code = intersection + 256 * org
        # chapter 1 == blank
        # followed by len(origin) chapters with views
        target_chapter = 1 + 1+idx;
        out.append(f'if (g0 == 0x{code:04X}) {{jump title 1 chapter {target_chapter};}} <!-- show brief still of {intersection}-{org} -->')
    out.append('jump vmgm menu 3; <!-- should not have happened -->')
    return out

def make_ts_code_block(intersection, split_in_two = False):
    #intersection = 9
    menu_basis_offset = 1 + ((1+len(origins[intersection])) if split_in_two else 1) # accounting for jumppad in root, and possibly
    #    an additional menu if this one is too long
    n_special_menus = 2 # 1st for smiley here, 2nd for star here
    processed_menus = 0
    linked_menus = []
    line_groups = []
    lines = []
    lines.append('<!-- titleset menu 1 (root) -->')
    lines.append('if ((g12 &amp; 0x0020) != 0) {jump vmgm menu 3;} <!-- stay in error menu -->')
    lines.append('if ((g12 &amp; 0x01) != 0) {jump vmgm menu 9;} <!-- player pushed menu button -->')
    if not include_view_chapters:
        # the following test results in a blank at the start of the game. May be dropped, but then the titleset menu would not work first thing into a game.
        lines.append('if ((g12 &amp; 0x0200) == 0) {jump title 1 chapter 1;} <!-- first time menu, jump to dummy title to define an entry point for resume (which enables use of titleset menu) -->')
    else:
        # better option: prepare stills of the views into the intersection and jump to those titles at this point, i.e. have a lookup of up to 4 views here.
        lines.append('if ((g12 &amp; 0x0200) == 0) { <!-- first time menu, jump to title of view to define an entry point for resume (which enables use of titleset menu) -->')
        lines += _make_view_jumppad(intersection)
        lines.append('}')
    lines.append('g12 |= 0x01; <!-- set flag to make next call into this menu divert to main menu -->')
    lines.append('<!-- g3 == binary pattern of star locations (bit 0 = intersection 1 etc) -->')
    lines.append('<!-- if we want no hint then we have to set g4 to a specific flag-value != 0 (i.e., 0x80) -->')
    lines.append('if ((g4 &amp; 0x80) == 0) {g4 = 0x00;} else {g4 = 0x80;}')
    own_loc = int(bitmask_fields([intersection]), 2)
    lines.append(f'if ((g3 &amp; 0x{own_loc:04X}) != 0) {{g4 |= 0x40;}} <!-- star at current intersection ({intersection}) -->')
    lines.append('else {')
    lines.append('<!-- place smiley here if both (a) it is time to do so, and (b) star-hints are not currently active -->')
    lines.append('  if ((g7 == 1) and ((g4 &amp; 0x80) != 0)) {g9 = (g9 &amp; 0x00FF) + 256 * (g0 &amp; 0x00FF); g7 = 0;}')
    lines.append('}')
    lines.append('if (g7 gt 1) {g7 -= 1;} <!-- count number of steps until smiley is to be placed at next opportunity -->')
    lines.append(f'if ((g9 &amp; 0xFF00) == 256 * {intersection}) {{g4 |= 0x20;}} <!-- smiley at current intersection ({intersection}) -->')

    line_groups.append(lines)
    lines = []

    for idx_origin, prev in enumerate(origins[intersection]):

        if idx_origin >= 1:
            line_groups.append(lines)
            lines = []

        # field tuple: (number of steps, followed link index form start view)
        field = {i:(None,None) for i in intersections}

        start = (intersection,prev)

        field[start[0]] = (0,None)
        depth = 0
        while any(field[p][0] is None for p in intersections):
            depth += 1
            trace(field, start, depth)


        max_steps = max(v[0] for v in field.values())
        directions = len(routes[start])
        for steps in range(1, max_steps+1):
            for direction in range(directions):
                dst = [k for k, v in field.items() if v == (steps, direction)]

        brk_open = 0
        idx0 = min(intersections)

        lines.append(f'if (g0 == 0x{(start[0])+(start[1])*256:04X}) {{ <!-- (intersection {start[0]}, looking from {start[1]}) -->')
        brk_open += 1
        indent = ' '*2*brk_open

        for steps in range(1, max_steps+1):
            if True:
                indent = ' '*2*brk_open
                line = f'{indent}if (g4 == 0) {{'
                lines.append(line)
                #print(line)
                brk_open += 1

            indent = ' '*2*brk_open
            #print(f'{steps} step(s)')
            
            for direction in range(directions):
                mask_dir = directions-1-direction
                dst = [k for k, v in field.items() if v == (steps, direction)]
                mask = int(bitmask_fields(dst), 2)
                if (mask != 0):
                    destis = ','.join(str(v) for v in dst)
                    test = f'0x{mask:04X}'
                    line = f'{indent}if (g3 &amp; {test} != 0) {{g4 += {2**mask_dir};}} <!-- stars at {destis} in direction {orders[start][direction]} -->'
                    lines.append(line)
        line = '  ' + '}'*(brk_open-1)
        lines.append(line)
        brk_open = 1

        # menu layout:
        # menu 1/root: jump pad
        # then the starred menus for that view
        # then the unstarred menus for that view (which double as hinted w/o star)
        # then the hinted menus for that view
        # then the next view

        indent = ' '*2*brk_open

        new_menus = n_special_menus + 2**len(routes[start])
        
        # offset 1 accounts for the menu with the star at this very intersection
        men_off = menu_basis_offset + processed_menus

        lines.append(f'{indent}if ((g4 &amp; 0x20) != 0) {{jump menu {men_off};}} <!-- smiley at current intersection -->')
        lines.append(f'{indent}if ((g4 &amp; 0x40) != 0) {{jump menu {men_off + 1};}} <!-- star at current intersection -->')
        lines.append(f'{indent}if ((g4 &amp; 0x80) != 0) {{jump menu {men_off + 2};}} <!-- stars are not to be hinted -->')
        linked_menus.append([men_off, start,'smiley'])
        linked_menus.append([men_off+1, start,'star'])
        men_off += n_special_menus
        for i in range(2**len(routes[start])):
            if bin(i)[2:].count('1') == 0:
                comm = ' <!-- no stars left to find (never called) -->'
            elif  bin(i)[2:].count('1') > 3:
                comm = ' <!-- more than 3 stars (never called) -->'
            else:
                comm = ''
            line = f'{indent}if (g4 == 0x{i:02X}) {{jump menu {men_off + i};}}{comm}'
            lines.append(line)
            spos = bin(i)[2:]
            spos = '0' * (len(routes[start])-len(spos)) + spos
            linked_menus.append([men_off+i, start,f'spos{spos}'])

        lines.append(f'{indent}jump vmgm menu 3; <!-- error: illegal state -->')
        processed_menus += new_menus

        brk_open -= 1
        indent = ' '*2*brk_open
        lines.append(f'{indent}}}')

    lines.append('jump vmgm menu 3; <!-- error: illegal origin for this intersection -->')
    line_groups.append(lines)
    lines = None

    if not split_in_two:
        out = []
        for lines in line_groups:
            out += lines

        if len(out) > 50:
            # there are estimated too many instructions in this menu,
            #   so split menu in two
            return make_ts_code_block(intersection, split_in_two = True)
            
        output = [out], linked_menus
    else:
        ops = []
        out1 = []
        for idx, lines in enumerate(line_groups):
            if idx > 0:
                out1.append(f'<!-- titleset menu {idx+1} -->')
            out1 += lines
            if idx < len(line_groups)-1:
                out1.append(f'jump menu {idx + 2}; <!-- continue in next menu -->')
                ops.append(out1)
                out1 = []
            else:
                ops.append(out1)

        output = ops, linked_menus
    
    return output

if __name__ == '__main__':
    # test code generation
    code1, code2, linked_menus = make_ts_code_block(8)

    print(code1)
    if code2 is not None:
        print()
        print(code2)
