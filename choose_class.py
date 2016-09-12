# coding:gb2312
import requests
from urllib import request, parse
import re
import http.client
from bs4 import BeautifulSoup
import time
# from PIL import Image

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
    Login_Page = login.text
    checkcode_img = request.urlretrieve(code_url, 'cc.jpg')
    # cc_image = Image.open('cc.jpg')
    # cc_image.show()
    checkcode = input('请输入验证码->')
    print('loading....')
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


def choose_class(ip, id, name, location):
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
    print('下面就是你还能选择的课：')
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
        choose = int(input('请输入你要选课的编号->'))
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
        input('输入任意键退出')
        quit()
    else:
        post_page = s.post(class_url, headers=table_headers, data=xk_data).text
        check_soup = BeautifulSoup(post_page, 'html5lib')
        check = check_soup.find_all('table')[1]
        class2 = check.find_all('tr')[1]
        classList2 = []
        classList2.append(class2.getText())
        for i1 in classList2:
            checked = re.findall(reg, i1)
        if len(checked) != 0:
            print('恭喜你你选到课了')
            print('你选到的是：', checked[0])
            input('输入任意键退出')
            quit()
        time.sleep(0.5)


def main():
    print('''
------------------------------------------------------------
  Py的辣鸡选课脚本测试版 --version 0.0.2
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
    ip = ip_list[ip_choose]
    location = Get_Location(ip)
    id = input("请输入学号->")
    pwd = input("请输入密码->")
    print('loading.....')
    html = login(id=id, pwd=pwd, ip_address=ip, location=location)
    try:
        name = catch_name(html)
        print('''登录成功!!!
        雷猴,{}同学'''.format(name))
        while True:
            choose_class(ip=ip, id=id, name=name, location=location)
    except AttributeError as e:
        print('查询失败，原因可能是教务系统挂了或者是选课接口没有打开')

if __name__ == '__main__':
    main()
