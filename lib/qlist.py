# coding=u8

'特殊列表，有最大长度，越新的元素越靠前，添加新元素时自动删去最旧元素'
'可以对应每个列表元素储存额外元素'
'不可直接调用pop（可以查看源文件解决问题）'

from pprint import pprint

class qlist(list):
    def __init__(self,maxlen):
        list.__init__([])
        self.maxlen = maxlen
        self.__pointer = 0
        self.__storeDict={}

    def put(self,item):
        self.insert(0,item)
        if self.__len__() > self.maxlen:
            item = self.pop(-1)
            if item in self.__storeDict:
                self.__storeDict.pop(item)
    def remove(self,item):
        item = self.pop(self.index(item))
        if item in self.__storeDict:
            self.__storeDict.pop(item)      
    def newest(self):
        if self.__len__() > 0:
            return self[0]
        else:
            return None
    def this(self):
        return self[self.__pointer]
    def last(self):
        if self.__pointer + 1 < self.__len__(): 
            self.__pointer = self.__pointer + 1
        return self[self.__pointer]
    def next(self):
        if self.__pointer - 1 >= 0:
            self.__pointer = self.__pointer - 1
        return self[self.__pointer]
    def point(self):
        return self.__pointer
    def pointto(self,index):
        if isinstance(index,int) and 0<=index<=self.__len__():
            self.__pointer = index
    def repoint(self):
        self.__pointer = 0
    def setlist(self,alist):
        if len(alist) < self.maxlen:
            self.clear()
            self[:] = alist
    def clear(self):
        self[:] = []
        self.__storeDict = {}
    def storeMore(self,item,item_more):
        if item in self[:]:
            self.__storeDict[item] = item_more
    def restoreMore(self,item):
        if item in self.__storeDict :
            return self.__storeDict[item]
    def popMore(self,item):
        if item in self.__storeDict :
            return self.__storeDict.pop(item)
    def showMore(self):
        for item in self.__storeDict.keys():
            print '{} : {}'.format(self.index(item),self.__storeDict[item])



if __name__ == '__main__':
    a = qlist(10)
    a.put(100)
    a.setlist([1,2,3,4,5])

    print a
    more = 100
    a.storeMore(3,more)
    print a.restoreMore(1)
    print a.restoreMore(3)
    a.remove(3)
    print a
    a.put(3)
    print a.restoreMore(3)
