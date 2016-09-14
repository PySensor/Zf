# coding:utf-8
import requests
from urllib import request, parse
import re
import http.client
from bs4 import BeautifulSoup
import os
from PIL import Image
# from prettytable import PrettyTable
import xlwt
import time

s = requests.session()


def get_location(ip_address):
    login_url = "http://" + ip_address + "/default2.aspx"
    response = http.client.HTTPConnection(ip_address)
    response.request("GET", '/default2.aspx', None)
    response_1 = response.getresponse()
    location_reg = r"a href='(.+)default2.aspx'"
    location_reg = re.compile(location_reg, re.S)
    location = re.findall(location_reg, response_1.read().decode('utf-8'))
    return location[0]


def get_viewstate(page):
    viewstate_reg = r'name="__VIEWSTATE" value="(.+?)"'
    viewstate_reg = re.compile(viewstate_reg, re.S)
    viewstate = re.findall(viewstate_reg, page)[0]
    return viewstate


def catch_name(main_html):
    name_reg = r'<span id="xhxm">(.+?)同学<'
    name_reg = re.compile(name_reg, re.S)
    name = re.findall(name_reg, main_html)[0]
    return name


def login(xh, pwd, ip_address, location):
    login_url = "http://" + ip_address + location + 'default2.aspx'
    code_url = "http://" + ip_address + location + 'CheckCode.aspx'
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/48.0.2564.82 Safari/537.36"}
    login = s.post(login_url, headers=headers)
    Login_Page = login.text
    print('正在读取验证码...请稍后')
    checkcode_img = request.urlretrieve(code_url, 'cc.jpg')
    cc_image = Image.open('cc.jpg')
    cc_image.show()
    checkcode = input('请输入验证码->')
    print('loading....')
    params = {
        "__VIEWSTATE": get_viewstate(Login_Page),
        "txtUserName": xh,
        "TextBox2": pwd,
        "txtSecretCode": checkcode,
        "RadioButtonList1": "学生",
        "Button1": "登录",
    }
    login_post = s.post(login_url, data=params, headers=headers)
    main_html = login_post.text
    name = catch_name(main_html)
    print('登录成功，你好{}同学'.format(name))
    return name


def cx_cj(ip, location, xh, name):
    xh = parse.urlencode({'xh': xh})
    xm = parse.urlencode({'xm': name.encode('gb2312')})
    gnmkdm = parse.urlencode({'gnmkdm': 'N121605'})
    cj_url = 'http://' + ip + location + 'xscj_gc.aspx?' + xh + '&' + xm + '&' +gnmkdm
    cj_headers = {
        'Host': ip,
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/52.0.2743.82 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'http://' + ip + location + 'xs_main.aspx?xh=' + xh,
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'ja,zh-CN;q=0.8,zh;q=0.6',
    }
    cj_page = s.get(url=cj_url, headers=cj_headers).content.decode('gb2312')
    viewstate = get_viewstate(cj_page)
    post_data = {
        '__VIEWSTATE': viewstate,
        'ddlXN': '',
        'ddlXQ': '',
        'Button2': '在校学习成绩查询',
    }
    cj_post_headers = {
        'Host': ip,
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Origin': 'http://' + ip,
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/52.0.2743.82 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': cj_url,
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'ja,zh-CN;q=0.8,zh;q=0.6',
    }
    print('成绩查询中请稍后...')
    try:
        cj_source = s.post(url=cj_url, headers=cj_post_headers, data=post_data).content.decode('gb2312')
    except Exception as e:
        print('查询失败..')
        input('回车退出程序')
        exit()
    print('查询成功，正在读取课表...')

    excel = xlwt.Workbook()
    sheet1 = excel.add_sheet('成绩表', cell_overwrite_ok=True)
    soup = BeautifulSoup(cj_source, 'html5lib')
    cj_table = soup.find('table', {'class': 'datelist'}).find('tbody')
    rows = cj_table.find_all('tr')
    field = rows[0].find_all('td')[0:13]
    datas = []
    reg = re.compile('<td>(.+?)</td>', re.S)
    for k, v in enumerate(field):
        field[k] = re.findall(reg, str(v))[0]
    # pre = PrettyTable(field)
    for i in range(0, len(field)):
        sheet1.write(0, i, field[i])

    for i in rows[1:]:
        datas.append(i.find_all('td')[0:13])
    for j, i in enumerate(datas):
        for k, v in enumerate(i):
            i[k] = re.findall(reg, str(v))[0]
            # pre.add_row(i)
        datas[j] = i

    for x, y in enumerate(datas):
        for a in range(0, len(y)):
            sheet1.write(x+1, a, y[a])

    # pre_txt = '''{}'''.format(pre)
    # print(pre_txt)
    print('成绩表正在保存中...')
    excel.save('{}同学的成绩表.xlsx'.format(name))
    print('保存成功！！！')


