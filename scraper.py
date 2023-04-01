import requests
from bs4 import BeautifulSoup
from db import db
import json
import pprint

# bazani borligini tekshirib olamiz
db.initialize()
# institut manzili
URL = 'https://student.andmiedu.uz'
# strukturasini o'zgartiryapman, ba'zi commentlar to'g'ri bo'lmasligi mumkin
class SCRAPER():
    def __init__(self, login, password):
        self.login = login
        self.password = password
        # shu asosiy cookielarni olib beruvchi funksiya bo'lib ishlashligi kerak
        
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

            req_login = requests.post(URL + '/dashboard/login',data=payload, cookies=dict(req.cookies), allow_redirects=False)
            output = dict(req_login.cookies)
            if '_frontendUser' in output:
                self.cookies = output
                return output
            else:
                self.cookies = False
                return False
        
        cookies = db.get_cookies(login)
        if cookies == False:
            auth_cookies = auth(login, password)
            if auth_cookies != False:
                db.insert_cookies(login, json.dumps(auth_cookies))
        elif cookies == 'expired':
            auth_cookies = auth(login, password)
            if auth_cookies != False:
                db.update_cookies(login, json.dumps(auth_cookies))
        else:
            self.cookies = cookies
    
    # shu funksiya True return qilsa, login va parol to'g'ri bo'ladi, va qolgan funksiyalar ham not_logged_in return qilmasligi kerak
    def is_everything_ok(self):
        if self.cookies != False:
            return True
        else:
            return False
    # nblarni olib beruvchi funksiya, dictionary return qiladi
    # aynan kimi davomati kerakligini login orqali aniqlashtirib oladi
    # Bu funksiya hozircha faqat bir dona o'qilyotgan semestrni oladi, kerak bo'lsa boshqalarini ham olsak bo'ladi keyinchalik
    def get_davomat(self):
        m_cookies = self.cookies
        if m_cookies != False:
            try:
                davomat_html = requests.get(URL + '/education/attendance', cookies=m_cookies).text
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
            except:
                return False
        else:
            return 'not_logged_in'

    # demak bu funksiya oraqali talabani zachotkasidagi baholarni olish mumkin
    def get_uzlashtirish(self):
        m_cookies = self.cookies
        if m_cookies != False:
            try:
                uzlashtirish_html = requests.get(URL + '/education/performance', cookies=m_cookies).text
                soup = BeautifulSoup(uzlashtirish_html, 'lxml')
                titles = soup.find_all('h3', class_='box-title')
                tbodies = soup.find_all('tbody')
                db = {}
                db_t = []
                for title in titles:
                    db_t.append(title.text)
                db['titles'] = db_t
                index = 0
                for tbody in tbodies:
                    trs = tbody.find_all('tr')
                    db_tbody = []
                    for tr in trs:
                        tds = tr.find_all('td')
                        data = {
                            'fan':tds[1].text.replace('\n','').strip(),
                            'jn':tds[2].text.replace('\n','').strip(),
                            'on':tds[3].text.replace('\n','').strip(),
                            'yn':tds[4].text.replace('\n','').strip()
                        }
                        db_tbody.append(data)
                    db[index] = db_tbody 
                    index += 1
                #pprint.pprint(db)
                return db
            except:
                return False
        else:
            return 'not_logged_in'




s = SCRAPER('303201100507','')
# d = s.get_davomat()
d = s.get_uzlashtirish()
print(d)