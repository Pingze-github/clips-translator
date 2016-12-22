# coding=u8


'toolBar成为主窗口一部分，通过hide和resize显隐，任何操作不会转移焦点 --- 最好方案'
'监听剪贴板，预先访问'
'窗口非置顶化'


import sys, os
sys.path.append('./lib')

# For py2exe
# if sys.executable.endswith("pythonw.exe"): 
#   sys.stdout = open(os.devnull, "w");
#   sys.stderr = open(os.path.join(os.getenv("TEMP"), "stderr-"+os.path.basename(sys.argv[0])), "w")

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from threading import Thread
from threading import Timer
import urllib
import json
# 自建库
from creeper import *
import pyhk
import mtget
import checkLang
import qlist
from cprint import cprint
from mt import Timing

# 全局变量

result_text = ''
original_last = ''
state = 0 
state_last = 0
clip_last = ''
result_list = qlist.qlist(10)

# 资源路径
icon = './icon/translator.png'
html_none = './html/none.html'
html_404 = './html/404.html'
html_null = './html/null.html'
html_suffix = './html/suffix.html'
html_prefix = './html/prefix.html'
html_loading = './html/loading.html'
html_netError = './html/netError.html'

'''程序状态字state: 
    0: 获取单词解释
    1：获取长句解释
    2：剪贴板无实义字符
    3：未找到相关结果
    4：未成功访问
    5：重复查询文本
'''

# 基本函数

def setClip(string):
    mimeData = QMimeData()
    clipboard = QApplication.clipboard()
    mimeData.setText(string)
    clipboard.setMimeData(mimeData) 

def getClip():
    mimeData = QMimeData()
    clipboard = QApplication.clipboard()
    clip = clipboard.text()
    clip = unicode(clip)
    return clip

def show():
    # print('Keypressed, show() run')
    translator.signal_show.emit()

def readHtml(path):
    with open(path,'r') as f:
        html = f.read()
    f.close()
    if isinstance(html,str):
        return html.decode('utf-8')
    else:
        return html

def checkResult(result):
    if result == 3:
        state = 3
        result = readHtml(html_none)
        return (state,result)
    elif result == 4:
        state = 4
        result = readHtml(html_404)
        return (state,result)
    elif result == 5:
        state = 5
        result = readHtml(html_netError)
        return (state,result)
    elif result == 6:
        state = 6
        result = result_list.newest()
        return (state,result)

# ****** 主翻译执行函数 ******

def translate(original):
    # clip = getClip()
    # (state,result) = update_baidu(original) # 选择
    (state,result) = update_iciba(original) # 选择
    # print('***GOT RESULT***')
    global state_last #记录上一次状态
    state_last = state
    if result != result_list.newest():
        result_list.put(result)
    # print('[STATE:{}]'.format(state))


# ****** 获取更新翻译 Baidu ******

def from_baidu(original,lang_type):
    # 需要自行判断原文是何种语言
    original = original.replace('/','').strip() # 去掉分隔符和手尾空格
    # original = original.replace('\n','') #去除换行符
    # print(original)
    global original_last
    if original == original_last and (state_last < 2 or state == 6):
        return 6
    else:
        original_last = original[:]
    url = 'http://fanyi.baidu.com/v2transapi'
    payload = {}
    payload['query'] = original
    payload['from'] = lang_type
    if lang_type == 'zh':
        payload['to'] = 'en'
    elif lang_type == 'en' or lang_type == 'jp':
        payload['to'] = 'zh'
    # print('start post')
    cp = Creeper(url,params=payload)
    response = cp.post()
    print(response.url)
    if response == False:
        return 5
    else:
        html = cp.get_html()
    if response.status_code!=200:
        return 4
    # print(response.url)
    translation = json.loads(response.text.decode('utf-8'))
    return translation

