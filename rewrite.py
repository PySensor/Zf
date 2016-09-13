# coding:utf-8
import requests
from urllib import request, parse
import re
import http.client
from bs4 import BeautifulSoup
import time
from PIL import Image

s = requests.session()


def Get_Location(ip_address):
    # ip_address = input('input the ip address of system: ')
    login_url = "http://" + ip_address + "/default2.aspx"
    response = http.client.HTTPConnection(ip_address)
    response.request("GET", '/default2.aspx', None)
    response_1 = response.getresponse()
    location_reg = r"a href='(.+)default2.aspx'"
    location_reg = re.compile(location_reg, re.S)
    location = re.findall(location_reg, response_1.read().decode('utf-8'))
    return location[0]


def Get_Viewstate(Login_Page):
    viewstate_reg = r'name="__VIEWSTATE" value="(.+?)"'
    viewstate_reg = re.compile(viewstate_reg, re.S)
    viewstate = re.findall(viewstate_reg, Login_Page)[0]
    return viewstate


def login(id, pwd, ip_address, location):
    login_url = "http://" + ip_address + location + 'default2.aspx'
    code_url = "http://" + ip_address + location + 'CheckCode.aspx'
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/48.0.2564.82 Safari/537.36"}
    login = s.post(login_url, headers=headers)
    print("loading.............")
    Login_Page = login.text
    checkcode_img = request.urlretrieve(code_url, 'cc.jpg')
    cc_image = Image.open('cc.jpg')
    cc_image.show()
    checkcode = input('Please input the checkcode: ')
    params = {
        "__VIEWSTATE": Get_Viewstate(Login_Page),
        "txtUserName": id,
        "TextBox2": pwd,
        "txtSecretCode": checkcode,
        "RadioButtonList1": "学生",
        "Button1": "登录",
    }
    login_post = s.post(login_url, data=params, headers=headers)
    main_html = login_post.text
    return main_html


def catch_name(main_html):
    name_reg = r'<span id="xhxm">(.+?)同学<'
    name_reg = re.compile(name_reg, re.S)
    name = re.findall(name_reg, main_html)[0]
    return name


def score(id, name, ip, location):
    xh = {'xh': id}
    xm = {'xm': name.encode('gb2312')}
    gnmkdm = {'gnmkdm': 'N121605'}
    xh = parse.urlencode(xh)
    xm = parse.urlencode(xm)
    gnmkdm = parse.urlencode(gnmkdm)
    cj_url = "http://" + ip + location + "xscj_gc.aspx?" + xh + '&' + xm + '&' +gnmkdm
    cj_headers = {
        "Host": ip,
        "Connection": "keep-alive",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/48.0.2564.82 Safari/537.36",
        "Referer": "http://" + ip + location + "xs_main.aspx?xh=" + id,
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ja,zh-CN;q=0.8,zh;q=0.6",
    }
    cj_page = s.post(cj_url, data=None, headers=cj_headers)
    cj_html = cj_page.text
    cxcj_headers = {
        "Host": ip,
        "Connection": "keep-alive",
        "Content-Length": "1901",
        "Cache-Control": "max-age=0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Origin": "http://" + ip,
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/48.0.2564.82 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": cj_url,
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ja,zh-CN;q=0.8,zh;q=0.6"
    }
    cxcj_data = {
        "__VIEWSTATE": Get_Viewstate(cj_html),
        "Button2": "在校学习成绩查询"
    }
    score_page = s.post(url=cj_url, data=cxcj_data, headers=cxcj_headers)
    score_html = score_page.content
    soup = BeautifulSoup(score_html, 'html5lib')
    title = soup.find('table', {'class': 'datelist'})
    tr = title.find_all('tr')
    data_list = []
    data_list2 = []
    for item in tr:
        xxx = item.find_all('td')
        for i in xxx:
            data_list.append(i.getText())
    for items in range(int(len(data_list)/16)):
        del data_list[2+9*items]
        del data_list[4+9*items]
        del data_list[7+9*items]
        del data_list[9+9*items]
        del data_list[9+9*items]
        del data_list[9+9*items]
        del data_list[9+9*items]
    title_list = data_list[0:9]
    for x in range(9):
        del data_list[0]
    length = int(len(data_list)/9)
    for itemx in range(int(length)):
        a1 = 0 + 9*itemx
        b1 = 10 + 9*itemx
        data_list2.append(list(data_list[a1:b1]))
    x1 = 0
    while x1 <= length-1:
        for index, titles in enumerate(title_list):
            print('{} -> {}'.format(title_list[index], data_list2[x1][index]))
        print('-'*100)
        x1 += 1


