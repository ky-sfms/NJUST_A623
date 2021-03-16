import json
import os
import threading

from dearpygui.core import *
from dearpygui.simple import *

import jiaowuchu
import zhlg

path = os.getcwd()
per_info_path = 'resource\\per_Info.json'
index = 0


# 教务处无法保存cookie

# 打包语句：
# >pyinstaller -w main.py jiaowuchu.py print_tool.py zhlg.py -i D:\mixed_file\daima\Python\mypro\resource\icon.ico

def mesbox(title, text, interval):
    size_main = get_main_window_size()
    with window(title, width=200, height=60, x_pos=int(size_main[0] / 2) - 100, y_pos=int(size_main[1] / 2) - 30,
                no_move=True):
        add_label_text('', default_value=text)
    if interval > 0:
        t = threading.Timer(interval, lambda: delete_item(title))
        t.setDaemon(True)
        t.start()
    return


def login(sender, data):
    global index
    if index == 0:
        index += 1
    else:
        return
    size_main = get_main_window_size()
    with window('提示', width=200, height=60, x_pos=int(size_main[0] / 2) - 100, y_pos=int(size_main[1] / 2) - 30):
        add_label_text('', default_value='正在登录…………')
    jwc = None
    lg = None
    already = False
    if os.path.exists('resource\\cookie.json'):
        with open('resource\\cookie.json', 'r', encoding='utf-8') as f:
            cookie = json.load(f)
        lg = zhlg.zhlg(get_value('name'), get_value('pwd_2'), cookie['zhlg'])
        # jwc = jiaowuchu.jwc(get_value('name'), get_value('pwd_2'), cookie['jwc'])
        if lg.islogin:  # and jwc.islogin:
            print('cookie登录成功')
            already = True
        else:
            os.remove('resource\\cookie.json')
    # if not already:
    if not os.path.exists(per_info_path):
        f = open(per_info_path, 'w')
        json.dump(
            {"username": get_value('name'), "jwc_password": get_value('pwd'), "zhlg_password": get_value('pwd_2')}, f)
        f.close()
        if not already:
            lg = zhlg.zhlg(get_value('name'), get_value('pwd_2'), None)
        jwc = jiaowuchu.jwc(get_value('name'), get_value('pwd'))
        pass
    else:
        if not already:
            lg = zhlg.zhlg(data[0], data[2], None)
        jwc = jiaowuchu.jwc(data[0], data[1])
    if not lg.islogin:
        mesbox('错误', '智慧理工登录失败', -1)
        return
    if not jwc.islogin:
        mesbox('错误', '教务处登录失败', -1)
        return
    with open('resource\\cookie.json', 'w', encoding='utf-8') as f:
        json.dump({'zhlg': lg.s.cookies.get_dict()}, f)
    # 已经登录成功
    delete_item('提示')
    set_main_window_size(1920, 1080)  # 全屏
    # 课程
    kc = jiaowuchu.kc(jwc.s, jwc.list['选课中心'])
    kc.paint()
    # 考试
    cj = jiaowuchu.cj(jwc.s)
    cj.paint()
    # 等级考试
    djcj = jiaowuchu.djcj(jwc.s)
    djcj.paint()
    # 智慧理工
    lg.paint()


def drop_item(name):
    item_list = get_all_items()
    for x in item_list:
        if name in get_item_label(x):
            delete_item(x)


def update(sender, data):
    show_item('name')
    show_item('pwd')
    show_item('pwd_2')
    hide_item('login')
    set_item_label(sender, '确定')
    set_item_callback('update', callback=reset)


def reset(sender, data):
    f = open(per_info_path, 'w')
    json.dump({"username": get_value('name'), "jwc_password": get_value('pwd'), "zhlg_password": get_value('pwd_2')},
              f)
    f.close()
    show_item('login')
    hide_item('name')
    hide_item('pwd')
    hide_item('pwd_2')
    set_item_label(sender, '重置')


if __name__ == '__main__':
    set_main_window_title('NJUST')
    set_main_window_size(400, 200)
    set_main_window_pos(550, 300)
    with window('loginwin', x_pos=0, y_pos=0, no_move=True, autosize=True, no_title_bar=True,
                no_scrollbar=True):
        add_additional_font('C:/Windows/Fonts/SIMHEI.TTF', 16, glyph_ranges='chinese_full')
        add_input_text('name', label='用户名', show=False)
        add_input_text('pwd', label='教务处密码', password=True, show=False)
        add_input_text('pwd_2', label='智慧理工密码', password=True, show=False)
        if os.path.exists(per_info_path):
            f = open(per_info_path)
            json_data = json.load(f)
            f.close()
            data = [json_data["username"], json_data["jwc_password"], json_data["zhlg_password"]]
            add_button('login', label='登录', callback=login, parent='loginwin', callback_data=data, tip='登录教务处和智慧理工',
                       width=400, height=25)
            add_button('update', label='重置', callback=update, parent='loginwin', tip="重置账户", width=400, height=25)
            pass
        else:
            show_item('name')
            show_item('pwd')
            show_item('pwd_2')
            add_button('login', label='登录', callback=login, parent='loginwin', callback_data=None, tip='登录教务处和智慧理工')
    start_dearpygui()
