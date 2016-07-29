import requests
from urllib import request, parse
import re
import http.client
from bs4 import BeautifulSoup


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
    print("loading.............")
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


ip = '119.145.67.59'
loc = Get_Location(ip)
id = input("Please input your id: ")
pwd = input("Please input your password: ")
html = login(id=id, pwd=pwd, ip_address=ip, location=loc)
n = catch_name(html)
score(id=id, name=n, location=loc, ip=ip)