def choose_class(ip, xh, name, location):
    xh = {'xh': xh}
    xm = {'xm': name.encode('gb2312')}
    gnmkdm = {'gnmkdm': 'N121203'}
    xh = parse.urlencode(xh)
    xm = parse.urlencode(xm)
    gnmkdm = parse.urlencode(gnmkdm)
    class_url = 'http://' + ip + location + 'xf_xsqxxxk.aspx?' + xh + '&' + xm + '&' + gnmkdm
    class_headers = {
            'Host': ip,
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/52.0.2743.82 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'http://' + ip + location + 'xs_main.aspx?' + xh,
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'ja,zh-CN;q=0.8,zh;q=0.6',
    }
    class_page = s.get(url=class_url, headers=class_headers).text
    print('继续loading......')
    table_headers = {
            'Host': ip,
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Content-Length': '77546',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/52.0.2743.82 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': class_url,
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'ja,zh-CN;q=0.8,zh;q=0.6',
            'Origin': 'http://' + ip,
    }
    data = {
            '__EVENTTARGET': 'dpkcmcGrid:txtPageSize',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': get_viewstate(class_page),
            'ddl_kcxz': '',
            'ddl_ywyl':	'有',
            'ddl_kcgs': '',
            'ddl_xqbs':	'1',
            'ddl_sksj': '',
            'TextBox1': '',
            'Button2': '确定',
            'kcmcGrid:_ctl2:jcnr': '|||',
            'kcmcGrid:_ctl3:jcnr': '|||',
            'kcmcGrid:_ctl4:jcnr': '|||',
            'kcmcGrid:_ctl5:jcnr': '|||',
            'kcmcGrid:_ctl6:jcnr': '|||',
            'kcmcGrid:_ctl7:jcnr': '|||',
            'kcmcGrid:_ctl8:jcnr': '|||',
            'kcmcGrid:_ctl9:jcnr': '|||',
            'kcmcGrid:_ctl10:jcnr': '|||',
            'kcmcGrid:_ctl11:jcnr': '|||',
            'kcmcGrid:_ctl12:jcnr': '|||',
            'kcmcGrid:_ctl13:jcnr': '|||',
            'kcmcGrid:_ctl14:jcnr': '|||',
            'kcmcGrid:_ctl15:jcnr': '|||',
            'kcmcGrid:_ctl16:jcnr': '|||',
            'dpkcmcGrid:txtChoosePage': '1',
            'dpkcmcGrid:txtPageSize': '100',
            'dpDataGrid2:txtChoosePage': '1',
            'dpDataGrid2:txtPageSize': '150',
    }
    class_table = s.post(url=class_url, headers=table_headers, data=data).text
    print('那就再loading一下吧......')
    # class_table = class_table.decode('gb2312')
    soup = BeautifulSoup(class_table, 'html5lib')
    table = soup.find('table', {'class': 'datelist'}).find('tbody')
    class_num = table.find_all('input')
    num_list = []
    for i in class_num:
        num_list.append(i.get('id'))
    num_list1 = num_list[::3]   #要选的课程
    num_list2 = num_list[2::3]  #不选的课程
    class_table = table.find_all('tr')
    class_list = []
    reg = re.compile('(\w.+)周', re.S)
    title_reg = re.compile('title="(.+?)"', re.S)
    for i in class_table[1:]:
        class_item = re.findall(reg, i.getText())[0]
        class_time = re.findall(title_reg, str(i))[0]
        class_list.append(class_item + class_time)
    print('下面就是你还能选择的课：')
    for n, c in enumerate(class_list):
        print('编号：{}-> 课程：{}'.format(n+1, c))

    xk_data = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': get_viewstate(class_page),
        'ddl_kcxz': '',
        'ddl_ywyl':	'有',
        'ddl_kcgs':	'',
        'ddl_xqbs': '1',
        'ddl_sksj': '',
        'TextBox1': '',
        'dpkcmcGrid:txtChoosePage': '1',
        'dpkcmcGrid:txtPageSize': '100',
        'Button1': '提交',
        'dpDataGrid2:txtChoosePage': '1',
        'dpDataGrid2:txtPageSize': '150',
    }
    for xxx in num_list2:
        xk_data[xxx] = '|||'
    try:
        choose = int(input('请输入你要选课的编号->'))
        xk_data[num_list1[choose-1]] = 'on'
    except Exception as e:
        print('你肯定是输错了点什么，重来吧')
    already_choose = soup.find_all('table')[1]
    class1 = already_choose.find_all('tr')[1:]
    reg = re.compile('(\w.+){', re.S)
    classList = []
    save_class = []
    for i in class1:
        item = i.getText()
        classList.append(item)
    for i1 in classList:
        already_class = re.findall(reg, i1)[0]
        save_class.append(already_class)
    if len(save_class) > 1:
        print('-'*75)
        print('然而你已经选到课了别来凑热闹')
        print('你选到的是：', save_class[0])
        input('输入任意键退出')
        quit()
    else:
        post_page = s.post(class_url, headers=table_headers, data=xk_data).text
        check_soup = BeautifulSoup(post_page, 'html5lib')
        check = check_soup.find_all('table')[1]
        class2 = check.find_all('tr')[1:]
        classList2 = []
        checked = []
        for j in class2:
            item2 = j.getText()
            classList2.append(item2)
        for j1 in classList2:
            check_item = re.findall(reg, j1)[0]
            checked.append(check_item)
        if len(checked) > 1:
            print('恭喜你你选到课了')
            print('你选到的是：', checked[0])
            input('输入任意键退出')
            quit()
        time.sleep(0.5)


