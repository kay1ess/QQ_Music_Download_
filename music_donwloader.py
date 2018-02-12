from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QThread, QObject, QBasicTimer, pyqtSlot
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import  QIcon
import json
from urllib.parse import urlencode
import sys
import os
import requests
from PyQt5.QtWidgets import QFileDialog, QCheckBox
from os.path import isfile
from selenium import webdriver
import time

#计划内容：
#1.多线程解决长操作体验
#2.加入文件保存路径选择
#3.加入变量设置
#4.异常处理

class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.file_name = None
        self.text =None
        self.ls, self.muisc_ls = [], []
    def initUI(self):
        H_header = ['歌曲名', '歌手', '专辑', '下载链接']
        self.resize(900, 720)
        self.desktop = QtWidgets.QApplication.desktop()
        x = (self.desktop.width() - self.width()) // 2
        y = (self.desktop.height() - self.height()) // 2
        self.move(x, y)
        self.setWindowIcon(QIcon('qqmusic.jpg'))
        self.setWindowTitle('QQ音乐下载器')
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setRowCount(20)
        self.table.setHorizontalHeaderLabels(H_header)

        self.table.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)
        #双击不能修改表单元格内容
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        #不显示网格
        self.table.setShowGrid(False)

        self.search_text = QtWidgets.QLineEdit('在这里输入歌曲名：')
        #默认文本框内容全选 光标放置在文本框
        self.search_text.selectAll()
        self.search_text.setFocus()
        #搜索 button
        self.search_btn = QtWidgets.QPushButton('搜索')

        #w文本框和搜索按钮获取到 文本框中的内容
        self.search_text.returnPressed.connect(self.get_list)
        self.search_btn.clicked.connect(self.get_list)

        self.native = QCheckBox()
        self.native.setText("Use native file dialog.")
        self.native.setChecked(True)
        #页面布局
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.search_text)
        hbox.addWidget(self.search_btn)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        #vbox.addWidget(self.test_lable)
        vbox.addWidget(self.table)
        self.setLayout(vbox)

    @pyqtSlot()
    def get_list(self):
        #self.test_lable.setText(text)
        self.text = self.search_text.text()
        self.btns = []

        self.music_ls = get_info(self.ls, self.text)
        print(self.music_ls)
        try:
            for i in range(20):
                for j in range(3):
                    self.table.setItem(i, j, QtWidgets.QTableWidgetItem(self.music_ls[i][j]))
                    self.table.resizeColumnsToContents()
                    self.table.resizeRowsToContents()
                self.btn = QtWidgets.QPushButton('下载')
                self.table.setCellWidget(i, 3, self.btn)
                    #重写btn的state 所以需要用到state和a

                self.btn.clicked.connect(lambda state, a = i: self.get_download(a))
        except Exception as e:

            QtWidgets.QMessageBox.warning(self, '搜索失败','搜索出现异常，请尝试更换关键词，错误代码为：'+ str(e))
            pass
    def get_download(self, i):
        self.music_name = self.music_ls[i][0]
        self.music_singer = self.music_ls[i][1]
        self.save_file_gui(self.music_name, self.music_singer, i)




    def save_file_gui(self, music_name, singer, i):

        self.file_name, extension = QFileDialog.getSaveFileName(self,
                                               'save music',
                                                '/Users/Kay/Music/'+music_name+'_'+singer+'.mp3'

                                                  )

        self.music_url = self.music_ls[i][3]
        obj = Get_Download_Url(self.music_url)
        obj.start()

        obj.download_song_signal.connect(self.download_music)

    def download_music(self, download_url):
        print(download_url)
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }

        try:
            r = requests.get(download_url, headers=headers, timeout=30)
            r.raise_for_status()

            with open(self.file_name, 'wb') as file:
                file.write(r.content)
                file.close()
                print(self.music_name + 'Download Finished')
                self.success_info()

        except Exception as e:
            print('Download Error, Reason:', e)
            self.failed_info()


    def success_info(self):
        QtWidgets.QMessageBox.information(self, '下载成功', self.music_name+'.mp3 下载成功')


    def failed_info(self):
        QtWidgets.QMessageBox.warning(self, '下载失败', self.music_name+'.mp3 下载失败请重新尝试')


