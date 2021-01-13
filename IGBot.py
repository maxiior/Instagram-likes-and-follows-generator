from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as B

from selenium.webdriver.common.keys import Keys

import time
import random
import os

driver = 0
path = "C:\\Python\\chromedriver.exe"
max_likes = 60
max_follows = 60

def main():
    global driver
    print('WELCOME TO IGBOT\n')

    login = input('Login: ')
    password = input('Password: ')
    target = input('Target: ')
    hours = input('How many hours should run?: ')
    limit = float(input('Followers limit that BOT should follow: '))
    driver = webdriver.Chrome(path)
    IGBot = InstagramBot(login, password, target, hours, limit, driver)
    IGBot.run_bot()

class InstagramBot:
    def __init__(self, username, password, target, hh, followers_limit, driver):
        self.followers_limit = int(followers_limit) 
        self.username = username
        self.all_hrefs = self.load_all_hrefs()
        self.cur_hrefs = self.load_cur_hrefs()
        self.cur_hrefs_time = self.load_cur_hrefs_times()
        self.prv_hrefs = self.load_prv_hrefs()
        self.too_many_followers_hrefs = self.load_too_many_followers_hrefs()
        self.driver = driver
        self.password = password
        self.hrefs = []
        self.target = target
        self.hh = hh
        self.adaptation = 2
    def closeBrowser(self):
        self.driver.close()
    def login(self):
        self.driver.get("https://www.instagram.com/")
        time.sleep(2)
        user_name_elem = self.driver.find_element_by_xpath("//input[@name='username']")
        user_name_elem.clear()
        user_name_elem.send_keys(self.username)
        password_elem = self.driver.find_element_by_xpath("//input[@name='password']")
        password_elem.clear()
        password_elem.send_keys(self.password)
        password_elem.send_keys(Keys.RETURN)
        time.sleep(5)
    def get_followers_number(self):
        followers = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#react-root > section > main')))
        sflw = B(followers.get_attribute('innerHTML'), 'html.parser')
        followers = sflw.findAll('span', {'class':'g47SY'})
        f = followers[1].getText().replace('.','').replace(',', '.').replace(' ', '')
        if 'tys' in f:
            f = float(f[:-3])*10**3
            return float(f)
        elif 'mln' in f:
            f = float(f[:-3])*10**6
            return float(f)
        else:
            return float(f)
    def get_my_followed_number(self):
        self.driver.get('https://www.instagram.com/' + self.username + '/')
        followers = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#react-root > section > main')))
        sflw = B(followers.get_attribute('innerHTML'), 'html.parser')
        followers = sflw.findAll('span', {'class':'g47SY'})
        f = followers[2].getText().replace('.','').replace(',', '.').replace(' ', '')
        if 'tys' in f:
            f = float(f[:-3])*10**3
            return f
        elif 'mln' in f:
            f = float(f[:-3])*10**6
            return f
        else:
            return float(f)
    def get_followers_hrefs(self, user, times):
        self.driver.get('https://www.instagram.com/' + user + '/')
        time.sleep(self.adaptation*random.randint(3,5))
        followers_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#react-root > section > main > div > header > section > ul > li:nth-child(2) > a > span')))
        followers_button.click()
        try:
            self.popup = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div[2]')))
        except:
            try:
                self.popup = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div/div[2]')))
            except:
                self.popup = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div[2]')))
        for i in range(3):
            time.sleep(self.adaptation*1)
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight/{}'.format(str(11-i)), self.popup)
        for i in range(times):
            time.sleep(self.adaptation*2)
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', self.popup)
        b_popup = B(self.popup.get_attribute('innerHTML'), 'html.parser')
        temp_hrefs = []
        for i in b_popup.findAll('li'):
            try:
                hlink = i.findAll('a')[0]['href']
                if 'div' in hlink or hlink == '/'+self.username+'/':
                    continue
                elif self.verify_hlink(hlink) == True:
                    temp_hrefs.append(hlink)
                else:
                    continue
            except:
                pass
        return temp_hrefs
    def verify_hlink(self, hlink):
        for i in self.all_hrefs:
            if i == hlink:
                return False
        for i in self.prv_hrefs:
            if i == hlink:
                return False
        for i in self.too_many_followers_hrefs:
            if i == hlink:
                return False
        return True
    def get_specific_hrefs(self):
        x = 0
        temp_hrefs = []
        i = 10
        while x < 120:
            i += 2
            temp_hrefs = self.get_followers_hrefs(self.target, i)
            x = len(temp_hrefs)
        if x > 120:
            while x != 120:
                temp_hrefs.pop()
                x = len(temp_hrefs)
        self.hrefs = temp_hrefs
    def error(self):
        while True:
            try:
                err = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#main-message > h1 > span')))
                if err.text == 'Ta strona nie działa':
                    driver.refresh()
                else:
                    break
            except:
                break
    def is_public(self):
        try:
            astate = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME,'rkEop')))
            if astate.text == 'To konto jest prywatne':
                return False
            else:
                return True
        except:
            return True
    def is_existing(self):
        try:
            astate = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR,'body > div > div.page.-cx-PRIVATE-Page__body.-cx-PRIVATE-Page__body__ > div > div > h2')))
            if astate.text == 'Przepraszamy, ta strona jest niedostępna': 
                return False
            else:
                return True
        except:
            try:
                astate = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#react-root > section > main > div > h2')))
                if astate.text == 'Przepraszamy, ta strona jest niedostępna':
                    return False
                else:
                    return True
            except:
                return True
    def like_post(self):
        post = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#react-root > section > main > div > div._2z6nI > article > div:nth-child(1) > div > div:nth-child(1) > div:nth-child(1)')))
        html = post.get_attribute('innerHTML')
        h = B(html, 'html.parser')
        href = h.a['href']
        self.driver.get('https://www.instagram.com' + href)
        time.sleep(self.adaptation*2)
        like_button = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#react-root > section > main > div > div.ltEKP > article > div.eo2As > section.ltpMr.Slqrh > span.fr66n > button > div > span > svg')))
        like_button.click()
    def follow_page(self):
        try:
            follow = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button')))
        except:
            follow = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[1]/button')))
        f_text = follow.text
        if f_text.lower() == 'obserwuj':
            follow.click()

    def app_all_hrefs(self, i):
        there = os.path.dirname(__file__) + "/" + self.username + "_all_hrefs.txt"
        file = open(there, "a")
        file.write("%s\n" % i)
        file.close()
    def load_all_hrefs(self):
        tab = []
        there =  os.path.dirname(__file__) + "/" + self.username + "_all_hrefs.txt" 
        try:
            file = open(there, "r")
            for i in file:
                tab.append(i[:-1])
            file.close()
        except:
            file = open(there, "w")
            file.close()
        return tab
    def app_cur_hrefs(self, i):
        there = os.path.dirname(__file__) + "/" + self.username +  "_cur_hrefs.txt"
        file = open(there, "a")
        file.write("%s\n" % i)
        file.close()
        there = os.path.dirname(__file__) + "/" + self.username +  "_cur_hrefs_time.txt"
        file = open(there, "a")
        file.write("%f\n" % time.time())
        file.close()
    def app_prv_hrefs(self, i):
        there = os.path.dirname(__file__) + "/" + self.username + "_prv_hrefs.txt"
        file = open(there, "a")
        file.write("%s\n" % i)
        file.close()
    def app_too_many_followers_hrefs(self, i):
        self.too_many_followers_hrefs.append(i)
        there = os.path.dirname(__file__) + "/" + self.username + "_" + str(self.followers_limit) + "_too_many_followers_hrefs.txt"
        file = open(there, "a")
        file.write("%s\n" % i)
        file.close()    
    def save_cur_hrefs(self):
        there = os.path.dirname(__file__) + "/" + self.username + "_cur_hrefs.txt"
        file = open(there, "w")
        for i in self.cur_hrefs:
            file.write("%s\n" % i)
        file.close()
        there = os.path.dirname(__file__) + "/" + self.username + "_cur_hrefs_time.txt"
        file = open(there, "w")
        for i in self.cur_hrefs_time:
            file.write("%s\n" % i)
        file.close()
    def app_me_hrefs(self, me_hrefs):
        there = os.path.dirname(__file__) + "/" + self.username + "_me_hrefs.txt"
        file = open(there, "a")
        file.write("%s\n" % me_hrefs)
        file.close()
    def load_cur_hrefs(self):
        tab = []
        there = os.path.dirname(__file__) + "/" + self.username + "_cur_hrefs.txt"
        try:
            file = open(there, "r")
            for i in file:
                tab.append(i[:-1])
            file.close()
        except:
            file = open(there, "w")
            file.close()
        return tab
    def load_cur_hrefs_times(self):
        tab = []
        there = os.path.dirname(__file__) + "/" + self.username + "_cur_hrefs_time.txt"
        try:
            file = open(there, "r")
            for i in file:
                tab.append(float(i[:-1]))
            file.close()
        except:
            file = open(there, "w")
            file.close()
        return tab
    def load_prv_hrefs(self):
        tab = []
        there = os.path.dirname(__file__) + "/" + self.username + "_prv_hrefs.txt"
        try:
            file = open(there, "r")
            for i in file:
                tab.append(i[:-1])
            file.close()
        except:
            file = open(there, "w")
            file.close()
        return tab
    def load_too_many_followers_hrefs(self):
        tab = []
        there = os.path.dirname(__file__) + "/" + self.username + "_" + str(self.followers_limit) + "_too_many_followers_hrefs.txt"
        try:
            file = open(there, "r")
            for i in file:
                tab.append(i[:-1])
            file.close()
        except:
            file = open(there, "w")
            file.close()
        return tab

    def app_update_follow_me_hrefs(self, href):
        there = os.path.dirname(__file__) + "/" + self.username + "_update_follow_me_hrefs.txt"
        file = open(there, "a")
        file.write("%s\n" % href)
        file.close()
    def load_update_follow_me_hrefs(self):
        tab = []
        there = os.path.dirname(__file__) + "/" + self.username + "_update_follow_me_hrefs.txt"
        try:
            file = open(there, "r")
            for i in file:
                tab.append(i[:-1])
            file.close()
        except:
            file = open(there, "w")
            file.close()
        return tab
    def check_update_follow_me_hrefs(self, tab, href):
        for x in tab:
            if x == href:
                return True
        return False
    def final_update(self, update_follow_me_hrefs):
        there = os.path.dirname(__file__) + "/" + self.username + "_update_follow_me_hrefs.txt"
        file = open(there, "w")
        for i in update_follow_me_hrefs:
            file.write("%s\n" % i)
        file.close()

    #def get_statistics(self, cur_hrefs_size, afterdays):
    #    there = os.path.dirname(__file__) + "/" + self.username + "_statistics.txt"
    #    file = open(there, "a")
    #    file.write("%d %d\n" % (cur_hrefs_size, afterdays))
    #    file.close()
    def clear_cur_hrefs(self, days):
        two_days = 172800
        days = days*24*60*60
        update_follow_me_hrefs = self.load_update_follow_me_hrefs()
        i = 0
        while i != len(self.cur_hrefs_time):
            if two_days <= (time.time() - self.cur_hrefs_time[i]) < days:
                if self.check_update_follow_me_hrefs(update_follow_me_hrefs, self.cur_hrefs[i]) == False:
                    if self.check_if_follow_me(self.cur_hrefs[i]) == False:
                        self.cur_hrefs.remove(self.cur_hrefs[i])
                        self.cur_hrefs_time.remove(self.cur_hrefs_time[i])
                        self.save_cur_hrefs()
                        time.sleep(self.adaptation*random.randint(5,7))
                    else:
                        self.app_update_follow_me_hrefs(self.cur_hrefs[i])
                        i += 1
                else:
                    i += 1
            elif (time.time() - self.cur_hrefs_time[i]) >= days:
                if self.check_if_follow_me(self.cur_hrefs[i]):
                    self.app_me_hrefs(self.cur_hrefs[i])
                    self.unfollow(self.cur_hrefs[i])
                    update_follow_me_hrefs.remove(self.cur_hrefs[i])
                    self.cur_hrefs.remove(self.cur_hrefs[i])
                    self.cur_hrefs_time.remove(self.cur_hrefs_time[i])
                    self.save_cur_hrefs()
                    self.final_update(update_follow_me_hrefs)
                else:
                    try:
                        update_follow_me_hrefs.remove(self.cur_hrefs[i])
                    except:
                        pass
                    self.cur_hrefs.remove(self.cur_hrefs[i])
                    self.cur_hrefs_time.remove(self.cur_hrefs_time[i])
                    self.save_cur_hrefs()
                time.sleep(self.adaptation*random.randint(5,7))
            else:
                i += 1

    def check_if_follow_me(self, account):
        driver.get('https://www.instagram.com' + account)
        self.error()
        if self.is_existing():
            time.sleep(self.adaptation*random.randint(1,2))
            try:
                follow_button = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div[2]/div/span/span[1]/button')))
            except:
                try:
                    follow_button = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[1]/button')))
                except: 
                    follow_button = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/span/span[1]/button')))
            if follow_button.text.lower() == 'obserwuj':
                return False 
            follow_button.click()
            try:
                unfollow_button = WebDriverWait(self.driver, 8).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div/div[3]/button[1]')))
            except:
                unfollow_button = WebDriverWait(self.driver, 8).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[2]/span/span[1]/button')))
            time.sleep(self.adaptation*random.randint(1,2))
            unfollow_button.click()
            try:
                follow = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button')))
                f_text = follow.text
                if f_text.lower() == 'również obserwuj':
                    time.sleep(self.adaptation*random.randint(1,2))
                    follow.click()
                    time.sleep(self.adaptation*random.randint(4,6))
                    return True
                else:
                    return False
            except:
                return False
        else:
            return False
    def unfollow(self, account):
        driver.get('https://www.instagram.com' + account)
        try:
            follow_button = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[2]/span/span[1]/button')))
        except:
            try:
                follow_button = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[1]/button')))
            except:
                follow_button = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/span/span[1]/button')))
        time.sleep(self.adaptation*random.randint(1,2))
        follow_button.click()
        try:
            unfollow_button = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div[3]/button[1]')))
        except:
            unfollow_button = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[2]/span/span[1]/button')))
        time.sleep(self.adaptation*random.randint(1,2))
        unfollow_button.click()
    def followers_update(self, user):
        self.cur_hrefs.append(user)
        self.cur_hrefs_time.append(time.time())
        self.all_hrefs.append(user)
        self.app_all_hrefs(user)
        self.app_cur_hrefs(user)

    def run_bot(self):
        added = 0
        L = 0
        cL = 0
        F = 0
        cF = 0
        h = 0

        print('loging in : run')
        self.login()
        print('loging in : done')

        print('cleaning process : run')
        self.clear_cur_hrefs(7)
        print('cleaning proces : done')

        print('following process : run')    
        while h != self.hh:
            my_followed = self.get_my_followed_number()
            time.sleep(self.adaptation*random.randint(4,8))
            if my_followed + 60 > 7500:
                while my_followed + 60 > 7500:
                    print('followers limit used :', my_followed)
                    print('need to wait : 60.0m')
                    time.sleep(3600)
                    self.clear_cur_hrefs(7)
                    my_followed = self.get_my_followed_number()
            else:
                print('searching accounts : run')
                self.get_specific_hrefs()
                print('searching accounts : done') 
                time.sleep(self.adaptation*random.randint(4,8))
                tim_start = time.time()
                for r in self.hrefs:
                    undetected = 0
                    while undetected==0:
                        self.driver.get('https://www.instagram.com' + r)
                        self.error()           
                        time.sleep(self.adaptation*random.randint(4,7))
                        try:
                            if self.is_public() and self.is_existing():
                                if self.get_followers_number() < self.followers_limit:
                                    if F < max_follows: 
                                        try:
                                            self.follow_page()
                                            F += 1
                                            cF +=1
                                            print('page followed successfully : ', cF)
                                            self.followers_update(r)
                                            time.sleep(self.adaptation*random.randint(8,12))
                                        except:
                                            print('could not follow : still', cF)
                                    if L < max_likes:
                                        try:
                                            self.like_post()
                                            L += 1
                                            cL += 1
                                            print("post liked : ", cL)
                                            time.sleep(self.adaptation*random.randint(8,12))
                                        except:
                                            print('could not like : still ', cL)
                                    else:
                                        break
                                else:
                                    time.sleep(self.adaptation*random.randint(3,5))
                                    self.app_too_many_followers_hrefs(r)
                                    print('too many followers')
                            else:
                                print('account is private')
                                self.app_prv_hrefs(r)
                                time.sleep(self.adaptation*5)
                            undetected = 1
                            added = 0
                        except:
                            print('bot has been detected')
                            if added == 0:
                                self.adaptation *= 1.2
                                print('adaptation level has been increased to ', self.adaptation , ' level')
                                added = 1
                            print('need to wait : 30.0m')
                            time.sleep(1800)
                tim_wait = 3600 - (time.time() - tim_start)
                if tim_wait > 0:
                    print('hourly limit used')
                    print('need to wait :', round((tim_wait/60),1), 'm')
                    time.sleep(tim_wait)
                else:
                    print('TIME :', round((tim_wait/60),1), 'm')
                    print('need to wait : 10.0m')
                    time.sleep(600)
                F=0
                L=0
                h += 1
        print('following process : done')
        self.closeBrowser()

if __name__ == '__main__':
	main()	