def update_baidu(original):
    prefix = readHtml(html_prefix)
    suffix = readHtml(html_suffix)
    global state, result_text
    if original == (u'\r\n' or u'\r' or u'\n') or original.strip() == u'':
        result = readHtml(html_null)
        state = 2
        return (state,result)
    lang_type = checkLang.check(original) # 自定义语言检查方法(http://fanyi.baidu.com/langdetect 可以在线检查)
    result = from_baidu(original,lang_type)
    return_check_value  = checkResult(result)
    # print('result_check_value {}'.format(return_check_value))
    if return_check_value != None:
        (state,result) = return_check_value
    else:
        trans_result = result['trans_result']
        # pprint(trans_result)
        dict_result = result['dict_result']
        if isinstance(dict_result,dict):
            state = 0
            result_text = ''
            simple_means = dict_result['simple_means']
            word_name = simple_means['word_name']
            symbols = simple_means['symbols']
            result = prefix
            result = result + '<div class="key"><span class="key">' + word_name + '</span>'
            if lang_type == 'zh':
                if 'word_symbol' in symbols[0]:
                    word_symbol = symbols[0]['word_symbol']
                    if len(word_symbol) > 0:
                        word_symbol = '[' + word_symbol + ']'
                        result = result + '<span class="key_speak">' + word_symbol + '</span></div>'
                result = result + '<hr class="line"><div class="value">'
                part_list = symbols[0]['parts']
                for part in part_list:
                    part_name = part['part_name']
                    if len(part_name) < 1:
                        part_name = part['means'][0]['part']
                    result_text = result_text + part_name
                    result = result + '<li class="short-value"><span class="prop">' + part_name + '</span>'
                    mean_list = part['means']
                    for mean in mean_list:
                        if 'word_mean' in mean:
                            mean = mean['word_mean']
                        mean = mean + u'；'
                        result_text = result_text + mean
                        result = result + '<span>' + mean + '</span>'
                    result = result + '</li>'
            elif lang_type == 'en':
                ph_en = symbols[0]['ph_en']
                if ph_en != None and ph_en != '':
                    ph_en = u'英 ['+ph_en+']'
                ph_am = symbols[0]['ph_am']
                if ph_am != None and ph_am != '':
                    ph_am = u'美 ['+ph_am+']'
                result = result + '<span class="key_speak">' + ph_am + '</span>' + '<span class="key_speak">' + ph_en + '</span></div>'
                result = result + '<hr class="line"><div class="value">'
                part_list = symbols[0]['parts']
                for part in part_list:
                    part_name = part['part']
                    result_text = result_text + part_name
                    result = result + '<li class="short-value"><span class="prop">' + part_name + '</span>'
                    mean_list = part['means']
                    for mean in mean_list:
                        mean_value = mean + u'；'
                        result_text = result_text + mean_value
                        result = result + '<span>' + mean_value + '</span>'
                    result = result + '</li>'       
            result = result+suffix
            # print('result_text:'+result_text)
        else:
            state = 1
            result_key_html = ''
            result_value_html = ''
            for data in trans_result['data']:
                result_key_text = data['src']
                result_value_text = data['dst']
                result_key_html = result_key_html + '<li class="long-key">' + result_key_text + '</li>'
                result_value_html = result_value_html + '<li class="long-value">' + result_value_text + '</li>'
            html_line = '<hr class="line">'
            result = '<div class="key">' + result_key_html + '</div>' + html_line + '<div class="value">' + result_value_html + '</div>'
            result_text = result_value_text
            result = prefix+result+suffix
            # print('result_text:'+result_text)
    return (state,result) 
        # if len(result_text) == 0:
        #     state = 3
        #     result = readHtml(html_none)

# ****** 获取更新翻译 ICIBA ******

def from_iciba(original):
    original = original.replace('/','').strip() # 去掉分隔符和手尾空格
    # print(original)
    global original_last
    if original == original_last and (state_last < 2 or state == 6):
        return 6
    else:
        original_last = original[:]
    url_prefix = 'http://www.iciba.com/'
    original = urllib.quote(original.encode('u8'))
    original = string_removeall(original,['%00','%0D','%0A'])
    url = url_prefix + original
    # print(url)
    response = mtget.mtget(url) 
    if response == False or response==None:
        return 5
    else:
        html = response.text
    if response.status_code!=200:
        return 4
    elif ('class="result-none-tip"' or 'class="suggest_b"') in html:
        return 3
    else:
        translation = re_find('<div class="in-base">(.+?</ul>)',html)
        if 'base-bt-bar' in translation:
            translation = re_find('<div class="in-base">(.+?)<div class="base-top-voice">',html)
        return translation

