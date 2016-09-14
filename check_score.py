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


def main():
    print('''
------------------------------------------------------------
  Py的辣鸡查成绩脚本测试版 --version 0.0.1
------------------------------------------------------------
请选择你要登录的教务系统ip：
  0.http://172.16.17.113(内网)
  1.http://172.16.17.110(内网)
  2.http://172.16.17.114(内网)
  3.http://119.145.67.59:8889(外网)
  4.http://119.145.67.59(外网)
------------------------------------------------------------''')
    ip_list = ['172.16.17.113', '172.16.17.110', '172.16.17.114', '119.145.67.59:8889', '119.145.67.59']
    ip_choose = int(input('输入选课的教务系统的ip的编号->'))
    try:
        ip = ip_list[ip_choose]
    except IndexError as e3:
        print('输入的编号有误')
        input('回车退出程序')
        exit()
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
    name = login(xh=xh, pwd=pwd, ip_address=ip, location=location)
    cx_cj(ip=ip, location=location, xh=xh, name=str(name))
    print('回车退出程序')

if __name__ == '__main__':
    main()