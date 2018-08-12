import sys
import curses
import io
import unicodedata

def main(filename):
    screen = curses.initscr()
    try:
        try:
            # 'r+': reading/writing, start at beginning, don't create
            with open(filename, 'r+') as f:
                mainloop(f, screen)
        except FileNotFoundError:
            # 'w+': create new file for reading/writing
            with open(filename, 'w+') as f:
                mainloop(f, screen)
    finally:
        curses.endwin()

def mainloop(f, screen):
    curses.noecho() # don't write characters as they are typed
    screen.scrollok(True) # auto scroll screen

    screen.addstr(f.read()) # print contents of file

    while True:
        key = screen.get_wch()
        if key == 0:
            curses.beep()
        elif isinstance(key, int):
            # special function key
            pass
        elif key == chr(3) or key == chr(17): # ctrl-c or ctrl-q
            # quit
            return
        elif key == "\b" or key == chr(127): # backspace
            cur = f.tell() # location in file
            if cur == 0: # at start of file
                curses.beep()
                continue
            num_bytes = 1 # byte length of the previous character
            while True:
                # find the smallest set of bytes that can be decoded
                f.seek(cur - num_bytes, io.SEEK_SET)
                try:
                    value = f.read(num_bytes)
                except UnicodeDecodeError:
                    num_bytes += 1
                    continue
                break
            if value == "\n":
                # at the start of the line. can't delete lines
                curses.beep()
                continue

            unicode_width = unicodedata.east_asian_width(value)
            # https://stackoverflow.com/a/31666966
            # characters that take up 2 spaces, like emoji
            fullwidth = unicode_width == "A" or unicode_width == "F" or unicode_width == "W"
            if ord(value) < 32:
                fullwidth = True # control character, starts with ^

            crs_y, crs_x = screen.getyx()
            if fullwidth:
                # delete the right half of a fullwidth character
                crs_x -= 1
                screen.move(crs_y, crs_x)
                screen.delch()
            crs_x -= 1
            if crs_x == -1:
                # at left edge of screen. wrap around.
                _, width = screen.getmaxyx()
                crs_x = width - 1
                crs_y -= 1
            screen.move(crs_y, crs_x)
            screen.delch()
            f.seek(cur - num_bytes, io.SEEK_SET) # move back one character
            f.truncate(f.tell()) # delete character from file
        elif key == "\n" or key == "\r": # enter
            f.write("\n")
            f.flush()
            crs_y, _ = screen.getyx()
            crs_y += 1
            height, _ = screen.getmaxyx()
            if crs_y == height:
                screen.scroll()
                crs_y = height - 1
            screen.move(crs_y, 0)
        else:
            if key == chr(6): # ctrl-f
                key = "🦊"
            if key == chr(20): # ctrl-t
                key = "🤔"
            f.write(key)
            screen.addstr(key)
            #screen.addstr(str(key)) # print key number for debugging

if __name__ == "__main__":
    main(sys.argv[1])
