from bs4 import BeautifulSoup
from PIL import Image
from dearpygui.core import *
from dearpygui.simple import *
import os
import pytesseract
import requests
import json
import time
import re
from tkinter import messagebox
import tkinter as tk

pic_fpath = "resource\\picf.png"
url_1 = 'http://202.119.81.113:8080'
url_2 = "http://202.119.81.113:8080/Logon.do?method=logon"
url_3 = "http://202.119.81.112:9080"
heard1 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75 '
}


def sel_title(x):
    return x.split("title")[1]


def sel_href(x):
    x1 = re.findall(pattern="href=\".*\"", string=str(x))[0]
    x2 = re.findall(pattern="\".*\"", string=str(x1))[0]
    x3 = str(x2).replace("\"", '')
    return x3


def replace_luoma(t: str, type: int):
    if type == 0:
        return t.replace('Ⅳ', '4').replace('Ⅲ', '3').replace('Ⅱ', '2').replace('Ⅰ', '1').replace('<br />',
                                                                                                 ' ').replace(
            '<font color=red>', '').replace('</font>', '')
    if type == 1:
        return t.replace('Ⅳ', '四工').replace('Ⅲ', '三工').replace('II', '二工').replace('I', '一工')
    if type == 2:
        p = re.compile('<br />(.+)')
        pp = p.findall(t)
        if pp:
            return pp[0]
        else:
            return t


class jwc:
    username = None
    keywords = None
    keys = None
    list = {}
    s = None
    rr = None
    islogin = False

    def __init__(self, username, keywords):
        self.username = username
        self.keywords = keywords
        self.s = requests.session()
        for i in range(0, 10):
            r = self.s.get(url_1 + '/verifycode.servlet', headers=heard1)
            f = open(pic_fpath, 'wb')
            f.write(r.content)
            f.close()
            self.keys = self.read_text()
            rr = self.s.post(url=url_2, headers=heard1, data={
                'USERNAME': self.username,
                'PASSWORD': self.keywords,
                'useDogCode': '',
                'RANDOMCODE': self.keys
            })
            if '学生个人中心' in rr.text.split('title')[1]:
                set_main_window_size(900, 1200)
                delete_item('loginwin', children_only=True)
                set_window_pos('loginwin', 0, 0)
                add_tab_bar('bar', parent='loginwin')
                self.rr = rr
                self.findhref()
                self.islogin = True
                break
            else:
                time.sleep(2)

    def read_text(self) -> object:
        # 验证码图片转字符串
        im = Image.open(pic_fpath)
        imgry = im.convert('L')
        # 二值化，采用阈值分割算法，threshold为分割点
        threshold = 127
        table = []
        for j in range(256):
            if j < threshold:
                table.append(0)
            else:
                table.append(1)
        out = imgry.point(table, '1')
        # 去除边框
        w, h = out.size
        width = 2
        pixdata = out.load()
        for x in range(width):
            for y in range(0, h):
                pixdata[x, y] = 255
        for x in range(w - width, w):
            for y in range(0, h):
                pixdata[x, y] = 255
        for x in range(0, w):
            for y in range(0, width):
                pixdata[x, y] = 255
        for x in range(0, w):
            for y in range(h - width, h):
                pixdata[x, y] = 255
        # 识别文本
        text = pytesseract.image_to_string(out, lang="eng", config='--psm 6')
        text = re.sub('[\W_]+', '', text)  # 删除其他多余字符
        text = text.replace('i', '1')
        return text

    def findhref(self):
        soup = BeautifulSoup(self.rr.text, 'html.parser')
        soup.find()
        list1 = soup.find(class_='wap')
        list2 = list1.find_all('a')
        for x in list2:
            x3 = sel_href(x)
            self.list[x.get_text().replace("\n", '')] = url_3 + x3

    def findhref_btn(self, rr, name):
        soup = BeautifulSoup(rr.text, 'html.parser')
        list1 = soup.find_all('input', class_='button')
        x1 = re.findall("onclick=\".*\(\)", str(list1))[0]
        x1 = str(x1).replace("onclick=", '')
        x1 = x1.replace("()", '')
        x2 = soup.findAll('script')
        x3 = str(x2[len(x2) - 1])
        x4 = str(re.findall('action = .*\"', x3)[0])
        x4 = x4.replace('action = ', '').replace('\"', '')
        return url_3 + x4


