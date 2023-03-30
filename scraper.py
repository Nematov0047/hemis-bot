import requests
from bs4 import BeautifulSoup
from db import db
import json
# bazani borligini tekshirib olamiz
db.initialize()
# institut manzili
URL = 'https://student.andmiedu.uz'
# bu yerda telegram botni ishlatmoqchi bo'lgan talaba login va parolini beradi, va shu login parol oraqli saytga kirib u yerda biz cookielarni ovolamiz, agar login yoki parol xato bo'lsa, funksiya False return qiladi
# Bu faqatgina bir marta olinib saqlab qo'yilishi kerak, har safar ishlatsek kirishlar tarixida ko'payib ketadi, bizi kirganimiz
def auth(login, password):
    req = requests.get(URL + '/dashboard/login')
    req_html = req.text
    soup = BeautifulSoup(req_html,'lxml')
    hidden_input = soup.input.get('value')

    payload = {
        'FormStudentLogin[login]':login,
        'FormStudentLogin[password]':password,
        '_csrf-frontend':hidden_input
    }

    req_login = requests.post('https://student.andmiedu.uz/dashboard/login',data=payload, cookies=dict(req.cookies), allow_redirects=False)
    output = dict(req_login.cookies)
    if '_frontendUser' in output:
        return output
    else:
        return False
# shu asosiy cookielarni olib beruvchi funksiya bo'lib ishlashligi kerak
def main_cookies(login, password):
    cookies = db.get_cookies(login)
    if cookies != False and cookies != 'expired':
        return cookies
    if password == '':
        return False
    auth_cookies = auth(login, password)
    if cookies == False:
        if auth_cookies == False:
            return False
        else:
            db.insert_cookies(login, json.dumps(auth_cookies))
            return auth_cookies
    elif cookies == 'expired':
        if auth_cookies == False:
            return False
        else:
            db.update_cookies(login, json.dumps(auth_cookies))
            return auth_cookies

# nblarni olib beruvchi funksiya, dictionary return qiladi
# aynan kimi davomati kerakligini login orqali aniqlashtirib oladi
def get_davomat(login):
    m_cookies = main_cookies(login, '')
    if m_cookies:
        davomat_html = requests.get('https://student.andmiedu.uz/education/attendance', cookies=m_cookies).text
        soup = BeautifulSoup(davomat_html,'lxml')
        tbody = soup.find('tbody')
        trs = tbody.find_all('tr')
        db = []
        for tr in trs:
            tds = tr.find_all('td')
            data = {
                'semestr':tds[1].text,
                'dars_sanasi':tds[2].text,
                'fanlar':tds[3].text,
                'mashg\'ulot':tds[4].text,
                'sababli':tds[5].text,
                'soatlar':tds[6].text,
                'xodim':tds[7].text
            }
            db.append(data)
        return db
    else:
        return 'not_logged_in'


#d = auth('303201100507','7xGjBZ2Fa24eHKW')
main_cookies('303201100507','7xGjBZ2Fa24eHKW')
d = get_davomat('303201100507')
print(d)