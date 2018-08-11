import sys
import curses
import io

def main(filename):
    screen = curses.initscr()
    with open(filename, 'r+') as f:
        screen.addstr(f.read())
        while True:
            key = screen.getch()
            if key == 3: # ctrl-c
                break
            if key == 8: # backspace
                f.seek(f.tell() - 1, io.SEEK_SET) # move back one character
                f.truncate(f.tell()) # delete character from file
                screen.delch()
            else:
                f.write(chr(key))
    curses.endwin()


if __name__ == "__main__":
    main(sys.argv[1])