# def get_class_table(ip, id, name, location):
#     xh = {'xh': id}
#     xm = {'xm': name.encode('gb2312')}
#     gnmkdm = {'gnmkdm': 'N121601'}
#     xh = parse.urlencode(xh)
#     xm = parse.urlencode(xm)
#     gnmkdm = parse.urlencode(gnmkdm)
#     table_url = 'http://' + ip + location + 'tjkbcx.aspx?' + xh + '&' + xm + '&' + gnmkdm
#     v_headers = {
#         'Host': ip,
#         'Connection': 'keep-alive',
#         'Upgrade-Insecure-Requests': '1',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
#                       ' Chrome/52.0.2743.82 Safari/537.36',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#         'Referer': 'http://' + ip + location + 'xs_main.aspx?' + xh,
#         'Accept-Encoding': 'gzip, deflate, sdch',
#         'Accept-Language': 'ja,zh-CN;q=0.8,zh;q=0.6',
#     }
#     table_headers = {
#         'Host': ip,
#         'Connection': 'keep-alive',
#         'Content-Length': '2590',
#         'Cache-Control': 'max-age=0',
#         'Origin': 'http://' + ip,
#         'Upgrade-Insecure-Requests': '1',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
#                       ' Chrome/52.0.2743.82 Safari/537.36',
#         'Content-Type': 'application/x-www-form-urlencoded',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#         'Referer': table_url,
#         'Accept-Encoding': 'gzip, deflate',
#         'Accept-Language': 'ja,zh-CN;q=0.8,zh;q=0.6',
#             }
#     page = s.get(table_url, headers=v_headers).text
#     viewstate = Get_Viewstate(page)
#     datas = {
#         '__EVENTTARGET': 'kb',
#         '__EVENTARGUMENT': '',
#         '__VIEWSTATE': viewstate,
#         'xn': '2016-2017',
#         'xq': '1',
#         'nj': '2015',
#         'xy': '12',
#         'zy': '1204',
#         'kb': '201512042016-2017112041501',
#
#     }
#     res = s.post(table_url, headers=table_headers, data=datas).text
#     return res


def choose_class(ip, id, name, location):
    print('loading......')
    xh = {'xh': id}
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
            '__VIEWSTATE': Get_Viewstate(class_page),
            'ddl_kcxz': '',
            'ddl_ywyl':	'有',
            'ddl_kcgs': '',
            'ddl_xqbs':	'1',
            'ddl_sksj': '',
            'TextBox1': '',
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
    reg = re.compile('(\w.+){', re.S)
    for i in class_table:
        result = re.findall(reg, i.getText())
        if len(result) != 0:
            class_list.append(result[0])
    for n, c in enumerate(class_list):
        print('编号：{}-> 课程：{}'.format(n+1, c))

    xk_data = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': Get_Viewstate(class_page),
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
        choose = int(input('请输入你要选课的编号：'))
        xk_data[num_list1[choose-1]] = 'on'
    except Exception as e:
        print('你肯定是输错了点什么，重来吧')
    already_choose = soup.find_all('table')[1]
    class1 = already_choose.find_all('tr')[1]
    reg = re.compile('(\w.+){', re.S)
    classList = []
    classList.append(class1.getText())
    for i in classList:
        already_class = re.findall(reg, i)

    if len(already_class) != 0:
        print('-'*75)
        print('然而你已经选到课了别来凑热闹')
        print('你选到的是：', already_class[0])
    else:
        while True:
            post_page = s.post(class_url, headers=table_headers, data=xk_data).text
            check_soup = BeautifulSoup(post_page, 'html5lib')
            check = check_soup.find_all('table')[1]
            class2 = check.find_all('tr')[1]
            classList2 = []
            classList2.append(class2.getText())
            for i1 in classList2:
                checked = re.findall(reg, i1)
            if len(checked) != 0:
                break
            time.sleep(0.5)










ip = '119.145.67.59'
location = Get_Location(ip)
id = input("Please input your id: ")
pwd = input("Please input your password: ")
html = login(id=id, pwd=pwd, ip_address=ip, location=location)
name = catch_name(html)
# viewstate = Get_Viewstate(html)
table = choose_class(ip=ip, id=id, name=name, location=location)
# score(id=id, name=name, location=location, ip=ip)



