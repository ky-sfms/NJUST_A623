import json
import os

from dearpygui.core import *
from dearpygui.simple import *

import jiaowuchu
import zhlg

path = os.getcwd()
cookpath = 'resource\\cookies.json'
jwc = None
index = 0

# 打包语句：
# >pyinstaller -w main.py jiaowuchu.py print_tool.py zhlg.py -i D:\mixed_file\daima\Python\mypro\resource\icon.ico

def login(sender, data):
    print('正在登录……')
    global jwc, index
    if index == 0:
        index += 1
    else:
        return
    drop_item("登录失败")
    if not os.path.exists(cookpath):
        f = open(cookpath, 'w')
        json.dump(
            {"username": get_value('name'), "jwc_password": get_value('pwd'), "zhlg_password": get_value('pwd_2')}, f)
        f.close()
        lg = zhlg.zhlg(get_value('name'), get_value('pwd_2'))
        jwc = jiaowuchu.jwc(get_value('name'), get_value('pwd'))
        pass
    else:
        lg = zhlg.zhlg(data[0], data[2])
        jwc = jiaowuchu.jwc(data[0], data[1])
    if not lg.islogin:
        add_text('智慧理工登录失败', parent='loginwin', before='name')
        return
    if not jwc.islogin:
        add_text('教务处登录失败', parent='loginwin', before='name')
        return
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
    drop_item("登录失败")
    show_item('name')
    show_item('pwd')
    show_item('pwd_2')
    hide_item('login')
    set_item_label(sender, '确定')
    set_item_callback('update', callback=reset)


def reset(sender, data):
    drop_item("登录失败")
    f = open(cookpath, 'w')
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
        if os.path.exists(cookpath):
            f = open(cookpath)
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
