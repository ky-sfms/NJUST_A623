import os
import requests
import time
import tkinter as tk
from tkinter import messagebox
import sys
import threading

username=''#输入学号
password=''#输入密码
url='http://m.njust.edu.cn/portal_io/login'
headers = {
	'Accept': 'application/json, text/javascript, */*; q=0.01',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
	'Connection': 'keep-alive',
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
	'Host': 'm.njust.edu.cn',
	'Origin': 'http://m.njust.edu.cn',
	'Referer': 'http://m.njust.edu.cn/portal/index.html',
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66',
	'X-Requested-With': 'XMLHttpRequest'
}
data={
	'username':username,
	'password':password
}
mywifiname='NJUST-FREE'
global window,l,tishi,timenum
timenum=0
tishi=''
#连接日志
#线程提示
def openrizhi(mes):
	f=open('D:/hook_rizhi.txt','a',encoding='UTF-8')
	f.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())+mes+"\n")
	f.close()
def add( ):
	global timenum,window,l
	timenum+=1
	l.config(text=('正在连接校园网%d秒\n' % (timenum))+tishi)
	l.update()
	window.after(1000,add)
def run(self):
	global window,l
	window = tk.Tk()
	window.title('提示')
	width=200
	height=55
	screenwidth = window.winfo_screenwidth()
	screenheight = window.winfo_screenheight()
	size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
	window.geometry(size)
	l = tk.Label(window,text='正在连接校园网%d秒' % (timenum),font=('Arial', 12),width=15, height=2)
	l.pack()    # 固定窗口位置
	window.resizable(False,False)
	window.update()
	window.after(1000,add)
	window.mainloop()
def threadrun():
    t = threading.Thread(target=run, args=("t1",))
    t.setDaemon(True)   #把子进程设置为守护线程，必须在start()之前设置
    t.start()
    
#连接校园网
def SchoolWife():
	global tishi
	response=requests.post(url,headers=headers,data=data)
	text=response.text
	m=text.split('reply_msg')[1]
	msg=m.split('userinfo')[0]
	msg=msg.replace('\"','')
	msg=msg.replace(':','')
	msg=msg.replace(',','')
	if '登录成功' in msg:
		tishi='连接校园网成功'
	if '已登陆' in msg:
		tishi='校园网已经连接'
	if tishi != '':
		openrizhi(tishi)
#获取当前电脑连接的wife名
def judgewife():
	# reconnect()
	mymessage = os.popen('netsh WLAN show interfaces').readlines()
	for x in mymessage:
		if (x.split(':')[0].find('配置文件')!=-1):
			if (x.split(':')[1].find(mywifiname)!=-1):
				SchoolWife()
			else:
				messagebox.showwarning('警告',"当前网络不是校园网\n所连网络:"+x.split(':')[1])

def reconnect():
	os.system("netsh wlan disconnect")
	os.system("netsh wlan connect name=\"NJUST-FREE\"")
	return

roott = tk.Tk()
roott.withdraw()#去除tk弹窗
threadrun()
judgewife()
time.sleep(2)