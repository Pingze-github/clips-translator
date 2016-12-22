# coding=u8

'基本规则:高优先级语言字符存在则判断为高优先级语言'

lang_list = ['en','zh','jp'] #支持的语言类型

def Hs2D(string):
    string = string[::-1]
    demical = 0
    i = 0
    for char in string:
        if char.upper() == 'A':
            char_int = 10
        elif char.upper() == 'B':
            char_int = 11
        elif char.upper() == 'C':
            char_int = 12
        elif char.upper() == 'D':
            char_int = 13
        elif char.upper() == 'E':
            char_int = 14
        elif char.upper() == 'F':
            char_int = 15
        else:
            char_int = int(char)
        demical = demical + char_int * 16 ** i
        i = i + 1
    return demical

def check(string):
    if isinstance(string,str):
        string = string.decode('u8')
    for char in string:
        char_repr = repr(char)
        if '\u' in char_repr:
            char_code = char_repr[4:-1] #即Unicode码值
            char_value = Hs2D(char_code)
            if Hs2D('3040')<char_value<Hs2D('30ff') or Hs2D('31f0')<char_value<Hs2D('31ff'):
                return lang_list[2]
            elif Hs2D('2e80')<char_value<Hs2D('2fdf') or Hs2D('3400')<char_value<Hs2D('4dbf') or Hs2D('4e00')<char_value<Hs2D('9fff'):
                return lang_list[1]
    return lang_list[0]

def main():
    print check('中文')
    print check('English')
    print check('ミン')

if __name__ == '__main__':
    main()