class kc:

    def __init__(self, s, url):
        name = '跨学期选课'
        self.yxkx = []
        self.xkkc = []
        self.kc_name = []
        self.xk_memory = []
        self.num_xk = None
        self.num_yx = None
        self.kc_name = ['课程名', '老师', '时间', '编号', '学分', '代号', '学时', '周次', '地点']
        self.s = s
        self.rr = s.get(url=url, headers=heard1)
        t = self.rr.text
        list1 = t.split("var tmpKc = Array();")
        if len(list1) != 1:
            i = 1
            for x in list1:
                if i == 1:
                    i = i + 1
                    continue
                else:
                    i = i + 1
                if name in x:
                    list2 = re.findall('.*;', x)
                    for j in range(6, 9):
                        y = re.findall("\".*\"", list2[j])[0]
                        z = str(y).replace('\"', '')
                        self.xk_memory.append(z)
            a = re.findall("link_str.*;", t)[0]
            b = re.findall('\'.*\'', str(a))[0]
            c = str(b).split("\"")
            url = url_3
            j = 0
            for x in c:
                if x[0] != '+':
                    url = url + x.replace('\'', '') + self.xk_memory[j]
                    j = j + 1
                    if j == len(self.xk_memory):
                        break
                pass
            self.r = s.get(url=url, headers=heard1)
            self.sel_kc(self.r.text)
        else:
            json_path = 'resource\\yxkc.json'
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.yxkx = json.load(f)['data']
                    self.xkkc = None
            else:
                self.yxkx = None
                self.xkkc = None

    def sel_kc(self, t: str):
        self.num_xk = len(re.findall("xkkcData\[\d*]", t))
        self.num_yx = len(re.findall("yxkcData\[\d*]", t))
        p = re.compile('function initData\(\){(.+)}\r\n//页面初始加载数据', re.S)
        n = p.findall(t)[0]
        list_xk = re.compile("var tmpKc = Array\(\);(.+?)xkkcData", re.S)
        list_yx = re.compile("var tmpKc = Array\(\);(.+?)yxkcData", re.S)
        xk_final = list_xk.findall(n)
        yx_final = list_yx.findall(n, pos=n.find('xkkcData[{:d}]'.format(self.num_xk - 1)))

        indes1 = (1, 7, 9, 11, 4, 12, 15, 8, 10, 21, 22)  # 课程名 老师 时间 编号 学分 代号 学时 周次 地点 数字周次 数字时间
        indes2 = (1, 10, 6, 0, 4, 22, 8, 5, 9)  # 课程名 老师 时间 编号 学分 代号 学时 周次 地点
        for x in xk_final:
            one = []
            for i in range(0, len(indes1)):
                p = re.compile('tmpKc\[{:d}\].?=.?\"(.+)\"'.format(indes1[i]))
                result = p.findall(x)
                if result:
                    if i == 8:
                        one.append(replace_luoma(result[0], 1))
                    else:
                        if i == 7:
                            one.append(replace_luoma(result[0], 2))
                        else:
                            one.append(replace_luoma(result[0], 0))
                else:
                    one.append('None')
            self.xkkc.append(one)
        for x in yx_final:
            one = []
            for i in range(0, len(indes2)):
                p = re.compile('tmpKc\[{:d}\].?=.?\"(.+)\"'.format(indes2[i]))
                result = p.findall(x)
                if result:
                    if i == 8:
                        one.append(replace_luoma(result[0], 1))
                    else:
                        if i == 7:
                            one.append(replace_luoma(result[0], 2))
                        else:
                            one.append(replace_luoma(result[0], 0))
                else:
                    one.append('None')
            self.yxkx.append(one)
        with open('resource\\yxkc.json', 'w', encoding='utf-8') as f:
            json.dump({'data': self.yxkx}, f)

    def find_index_xk_id(self, classid):
        for i in range(0, len(self.xkkc)):
            if classid == self.xkkc[i][3]:
                return i

    def find_index_xk_teacher(self, name) -> list:
        kc_list = []
        for i in range(0, len(self.xkkc)):
            if name in self.xkkc[i][1]:
                kc_list.append(i)
        return kc_list

    def find_index_yx(self, classname: str):
        for i in range(self.num_xk, len(self.num_yx)):
            if classname in self.yxkx[i][0]:
                return i

    def xk(self, index):
        url = "http://202.119.81.112:9080/njlgdx/xk/processXk"
        pars = {
            'jx0502id': self.xk_memory[1],
            'jx0404id': self.xkkc[index][3],
            'jx0502zbid': self.xk_memory[0],
            'xf': self.xkkc[index][4],
            'kch': self.xkkc[index][5],
            'zxs': self.xkkc[index][6],
            'kcsx': '1',
            'szkcfl': '',
            'kkzcmx': self.xkkc[index][9],
            'kcsjmx': self.xkkc[index][10]
        }
        re = self.s.post(url=url, headers=heard1, data=pars)
        text = re.json()
        add_text(text['msgContent'] + ':' + self.xkkc[index][0] + ' ' + self.xkkc[index][1] + ' ' + self.xkkc[index][2],
                 parent='tab3')
        if '选课成功' in text['msgContent']:
            return True
        else:
            return False

    def tx(self, index):
        url = "http://202.119.81.112:9080/njlgdx/xk/processTx";
        pars = {"jx0502id": self.xk_memory[1],
                "jx0404id": self.xkkc[index][3],
                "jx0502zbid": self.xk_memory[0]
                }
        re = self.s.post(url=url, headers=heard1, data=pars)
        add_text(re.text + ':' + self.xkkc[index][0] + ' ' + self.xkkc[index][1] + ' ' + self.xkkc[index][2],
                 parent='tab3')

    def paint(self):

        with tab('tab3', label='选课', parent='bar'):  # 课程名 老师 时间 编号 学分 代号 学时 周次 地点 0 1 2 8 7 4
            if self.xkkc is not None:
                add_text('选课表')
                add_table('选课表_table', ['课程名', '老师', '时间', '地点', '周次', '学分'], width=1380, height=450)
                for x in self.xkkc:
                    add_row('选课表_table', [x[0], x[1], x[2], x[8], x[7], x[4]])
            if self.yxkx is not None:
                add_text('课表')
                add_table('课表_table', ['课程名', '老师', '时间', '地点', '周次', '学分'], width=1380, height=450)
                for x in self.yxkx:
                    add_row('课表_table', [x[0], x[1], x[2], x[8], x[7], x[4]])
        add_input_text('first', default_value='20210308', label='本学期第一周第一天', parent='loginwin', before='bar')
        add_input_text('pre', default_value='30', label='提前提醒时间', parent='loginwin', before='bar')
        add_button('print', label='课表生成日历', callback=self.printf, callback_data=[get_value('first'), get_value('pre')],
                   parent='loginwin', before='bar')

    def write_rili(self):
        self.rili = []
        for i in range(0, len(self.yxkx)):
            weeks = 0
            a1 = self.yxkx[i][7].split(',')
            a2 = self.yxkx[i][7].split('-')
            if len(a1) > 1:
                if int(a1[0]) % 2 == 0:
                    weeks = 2
                else:
                    weeks = 1
                s = a1[0]
                e = a1[len(a1) - 1]
            else:
                s = a2[0]
                e = a2[1]

            t = self.yxkx[i][2]
            p = re.compile(r'(.*?)\((.*?)\)')
            result = re.findall(p, t)

            for x in result:
                a = str(x[0]).strip()
                b = str(x[1]).strip()

                if a == "星期一":
                    weekday = 1
                elif a == "星期二":
                    weekday = 2
                elif a == "星期三":
                    weekday = 3
                elif a == "星期四":
                    weekday = 4
                elif a == "星期五":
                    weekday = 5
                elif a == "星期六":
                    weekday = 6
                else:
                    weekday = 7
                self.w(i, s, e, weeks, weekday, b)

    def w(self, i, s, e, weeks, weekday, classtime):
        d = {}
        d["ClassName"] = self.yxkx[i][0]
        d["StartWeek"] = int(s)
        d["EndWeek"] = int(e)
        d["WeekStatus"] = int(weeks)
        d["Weekday"] = int(weekday)
        d["ClassTimeId"] = classtime
        d["Classroom"] = self.yxkx[i][8]
        d["isClassSerialEnabled"] = self.yxkx[i][3]
        d["isClassTeacherEnabled"] = self.yxkx[i][1]
        self.rili.append(d)

    def printf(self, sender, data):
        self.write_rili()
        from print_tool import GenerateCal
        process = GenerateCal(self.rili)
        process.set_attribute(data)
        process.main_process()
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("提示", "生成.ics文件成功")


