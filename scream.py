import sys
import curses
import io

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
        key = screen.getch()
        if key == 3 or key == 17: # ctrl-c or ctrl-q
            break
        elif key == 8 or key == 127: # backspace
            cur = f.tell()
            f.seek(cur - 1, io.SEEK_SET)
            value = f.read(1)
            if value == "\n":
                curses.beep() # can't delete lines
            else:
                crs_y, crs_x = screen.getyx()
                crs_x -= 1
                if crs_x == -1:
                    _, width = screen.getmaxyx()
                    crs_x = width - 1
                    crs_y -= 1
                screen.move(crs_y, crs_x)
                screen.delch()
                f.seek(cur - 1, io.SEEK_SET) # move back one character
                f.truncate(f.tell()) # delete character from file
        elif key == 10 or key == 13: # enter
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
            f.write(chr(key))
            screen.addch(key)
            #screen.addstr(str(key)) # print key number for debugging

if __name__ == "__main__":
    main(sys.argv[1])