def cx_kb(ip, location, xh, name):
    xh = parse.urlencode({'xh': xh})
    xm = parse.urlencode({'xm': name.encode('gb2312')})
    gnmkdm = parse.urlencode({'gnmkdm': 'N121605'})
    kb_url = 'http://' + ip + location + 'xskbcx.aspx?' + xh + '&' + xm + '&' +gnmkdm
    kb_headers = {
        'Host': ip,
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/52.0.2743.82 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'http://' + ip + location + 'xs_main.aspx?xh=' + xh,
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'ja,zh-CN;q=0.8,zh;q=0.6',
    }
    print('课表查询中请稍后...')
    try:
        kb_page = s.get(url=kb_url, headers=kb_headers).content.decode('gb2312')
    except Exception as e:
        print('查询失败..')
        input('回车退出程序')
        exit()
    print('查询成功，正在读取课表...')
    soup = BeautifulSoup(kb_page, 'html5lib')
    table = soup.find('table', {'id': 'Table1'}).find('tbody')
    rows = table.find_all('tr')[2:12:2]
    Monday = []
    Tuesday = []
    Wednesday = []
    Thursday = []
    Friday = []
    reg = re.compile('周(.?)第', re.S)

    for i in range(4):
        for j in rows[i].find_all('td', {'rowspan': '2'}):
            lesson = j.getText()
            if re.findall(reg, lesson)[0] == '一':
                Monday.append(lesson)
            elif re.findall(reg, lesson)[0] == '二':
                Tuesday.append(lesson)
            elif re.findall(reg, lesson)[0] == '三':
                Wednesday.append(lesson)
            elif re.findall(reg, lesson)[0] == '四':
                Thursday.append(lesson)
            elif re.findall(reg, lesson)[0] == '五':
                Friday.append(lesson)
            else:
                pass

    for i1 in rows[4].find_all('td', {'rowspan': '3'}):
        lesson1 = i1.getText()
        num = re.findall(reg, lesson1)
        if len(num) > 0:
            if num[0] == '一':
                Monday.append(lesson)
            elif num[0] == '二':
                Tuesday.append(lesson)
            elif num[0] == '三':
                Wednesday.append(lesson)
            elif num[0] == '四':
                Thursday.append(lesson)
            elif num[0] == '五':
                Friday.append(lesson)
            else:
                pass

    print('-'*120)
    print('周一：')
    for i in Monday:
        print(i)
    print('-'*120)
    print('周二：')
    for i in Tuesday:
        print(i)
    print('-'*120)
    print('周三：')
    for i in Wednesday:
        print(i)
    print('-'*120)
    print('周四：')
    for i in Thursday:
        print(i)
    print('-'*120)
    print('周五：')
    for i in Friday:
        print(i)
    print('-'*120)

    print('课表正在保存到本地，请稍等...')
    with open('{}同学的课表.txt'.format(name), 'w+', encoding='utf-8') as f:
        f.writelines('-'*120+'\n')
        f.writelines('周一：'+'\n')
        for i in Monday:
            f.writelines(i+'\n')
        f.writelines('-'*120+'\n')
        f.writelines('周二：'+'\n')
        for i in Tuesday:
            f.writelines(i+'\n')
        f.writelines('-'*120+'\n')
        f.writelines('周三：'+'\n')
        for i in Wednesday:
            f.writelines(i+'\n')
        f.writelines('-'*120+'\n')
        f.writelines('周四：'+'\n')
        for i in Thursday:
            f.writelines(i+'\n')
        f.writelines('-'*120+'\n')
        f.writelines('周五：'+'\n')
        for i in Friday:
            f.writelines(i+'\n')
        f.writelines('-'*120+'\n')
    f.close()
    print('保存成功！！！')


