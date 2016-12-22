# coding=u8

import psutil
import os

filename = 'pid.log'

def writePid():
    pid = os.getpid()
    with open(filename,'w') as file:
        file.write(str(pid))
        file.flush()
    file.close()

def readPid():
    with open(filename,'r') as file:
        pid = file.read()
    file.close()
    try:
        pid = str(pid)
    except ValueError:
        pid = -1
    return pid

def check():
    if os.path.exists(filename) and os.path.isfile(filename):
        pid_running = readPid()
    else:
        pid_running = -1
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if int(p.pid) == int(pid_running):
            return False
    writePid()
    return True



if __name__ == '__main__':
    writePid()
    print readPid()
