import sys
import curses
import io
import unicodedata

def main(filename):
    screen = curses.initscr()
    try:
        try:
            with open(filename, 'r+') as f:
                mainloop(f, screen)
        except FileNotFoundError:
            with open(filename, 'w+') as f:
                mainloop(f, screen)
    finally:
        curses.endwin()

def mainloop(f, screen):
    curses.noecho()
    screen.scrollok(True) # auto scroll screen
    screen.addstr(f.read()) # print contents of file
    while True:
        key = screen.get_wch()
        if key == 0:
            curses.beep()
        elif key == chr(3) or key == chr(17): # ctrl-c or ctrl-q
            break
        elif key == "\b" or key == chr(127): # backspace
            cur = f.tell()
            if cur == 0:
                curses.beep()
                continue
            num_bytes = 1
            while True:
                f.seek(cur - num_bytes, io.SEEK_SET)
                try:
                    value = f.read(num_bytes)
                except UnicodeDecodeError: # could be an emoji
                    num_bytes += 1
                    continue
                break
            if value == "\n":
                curses.beep()
                continue # can't delete lines

            unicode_width = unicodedata.east_asian_width(value)
            # https://stackoverflow.com/a/31666966
            # characters that take up 2 spaces, like emoji
            fullwidth = unicode_width == "A" or unicode_width == "F" or unicode_width == "W"

            crs_y, crs_x = screen.getyx()
            crs_x -= 2 if fullwidth else 1
            if crs_x == -1:
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
            if key == ord(6): # ctrl-f
                key = "🦊"
            if key == ord(20): # ctrl-t
                key = "🤔"
            f.write(key)
            screen.addstr(key)
            #screen.addstr(str(key)) # print key number for debugging

if __name__ == "__main__":
    main(sys.argv[1])