def update_iciba(original):
    prefix = readHtml(html_prefix)
    suffix = readHtml(html_suffix)   
    # # print(repr(original))
    global state, result_text
    if original == (u'\r\n' or u'\r' or u'\n') or original.strip() == u'':
        result = readHtml(html_null)
        state = 2
        return
    result = from_iciba(original)
    return_check_value  = checkResult(result)
    if return_check_value != None:
        (state,result) = return_check_value
    else:
    # 统计字符占位
        if 'class="base-list switch_part"' in result:
            state = 0
            result_key_html = re_find('(<h1 class="keyword">.+?)<ul class="base-list switch_part"',result)
            result_key_text = re_find('<h1 class="keyword">(.+?)</h1>',result_key_html)
            result_key_speak_text = re_find('<div class="base-speak">(.+?)</span>',result_key_html)
            result_key_speak_text = result_key_speak_text[result_key_speak_text.rfind('>')+1:]
            result_key_html = '<span class="key">' + result_key_text + '</span>'
            result_key_speak_html = '<span class="key_speak">' + result_key_speak_text + '</span>'

            result_value_html = re_find('<ul class="base-list switch_part".+?>(.+?)</ul>',result)
            result_value_html = result_value_html.replace('clearfix','short-value').replace('<p>','').replace('</p>','')
            html_line = '<hr class="line">'
            result = '<div class="key">' + result_key_html + result_key_speak_html + '</div>' + html_line + '<div class="value">' + result_value_html + '</div>'
            spans = re_findall('<span>(.+?)</span>',result_value_html)
            result_text = '' 
            for span in spans:
                result_text = result_text + span
        else:
            state = 1
            result_key_html = re_find('(<h1 class="keyword".+?</h1>)',result)
            result_key_text = re_find('>(.+?)<',result_key_html)
            result_key_html = '<li class="long-key">' + result_key_text + '</li>'
            result_value_html = re_find('(<div style="margin-top: 40px; text-align: left;">.+?</div>)',result)
            result_value_text = re_find('>(.+?)<',result_value_html)
            result_value_html = '<li class="long-value">' + result_value_text + '</li>'
            html_line = '<hr class="line">'
            result = '<div class="key">' + result_key_html + '</div>' + html_line + '<div class="value">' + result_value_html + '</div>'
            result_text = result_value_text
            if len(result_text) == 0:
                state = 3
                result = readHtml(html_none)
                return
        result = prefix+result+suffix
        result_last = result[:]
        # print('result_text:'+result_text)
    return (state,result) 



# ****** 线程类 ******
class Translate_thread(Thread):
    def __init__(self,original):
        super(Translate_thread,self).__init__()
        self.original = original
        self.result = None
        self.setDaemon(True)
    def run(self):
        translate(self.original)
        self.result = result_list.newest()
        translator.signal_translate_done.emit()

# ****** QTGUI类 ******