class Get_Download_Url(QThread, QObject):
    download_song_signal = pyqtSignal(str)

    def __init__(self , music_url):
        #继承父类构造方法
        super(Get_Download_Url, self).__init__()
        self.music_url = music_url
        #加入选项 禁用加载图片 禁用图形运行 禁用声音
        self.option = webdriver.ChromeOptions()
        self.prefs = {
            "profile.managed_default_content_settings.images": 2
        }
        self.option.add_argument('--headless')
        self.option.add_argument('--mute-audio')
        self.option.add_experimental_option('prefs', self.prefs)
        self.obj = webdriver.Chrome(chrome_options=self.option)


        #self.obj.maximize_window()
    #模拟浏览器 点击试听，然后等待加载获得歌曲的url
    def get_url(self, music_url):
        self.obj.set_page_load_timeout(10)
        try:
            #time.sleep(30)
            self.obj.get(music_url)

            time.sleep(3)

            self.obj.find_element_by_class_name("js_all_play").click()

            time.sleep(3)
            windows = self.obj.window_handles
            self.obj.switch_to.window(windows[-1])
            #self.obj.find_element_by_class_name("icon_txt").click()
            #WebDriverWait(self.obj, 20, 1).until()
            #切换窗口句柄 到当前
            time.sleep(6)
            self.download_url = self.obj.find_element_by_css_selector("#h5audio_media source").get_attribute("src")
            self.obj.quit()
            print(self.download_url)
            return self.download_url
        except Exception as e:
            print(" Selenium is Error", e)
            self.obj.quit()
            QtWidgets.QMessageBox.warning(self,'服务器异常', '抱歉！该歌曲下载出现异常，无法下载，错误代码：'+str(e))


    def run(self):
        download_url = self.get_url(self.music_url)
        self.download_song_signal.emit(download_url)







def get_html(keyword):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        't': 0,
        'cr': 1,
        #翻页
        #'p': 1,
        #定义搜索结果的数目，每页20
        'n': 20,
        'w': keyword,
        'format': 'json'

    }
    url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?' + urlencode(headers)
    try:
        r = requests.get(url, timeout=30)
        r.encoding = 'utf-8'
        r.raise_for_status()
        return r.text
    except:
        print('Html Error')
        return None


#获取到 歌曲对应的ID号码
def parse_html(html):
    data = json.loads(html)
    song_data = data.get('data')
    song = song_data.get('song')
    list = song.get('list')
    if list:
        for l in list:
            if l.get('media_mid'):
                music_name = l.get('songname')
                music_id = l.get('media_mid')
                music_albumname = l.get('albumname')
                if music_albumname == '   ':
                    music_albumname = '>>>--未知专辑--<<<'
                singer_temp = l.get('singer')
                singer = singer_temp[0].get('name')
                yield (music_name, singer, music_albumname, music_id)

def get_info(ls, keyword):
    html = get_html(keyword)
    music_id = parse_html(html)
    music_name, singer, music_album, music_url = [], [], [], []

    for item in music_id:
        music_name.append(item[0])
        singer.append(item[1])
        music_album.append('《' + item[2] + '》')
        music_url.append(u'https://y.qq.com/n/yqq/song/' + item[3] + u'.html')
    #print(music_name, singer, music_album, music_url)
    for i in range(len(music_name)):
        #print("Downloading" + ">>>>>" + music_name[i] + '-----' + singer[i] + "-----" + music_album[i])
        csv_ls_temp = [music_name[i], singer[i], music_album[i], music_url[i]]
        ls.append(csv_ls_temp)

    return ls

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    table = MyWindow()
    table.show()
    sys.exit(app.exec_())