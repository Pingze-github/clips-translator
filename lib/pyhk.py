# coding=u8
# author: wang719695@gmail.com

import pythoncom  
import pyHook
import win32api
from threading import Thread


'''
自建注册系统热键库
'''
'为使translator正常使用，考虑禁止ESC记录进Down_list'

down_list = [] #按下的键
func_key = {} #注册的字典列表

def check():
    for func in func_key:
        if set(down_list) == set(func_key[func]):
            func()

def register(func_key_give):
    global func_key
    func_key = func_key_give

def KeyDownEvent(event):
    key = event.Key
    if key not in down_list and key != 'Escape':
        down_list.append(key)
    check()
    return True
   
def KeyUpEvent(event):
    key = event.Key
    if key in down_list: 
        down_list.remove(key) #列表的remove键只去掉一个
    return True


def hook():
    #创建hook句柄  
    hm = pyHook.HookManager()  
    hm.KeyDown = KeyDownEvent  
    hm.KeyUp = KeyUpEvent  
    hm.HookKeyboard()  
    pythoncom.PumpMessages(10000)  

class pyhk(object):
    def __init__(self,func_key):
        super(pyhk,self).__init__()
        register(func_key)

    def start(self):
        global hook_thread
        hook_thread = Thread(target=hook)
        hook_thread.setDaemon(True)
        hook_thread.start()

# ****** test ******

def do():
    print('****** do something *******')

def main():
    dic={
        do:['F1','Lmenu']
    }
    p = pyhk(dic)
    p.start()
    # time.sleep(10)



if __name__ == '__main__':
    main()

