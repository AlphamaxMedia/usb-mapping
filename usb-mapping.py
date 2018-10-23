#!/usr/bin/python3

import pyudev
import time
import curses
from curses import wrapper
import threading
import pickle

begin_x = 5
begin_y = 3
height = 30
width = 80

# these are x, y coordinates
nc_action = [2, 1]
nc_sysname = [2, 2]
nc_devpath = [2, 3]

nc_portarray = [2, 5]
portindex = 0
portname = 'NONAME'
port_dict = {portname:'INSERT DRIVE'}

nc_input = [2, height - 1]
nc_prompt = [0, height - 2]
prompt = "Hit q when done, or give this port a name: "
replprompt = "MAP> "
inputstr = ""

win = None
winLock = threading.RLock()

usb_mapping = {}

def log_event(action, device):
    global portname
    global port_dict
    global prompt

    with winLock:
        win.move(nc_action[1],nc_action[0])
        win.clrtoeol()
        win.addnstr(nc_action[1], nc_action[0], 'Action: ' + action, width)
        if device.device_type == 'partition':
            win.move(nc_devpath[1],nc_devpath[0])
            win.clrtoeol()
            win.addnstr(nc_devpath[1], nc_devpath[0], 'Device: ' + device.device_node, width)
        else:
            win.move(nc_sysname[1],nc_sysname[0])
            win.clrtoeol()
            win.addnstr(nc_sysname[1], nc_sysname[0], 'Sysname: ' + device.sys_name, width)

        if device.device_type == 'usb_interface' and action == 'add':
            port_dict.pop(portname)
            port_dict[portname] = device.sys_name
            portname = 'NONAME'
            port_dict[portname] = 'INSERT DRIVE'
            prompt = 'Hit q when done, or give the next port a name: '
        win.refresh()


def progmain(mainscr):
    global win
    global inputstr
    global portname
    global prompt

    mainscr.clear()

    win = curses.newwin(height, width, begin_y, begin_x)
    win.nodelay(1) # non-blocking input

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by('usb')
    monitor.filter_by('block')

    observer = pyudev.MonitorObserver(monitor, log_event)
    observer.start()

    while(True):
        with winLock:
            offset = 0
            for port in sorted(port_dict):
                if port == 'NONAME':
                    continue
                win.move(nc_portarray[1] + offset, nc_portarray[0])
                win.clrtoeol()
                win.addnstr(nc_portarray[1] + offset, nc_portarray[0], port + ":" + port_dict[port], width)
                offset = offset + 1

            win.border()
            win.move(nc_prompt[1], nc_prompt[0])
            win.clrtobot()
            win.addnstr(nc_prompt[1], nc_prompt[0], prompt, width)
            win.addnstr(nc_input[1], nc_input[0], replprompt, width)
            win.addnstr(nc_input[1], nc_input[0] + len(replprompt), inputstr, width-2)
            win.move(nc_input[1], nc_input[0] + len(inputstr) + len(replprompt))

            win.refresh()

        try:
            c = win.getch()
        except:
            c = ''

        time.sleep(0.05)

        if c == ord('q') or c == ord('Q'):
            if 'NONAME' in port_dict:
                port_dict.pop('NONAME')
            with open('usb_map.pkl', 'wb') as f:
                pickle.dump(port_dict, f, pickle.HIGHEST_PROTOCOL)
            observer.stop()
            return
        elif c in(curses.KEY_BACKSPACE, curses.KEY_DL, 127, curses.erasechar()):
            win.delch(nc_input[1], nc_input[0] + len(inputstr) + len(replprompt))
            inputstr = inputstr[:-1]
        elif c == ord('\n'):
            if inputstr != '':
                port_dict.pop(portname)
                port_dict[inputstr] = 'INSERT DRIVE'
                portname = inputstr
                inputstr = ''
                prompt = 'Insert disk into the corresponding port.'
        elif c != curses.ERR:
            inputstr = inputstr + chr(c)


def main():
    wrapper(progmain)

if __name__ == "__main__":
    main()