class cj:
    rr = None
    url = "http://202.119.81.112:9080/njlgdx/kscj/cjcx_list"
    list_cj = []

    def __init__(self, s: object) -> object:
        self.rr = s.get(url=self.url, headers=heard1)
        soup = BeautifulSoup(replace_luoma(self.rr.text, 0), 'html.parser')
        list1 = soup.find('table', class_='Nsb_r_list Nsb_table')
        list2 = list1.find_all('tr')
        for x in list2:
            one = []
            if x.find('td') == None:
                for y in x.find_all('th'):
                    one.append(y.get_text())
            else:
                for y in x.find_all('td'):
                    one.append(y.get_text())
            self.list_cj.append(one)

    def tojd(self, m):
        try:
            n = float(m)
            if n in range(90, 101):
                return 4.0
            if n in range(85, 90):
                return 3.7
            if n in range(82, 85):
                return 3.3
            if n in range(78, 82):
                return 3.0
            if n in range(75, 78):
                return 2.7
            if n in range(72, 75):
                return 2.3
            if n in range(68, 72):
                return 2.0
            if n in range(64, 68):
                return 1.5
            if n in range(60, 64):
                return 1.0
            else:
                return 0.0
        except:
            if m == '优秀':
                return 4.0
            if m == '良好':
                return 3.0
            if m == '中等':
                return 2.0
            if m == '及格':
                return 1.0
            else:
                return 0.0

    def tofs(self, m):
        try:
            return float(m)
        except:
            if m == '优秀':
                return 90
            if m == '良好':
                return 80
            if m == '及格':
                return 60

    def toavg(self, list1):
        fs = []
        jd = []
        sumxf = []
        xq = []
        fs.append(0.0)
        jd.append(0.0)
        sumxf.append(0.0)
        xq.append(self.list_cj[1][1])
        for i in list1:
            if self.list_cj[i][1] != xq[len(xq) - 1]:
                try:
                    xq.append(self.list_cj[i][1])
                    fs.append(0.0)
                    jd.append(0.0)
                    sumxf.append(0.0)
                    fs[len(xq) - 1] = fs[len(xq) - 1] + self.tofs(self.list_cj[i][4]) * float(self.list_cj[i][6])
                    jd[len(xq) - 1] = jd[len(xq) - 1] + self.tojd(self.list_cj[i][4]) * float(self.list_cj[i][6])
                    sumxf[len(xq) - 1] = sumxf[len(xq) - 1] + float(self.list_cj[i][6])
                except:
                    print(self.list_cj[i])
            else:
                fs[len(xq) - 1] = fs[len(xq) - 1] + self.tofs(self.list_cj[i][4]) * float(self.list_cj[i][6])
                jd[len(xq) - 1] = jd[len(xq) - 1] + self.tojd(self.list_cj[i][4]) * float(self.list_cj[i][6])
                sumxf[len(xq) - 1] = sumxf[len(xq) - 1] + float(self.list_cj[i][6])
        for i in range(0, len(xq)):
            fs[i] = round(fs[i] / sumxf[i], 2)
            jd[i] = round(jd[i] / sumxf[i], 2)
        return {'jf': fs, 'jj': jd}

    def onall(self, sender, data):
        if get_value('必修') == False:
            re = self.toavg(data[1])
            set_value('1', value=re["jf"])
            set_value('2', value=re["jj"])
        else:
            re = self.toavg(data[0])
            set_value('1', value=re["jf"])
            set_value('2', value=re["jj"])
            pass
        return

    def paint(self):
        # 序号 开学学期 课程编号 课程名称 成绩 成绩标识 学分 总学时 考核方式 课程属性 课程性质
        # 0    1      2       3      4   5       6   7     8       9      10
        with tab('tab2', label="考试成绩", parent='bar'):
            add_table("成绩查询", self.list_cj[0], width=1080, height=450)
            list_n = []
            list_n.append([])
            list_n.append(range(1, len(self.list_cj)))
            for i in range(1, len(self.list_cj)):
                add_row("成绩查询", self.list_cj[i])
                if self.list_cj[i][9] == '必修':
                    list_n[0].append(i)
            re1 = self.toavg(list_n[1])
            delete_column('成绩查询', 5)
            add_simple_plot('1', value=re1["jf"], label='均分', height=100, width=1080)
            add_simple_plot('2', value=re1["jj"], label='均绩', height=100, width=1080)
            add_checkbox('必修', callback=self.onall, callback_data=list_n)


class djcj:
    url = 'http://202.119.81.112:9080/njlgdx/kscj/djkscj_list'
    rr = None
    djcjlist = []

    def __init__(self, s):
        self.rr = s.get(url=self.url, headers=heard1)
        t = self.rr.text
        soup = BeautifulSoup(t, 'html.parser')
        table = soup.find('table', class_='Nsb_r_list Nsb_table')
        tr = table.find_all('tr')
        th = tr[0].find_all('th')
        self.djcjlist.append([th[0].get_text(), th[1].get_text(), th[2].get_text(), th[4].get_text()])
        for i in range(2, len(tr)):
            td = tr[i].find_all('td')
            self.djcjlist.append([td[0].get_text(), td[1].get_text(), td[4].get_text(), td[8].get_text()])
        return

    def paint(self):
        with tab('tab1', label='等级考试', parent='bar'):
            add_table('考试查询', self.djcjlist[0], width=1080, height=150)
            for x in range(1, len(self.djcjlist)):
                add_row('考试查询', self.djcjlist[x])
                pass