def main():
    print('''
------------------------------------------------------------
  Py的辣鸡查教务系统脚本测试版 --version 0.0.1
------------------------------------------------------------
请选择你要登录的教务系统ip：
  0.http://172.16.17.113(内网)
  1.http://172.16.17.110(内网)
  2.http://172.16.17.114(内网)
  3.http://119.145.67.59:8889(外网)
  4.http://119.145.67.59(外网)
------------------------------------------------------------''')
    ip_list = ['172.16.17.113', '172.16.17.110', '172.16.17.114', '119.145.67.59:8889', '119.145.67.59']
    while True:
        try:
            ip_choose = int(input('输入选课的教务系统的ip的编号->'))
            if ip_choose == 0:
                ip = ip_list[0]
            elif ip_choose == 1:
                ip = ip_list[1]
            elif ip_choose == 2:
                ip = ip_list[2]
            elif ip_choose == 3:
                ip = ip_list[3]
            elif ip_choose == 4:
                ip = ip_list[4]
            else:
                raise IndexError
        except IndexError as e3:
            print('输入的ip编号有误')
            input('回车继续选择')
        else:
            try:
                location = get_location(ip)
            except IndexError as e2:
                print('没错辣鸡服务器真的炸了....炸了....了....')
                input('回车退出程序')
                exit()
            xh = input('xh-> ')
            if not os.path.exists(os.getcwd() + '\{}.txt'.format(xh)):
                pwd = input('pwd-> ')
                with open('{}.txt'.format(xh), 'w+', encoding='utf-8') as f1:
                    f1.writelines(pwd)
                f1.close()
                pwd = pwd
            else:
                xh = xh
                print('正在从本地读取密码...')
                with open('{}.txt'.format(xh), 'r') as f:
                    pwd = f.readlines()[0]
                f.close()
            while True:
                try:
                    name = login(xh=xh, pwd=pwd, ip_address=ip, location=location)
                except IndexError as e1:
                    print('登录失败，原因可能是教务系统挂了或者你输入的信息有误,请检查清楚')
                else:
                    while True:
                        print('''
请选择:
    0.退出程序
    1.查课表
    2.查成绩
    3.选课(测试)''')
                        try:
                            func_choose = int(input('->'))
                            if func_choose == 0:
                                quit()
                            elif func_choose == 1:
                                cx_kb(ip=ip, location=location, xh=xh, name=str(name))
                            elif func_choose == 2:
                                cx_cj(ip=ip, location=location, xh=xh, name=str(name))
                            elif func_choose == 3:
                                choose_class(ip=ip, location=location, xh=xh, name=str(name))
                            else:
                                print('输入功能编号错误')
                                input('回车重来')
                        except AttributeError as e:
                            print('查询失败，原因可能是教务系统挂了或者是选课接口没有打开')
                            input("回车继续抢课")


if __name__ == '__main__':
    main()