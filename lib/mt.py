# coding=u8

from threading import Thread
import time

class Timing(Thread):
    def __init__(self,time,target):
        super(Timing,self).__init__(target=target)
        self.time = time
        self.target = target
        self.setDaemon(True)
    def run(self):
        while(1):
            self.target()
            time.sleep(self.time)

def do():
    print time.time()

if __name__ == '__main__':
    t = Timing(1,do)
    t.start()
    time.sleep(5)

