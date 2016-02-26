# coding:utf-8
import requests
from urllib import request, parse
import re
import http.client


def getLocation():
    login_url = "http://119.145.67.59/default2.aspx"
    response = http.client.HTTPConnection('119.145.67.59')
    response.request("GET", '/default2.aspx', None)
    res = response.getresponse()
    location_re = r"a href='(.+)default2.aspx'"
    location_r = re.compile(location_re, re.S)
    location = re.findall(location_r, res.read().decode('utf-8'))
    return location[0]


def getView(loginPage):
    view = r'name="__VIEWSTATE" value="(.+?)"'
    view = re.compile(view, re.S)
    viewstate = re.findall(view, loginPage)[0]
    return viewstate


def main():
    location = getLocation()
    s = requests.session()
    head = { "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/48.0.2564.82 Safari/537.36"}
    login_url = "http://119.145.67.59" + location + 'default2.aspx'
    code_url = "http://119.145.67.59" + location + 'CheckCode.aspx'
    login = s.post(login_url, headers=head)
    loginPage = login.text
    ID = input('input your student id: ')
    Password = input('input your password: ')
    img = request.urlretrieve(code_url, '1.jpg')
    print('loding......')
    scode = input('input the scode: ')
    headers = {
                "Host": "119.145.67.59",
                "Connection": "keep-alive",
                "Content-Length": "194",
                "Cache-Control": "max-age=0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Origin": "http://119.145.67.59",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/48.0.2564.82 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "http://119.145.67.59" + location + "default2.aspx",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "ja,zh-CN;q=0.8,zh;q=0.6"
    }
    parms = {
        "__VIEWSTATE": getView(loginPage),
        "txtUserName": ID,
        "TextBox2": Password,
        "txtSecretCode": scode,
        "RadioButtonList1": "学生",
        "Button1": "登录"
    }
    login_post = s.post(login_url, data=parms, headers=headers)
    main_url = "http://119.145.67.59" + location + "xs_main.aspx?xh=" + ID  #catch indexerror
    main_html = login_post.text
    name_re = r'<span id="xhxm">(.+?)同学<'
    name_res = re.compile(name_re, re.S)
    name = re.findall(name_res, main_html)[0]
    a = {"xh": ID}
    b = {"xm": name.encode('gb2312')}
    c = {"gnmkdm": "N121605"}
    e = parse.urlencode(a)
    f = parse.urlencode(b)
    g = parse.urlencode(c)
    xscj_url = "http://119.145.67.59" + location + "xscj_gc.aspx?" + e + '&' + f + '&' + g
    cj_headers = {
        "Host": "119.145.67.59",
        "Connection": "keep-alive",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/48.0.2564.82 Safari/537.36",
        "Referer": "http://119.145.67.59" + location + "xs_main.aspx?xh=" + ID,
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ja,zh-CN;q=0.8,zh;q=0.6",
    }
    cxcj_page = s.post(xscj_url, data=None, headers=cj_headers)
    cxcj_html = cxcj_page.text
    # print(cxcj_html)
    cxcj_headers = {
        "Host": "119.145.67.59",
        "Connection": "keep-alive",
        "Content-Length": "1901",
        "Cache-Control": "max-age=0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Origin": "http://119.145.67.59",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/48.0.2564.82 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": xscj_url,
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "ja,zh-CN;q=0.8,zh;q=0.6"
    }

    cxcj_data = {
        "__VIEWSTATE": getView(cxcj_html),
        "Button2": "在校学习成绩查询"
    }
    cx_page = s.post(url=xscj_url, data=cxcj_data, headers=cxcj_headers)
    cx_html = cx_page.text
    return cx_html



print(main())