class MyWebView(QWebView):
    def __init__(self,parent=None):
        super(MyWebView,self).__init__(parent=parent)
        self.frame = self.page().mainFrame()
        self.setMouseTracking(True)
        self.frame.setScrollBarPolicy(Qt.Vertical,Qt.ScrollBarAsNeeded)
        self.frame.setScrollBarPolicy(Qt.Horizontal,Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("QScrollBar:vertical{background-color:red;width:5px}QScrollBar::handle:vertical{background-color:red}")
    # def wheelEvent(self, event): #启用和隐藏进度条，不再需要此方法
    #     numSteps = -event.delta()/4  #每步补正
    #     self.frame.scroll(0,numSteps)
    #     event.accept()  #接收该事件

class SimpleTranslator(QWebView):
    def __init__(self):
        super(SimpleTranslator,self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint|Qt.Tool)
        self.setHtml(result_list.this())
        self.show()


class Translator(QWidget):
    signal_show = pyqtSignal()
    signal_translate_done = pyqtSignal()
    signal_notActive = pyqtSignal()
    def __init__(self):
        super(Translator,self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True) # 主窗体透明化
        self.setMaximumWidth(500)
        self.setMouseTracking(True)
        self.toolBar = ToolBar()
        self.toolBar.hide()
        self.viewContainer = QWidget()
        self.viewContainer.setFixedWidth(500)
        self.viewContainer.setStyleSheet('QWidget{background:#141414;}')
        self.view = MyWebView(self.viewContainer)
        self.viewContainer.setMinimumHeight(90) # 确保单行空间不被压榨
        self.createTrayIcon()
        self.trayIcon.show()
        self.desktop = QApplication.desktop()
        # 主栏布局
        mainlayout = QVBoxLayout()
        mainlayout.addWidget(self.viewContainer)
        self.label = QLabel()
        self.label.setMinimumHeight(30) # ***关键句，预先使主栏足够高，避免了侧栏显示时的变化
        mainlayout.addWidget(self.label) #直接加label会过度压榨view空间
        # 侧栏布局
        barlayout = QVBoxLayout()
        barlayout.setMargin(0)
        barlayout.addWidget(self.toolBar)
        barlayout.addWidget(QLabel()) # OK，使toolBar贴边
        # self.toolBar.setAlignment(Qt.AlignTop)
        # barlayout.addSpacerItem(QSpacerItem(0,0)) # 会导致窗口过大
        # label.setMaximumHeight(1) #会使toobar不居于上边
        # 总布局
        layout = QHBoxLayout(self)
        layout.setMargin(0)
        layout.addLayout(mainlayout)
        layout.addLayout(barlayout)
        # self.toolBar.setGeometry(500,0,22,22*6)
        # viewContainer布局
        vclayout = QHBoxLayout()
        vclayout.setMargin(15)
        vclayout.addWidget(self.view)
        self.viewContainer.setLayout(vclayout)
        # 定时线程
        global timer_toolBar_hide
        timer_toolBar_hide = Timer(0.5,self.hideToolBar)
        # 信号
        self.signal_show.connect(self.showWindow)
        self.signal_translate_done.connect(self.autoShowWindow)
        self.signal_notActive.connect(self.hideWindow)
        # 清空
        self.clear()

    def createTrayIcon(self):
        self.quitProAction = QAction(u"退出", self, triggered=quitPro)
        self.trayIconMenu = QMenu(self)
        self.trayIconMenu.addAction(self.quitProAction)
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.setIcon(QIcon(icon))

    def autosize(self,html):
        print 'autosize() run'
        width = 500
        if html != result_list.newest():
            # print(result_list.point())
            self.resize(width,result_list.restoreMore(html))
            self.repaint()
        # self.resize(width,0) #由于运行效率问题，有时会闪烁一下
        # 考虑对每个词条储存大小，这里resize到对应大小(不好操作)
        self.show()
        scroll_value = self.view.frame.scrollBarMaximum(Qt.Vertical)
        print (scroll_value)
        if scroll_value > 0:
            height = self.height() + scroll_value  #可以考虑是否能手动补正
            if height > 400:
                height = 400
            result_list.storeMore(html,height)
            self.resize(width,height)
            # self.label.setMaximumHeight()
            # self.viewContainer.setMaximumHeight(height)
            if height-22 < 130:
                self.label.setMinimumHeight(152-(height-22)-10)
            self.repaint()
        else:
            result_list.storeMore(html,self.height())

    def hideWindow(self):
        # print('hideWindow() run')
        result_list.repoint()
        self.hide()
        self.toolBar.hideWindow()
        self.clear()

    def showWindow(self):
        print 'Signal got, showWindow() run'
        self.move(self.desktop.width()/2-self.width()/2, self.desktop.height()/2 - 200)
        self.show()
        if not translate_thread.isAlive():
            html = translate_thread.result
            self.view.setHtml(html)
            self.autosize(html)
        self.raise_()
        self.raise_()
        self.raise_()
        self.raise_()
        self.activateWindow()

    def autoShowWindow(self):
        html = translate_thread.result
        self.view.setHtml(html)
        if self.isVisible():
            self.autosize(html)
        # html = translate_thread.result
        # print('HTML: {}'.format(html[:10]))
        # self.refresh(html)

    def refresh(self,html):
        self.view.setHtml(html)
        self.autosize(html)    

    def clear(self):
        # print('clear() run')
        self.view.setHtml(readHtml(html_loading))
        self.label.setMinimumHeight(152-90) #调节‘正在查询’view大小
        self.resize(500,90)
        self.repaint()

    # def eventFilter(self,source,event):
    #     if event.type() == QEvent.WindowDeactivate and source == self: #有时无效
    #         print('**Deactivate')
    #         self.hideWindow()
    #     return QWidget.eventFilter(self, source, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hideWindow()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            QApplication.postEvent(self, QEvent(174))
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    def enterEvent(self,event):
        print('main enter')
        timer_toolBar_hide.cancel()
        self.toolBar.showWindow()

    def leaveEvent(self, evnet):
        print('main leave')
        global timer_toolBar_hide
        timer_toolBar_hide = Timer(0.5,self.toolBar.hideWindow)
        timer_toolBar_hide.start()

    def hideToolBar(self):
        # print('hideToolBar() run')
        self.toolBar.hideWindow()


class ToolBar(QWidget):
    signal_show = pyqtSignal()
    signal_hide = pyqtSignal()

    def __init__(self,parent=None):
        super(ToolBar,self).__init__(parent)
        self.setWindowFlags(Qt.SubWindow|Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint)
        # self.setWindowFlags(Qt.SubWindow|Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint)
        self.bt_close = QPushButton('X')
        self.bt_save = QPushButton('S')
        self.bt_stick = QPushButton('T')
        self.bt_copy = QPushButton('C')
        self.bt_left = QPushButton('<')
        self.bt_right = QPushButton('>')
        self.bt_close.setToolTip(u'关闭/销毁')
        self.bt_save.setToolTip(u'储存HTML到文件')
        self.bt_stick.setToolTip(u'粘贴到屏幕')
        self.bt_copy.setToolTip(u'复制结果到剪贴板')
        self.bt_left.setToolTip(u'前一条')
        self.bt_right.setToolTip(u'后一条')
        self.connect(self.bt_close, SIGNAL('clicked()'), self.bt_close_func)
        self.connect(self.bt_save, SIGNAL('clicked()'), self.bt_save_func)
        self.connect(self.bt_stick, SIGNAL('clicked()'), self.bt_stick_func)
        self.connect(self.bt_copy, SIGNAL('clicked()'), self.bt_copy_func)
        self.connect(self.bt_left, SIGNAL('clicked()'), self.bt_left_func)
        self.connect(self.bt_right, SIGNAL('clicked()'), self.bt_right_func)
        layout = QVBoxLayout()
        layout.addWidget(self.bt_left)
        layout.addWidget(self.bt_right)
        layout.addWidget(self.bt_close)
        layout.addWidget(self.bt_save)
        layout.addWidget(self.bt_stick)
        layout.addWidget(self.bt_copy)
        layout.setMargin(0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.setFixedSize(22,22*6)
        file = QFile('ToolBar.qss')
        file.open(QFile.ReadOnly)
        styleSheet = QLatin1String(file.readAll())
        self.setStyleSheet(styleSheet)
        self.signal_show.connect(self.showWindow)
        self.signal_hide.connect(self.hideWindow)

    def showWindow(self):
        # print('showWindow() run')
        translator.setFixedWidth(524) 
        self.show() # 此行使窗口height扩大到toolbar+label，考虑在view下方加label

    def hideWindow(self):
        print('toolBar hide')
        translator.setFixedWidth(500)
        if not translator.isHidden() and not translator.isActiveWindow():
            translator.activateWindow()
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            translator.hideWindow()

    def bt_close_func(self):
        translator.hideWindow()
        # pprint(result_list.showMore()) 
    def bt_save_func(self):
        # print(type(result))
        filepath = QFileDialog.getSaveFileName(self,u'保存','traslation.html',"Doc(*.html)")
        if len(filepath) > 0:
            with open(filepath,'wb') as file:
                file.write(result.encode('u8'))
            file.close()
    def bt_stick_func(self):
        global simple_list
        simple_list = []
        simple_list.append(SimpleTranslator())
    def bt_copy_func(self):
        if state < 2:
            setClip(result_text)
            # print(result_text)
            # print('已保存到剪贴板')
    def bt_left_func(self):
        html = result_list.last()
        # translator.view.setHtml(html)
        translator.refresh(html)
    def bt_right_func(self):
        html = result_list.next()
        # translator.view.setHtml(html)
        translator.refresh(html)

def quitPro():
    timer_clip_check.cancel()
    timer_toolBar_hide.cancel()
    timer_active_check.cancel()
    app.exit()
    print('结束运行')
    sys.exit()

# ******　独立线程工作　******

def registerHK():
    func_key={
        show: ['F2','Lmenu']
    }
    global pk
    pk = pyhk.pyhk(func_key)
    pk.start()

def timingActiveCheck():
    global timer_active_check
    timer_active_check = Timer(0.5,activeCheck)
    timer_active_check.start()

def activeCheck():
    # print(translator.isActiveWindow())
    if not translator.isActiveWindow() and translator.isVisible():
        print('***NOT ACTIVE')
        #translator.signal_notActive.emit()
    timingActiveCheck()


def clipCheck():
    global clip_last,translate_thread
    clip = getClip() #应该检查下clip，转成字符串
    if clip_last != clip:
        print('***DIFF***')
        translate_thread = Translate_thread(clip)
        translate_thread.start()
        clip_last = clip
    timingClipCheck()

def timingClipCheck():
    timer_clip_check = Timer(0.5,clipCheck)
    timer_clip_check.start()

def main():
    global app, translator
    app = QApplication(sys.argv)
    # QApplication.setQuitOnLastWindowClosed(False)
    translator = Translator()
    app.installEventFilter(translator)
    registerHK() #注册快捷键
    timingActiveCheck()
    timingClipCheck()
    # translator.show()
    print('开始运行')
    sys.exit(app.exec_())

if __name__ == '__main__':
    import singleMe
    if singleMe.check() == True:
        main()
    else:
        print('You can only one instance of this program.'.upper())


'''
1.做好工具栏 (完成)
2.想办法实现移入移出事件，稳定工具栏 (利用enterEvent完成)
3.有时不能自动隐藏（未发现问题）
4.查询文本中存在"/"等符号时认为网址而返回404 (去掉/完成)
5.正确确认web页面大小   (利用scroll值确定)
6.重复查询文本缓存，免联网查询 （完成）
7.有时不能继续查询
8.点击工具栏后原起始窗口失去焦点 (？？？原因不明)
    尝试将工具栏与起始窗口设计为一个窗口
9.所有窗口失焦时，按快捷键，不能显示 (发现快捷键组Escape不能释放，初步解决)
    应当是快捷键失效(截图软件同样失效)
10.BUG: 快捷键收到 到 窗口激活 这段时间内 若恰做激活检查，会隐藏窗口 (完成)
    应在窗口激活并显示后再进行检查，窗口隐藏后检查中止
11.添加系统托盘 (完成)
12.金山词源改为百度api来源(done)
13.增加科林斯和英英词源(仅在词语状态下激活)
13.本子预先查询字段语言系统(本地代码检查)
14.工具栏添加：切换词源（金山（百度）、有道、海词、谷歌）
15.完成“贴到屏幕”功能 (初步完成)
16.完成“历史记录”功能和工具栏图标 (完成)
17.条目切换后 autosize失效。(储存height，完成)
18.该变工具栏位置，避免工具栏随内容四处移动(完成)
19.将工具栏与主窗口识别成同一窗口（使用局部透明或Mask）(完成)
    解决主窗口透明问题
20.解决剪贴板中分段文字处理问题
21.自动去除简书、豆瓣、知乎等网站的附加复制内容
22.调试BUG
23.中文词组搜索没有part
24.滑倒toolbar后返回toolbar隐藏（解决，去除toobar的event）
*25.找到代替label的无体积占位组件（未找到，使用setMaximumHeight()解决）
26.修改查询机制，单独线程检查剪贴板，发现更新后即后台访问。
    1.此状态下如何自动调整窗口
    2.清空机制
27.有时程序会未响应
    考虑重新进行事件与GUI分离
28.自动关闭有时无效
    使用另外线程检查是否激活
    实验发现是程序内部对窗口是否激活的isActivateWindow()返回结果不正确
        取消窗口置顶后有改善
'''
