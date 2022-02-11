from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as B

from selenium.webdriver.common.keys import Keys

import time
import random
import os
import numpy as np

DRIVER = None
PATH = "D:\\Python\\chromedriver.exe"

ADAPTATION = 2
MAX_LIKES_PER_HOUR = 60
MAX_FOLLOWS_PER_HOUR = 60
LIMIT_OF_FOLLOWED_ACCOUNTS = 7500
DAYS_TO_UNFOLLOW = 7


def main():
    global DRIVER
    print('WELCOME TO IGBOT\n')

    login = input('Login : ')
    password = input('Password : ')
    target = input('Target : ')
    hours = input('How many hours should run? : ')
    limit = float(input('Followers limit that BOT should follow : '))
    clearing_mode = input(
        'What type of clearing you want to use? [none/light/hard] : ')
    DRIVER = webdriver.Chrome(PATH)
    IGBot = InstagramBot(login, password, target, hours,
                         limit, clearing_mode, ADAPTATION, DRIVER)
    IGBot.run_bot()


class InstagramBot:
    def __init__(self, username, password, target, hours, followers_limit, clearing_mode, adaptation, driver):
        self.followers_limit = int(followers_limit)
        self.username = username
        self.all_hrefs = self.load_all_hrefs()
        self.cur_hrefs = self.load_current_hrefs()
        self.cur_hrefs_time = self.load_current_hrefs_times()
        self.prv_hrefs = self.load_private_hrefs()
        self.too_many_followers_hrefs = self.load_too_many_followers_hrefs()
        self.driver = driver
        self.password = password
        self.hrefs = []
        self.target = target
        self.hours = hours
        self.clearing_mode = clearing_mode
        self.adaptation = adaptation

    def closeBrowser(self):
        self.driver.close()

    def wait(self, a, b):
        time.sleep(self.adaptation*random.randint(a, b))

    def login(self):
        self.driver.get("https://www.instagram.com/")
        time.sleep(2)
        user_name_textbox = self.driver.find_element_by_xpath(
            "//input[@name='username']")
        password_textbox = self.driver.find_element_by_xpath(
            "//input[@name='password']")
        user_name_textbox.clear()
        user_name_textbox.send_keys(self.username)
        password_textbox.clear()
        password_textbox.send_keys(self.password)
        password_textbox.send_keys(Keys.RETURN)
        time.sleep(5)

    def get_followers_number(self):
        try:
            followers = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#react-root > section > main > div > header > section > ul > li:nth-child(2) > a > div > span')))
        except:
            followers = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#react-root > section > main > div > header > section > ul > li:nth-child(2) > div > span')))

        f = followers.text.replace(
            '.', '').replace(',', '.').replace(' ', '')
        if 'tys' in f:
            f = float(f[:-3])*10**3
            return float(f)
        elif 'mln' in f:
            f = float(f[:-3])*10**6
            return float(f)
        else:
            return float(f)

    def get_my_followed_accounts_number(self):
        self.driver.get('https://www.instagram.com/' + self.username + '/')
        followers = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#react-root > section > main > div > header > section > ul > li:nth-child(3) > a > div > span')))
        f = followers.text.replace(
            '.', '').replace(',', '.').replace(' ', '')
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
        self.wait(3, 5)
        followers_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#react-root > section > main > div > header > section > ul > li:nth-child(2) > a > div > span')))
        followers_button.click()
        try:
            self.popup = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div/div/div/div[2]')))
        except:
            print("ERROR: get_followers_hrefs")

        for i in range(times):
            self.wait(1, 2)
            self.driver.execute_script(
                'arguments[0].scrollTop = arguments[0].scrollHeight', self.popup)
        popup = B(self.popup.get_attribute('innerHTML'), 'html.parser')
        accounts = []
        for i in popup.findAll('li'):
            try:
                hlink = i.findAll('a')[0]['href']
                if 'div' in hlink or hlink == '/'+self.username+'/':
                    continue
                elif self.verify_hlink(hlink):
                    accounts.append(hlink)
                else:
                    continue
            except:
                pass
        return accounts

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

    def get_specific_accounts(self):
        number_of_selected_accounts = 0
        accounts = []
        i = 10
        while number_of_selected_accounts < 120:
            i += 10
            accounts = self.get_followers_hrefs(self.target, i)
            number_of_selected_accounts = len(accounts)
        if number_of_selected_accounts > 120:
            while number_of_selected_accounts != 120:
                accounts.pop()
                number_of_selected_accounts = len(accounts)
        self.hrefs = accounts

    def error(self):
        while True:
            try:
                err = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#main-message > h1 > span')))
                if err.text == 'Ta strona nie działa':
                    print('ERR: strona nie działa')
                    self.driver.refresh()
                else:
                    break
            except:
                break

    def is_account_public(self):
        try:
            information = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'rkEop')))
            if information.text == 'To konto jest prywatne':
                return False
            else:
                return True
        except:
            return True

    def is_account_existing(self):
        check = True

        try:
            information = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'body > div > div.page.-cx-PRIVATE-Page__body.-cx-PRIVATE-Page__body__ > div > div > h2')))
            if information.text == 'Przepraszamy, ta strona jest niedostępna':
                check = False
        except:
            pass

        try:
            information = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#react-root > section > main > div > div > h2')))
            if information.text == 'Przepraszamy, ta strona jest niedostępna':
                check = False
        except:
            pass

        return check

    def like_post(self):
        post = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#react-root > section > main > div > div._2z6nI > article > div:nth-child(1) > div > div:nth-child(1) > div:nth-child(1)')))
        href = B(post.get_attribute('innerHTML'), 'html.parser').a['href']
        self.driver.get('https://www.instagram.com' + href)
        self.wait(1, 2)
        like_button = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#react-root > section > main > div > div > article > div > div.qF0y9.Igw0E.IwRSH.eGOV_._4EzTm > div > div.eo2As > section.ltpMr.Slqrh > span.fr66n > button')))
        like_button.click()

    def follow_account(self):
        try:
            follow_button = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div/button')))
        except:
            print('ERROR: follow_account')
        button_text = follow_button.text
        if button_text.lower() == 'obserwuj':
            follow_button.click()

    def load_all_hrefs(self):
        hrefs = []
        file_path = os.path.dirname(__file__) + "/" + \
            self.username + "_all_hrefs.txt"
        try:
            file = open(file_path, "r")
            for i in file:
                hrefs.append(i[:-1])
            file.close()
        except:
            file = open(file_path, "w")
            file.close()
        return hrefs

    def load_current_hrefs(self):
        hrefs = []
        file_path = os.path.dirname(__file__) + "/" + \
            self.username + "_cur_hrefs.txt"
        try:
            file = open(file_path, "r")
            for i in file:
                hrefs.append(i[:-1])
            file.close()
        except:
            file = open(file_path, "w")
            file.close()
        return hrefs

    def load_current_hrefs_times(self):
        hrefs = []
        file_path = os.path.dirname(__file__) + "/" + \
            self.username + "_cur_hrefs_time.txt"
        try:
            file = open(file_path, "r")
            for i in file:
                hrefs.append(float(i[:-1]))
            file.close()
        except:
            file = open(file_path, "w")
            file.close()
        return hrefs

    def load_private_hrefs(self):
        hrefs = []
        file_path = os.path.dirname(__file__) + "/" + \
            self.username + "_prv_hrefs.txt"
        try:
            file = open(file_path, "r")
            for i in file:
                hrefs.append(i[:-1])
            file.close()
        except:
            file = open(file_path, "w")
            file.close()
        return hrefs

    def load_too_many_followers_hrefs(self):
        hrefs = []
        file_path = os.path.dirname(__file__) + "/" + self.username + "_" + \
            str(self.followers_limit) + "_too_many_followers_hrefs.txt"
        try:
            file = open(file_path, "r")
            for i in file:
                hrefs.append(i[:-1])
            file.close()
        except:
            file = open(file_path, "w")
            file.close()
        return hrefs

    def load_transitional_follow_me_hrefs(self):
        hrefs = []
        file_path = os.path.dirname(__file__) + "/" + \
            self.username + "_transitional_follow_me_hrefs.txt"
        try:
            file = open(file_path, "r")
            for i in file:
                hrefs.append(i[:-1])
            file.close()
        except:
            file = open(file_path, "w")
            file.close()
        return hrefs

    def append_all_hrefs(self, href):
        file_path = os.path.dirname(__file__) + "/" + \
            self.username + "_all_hrefs.txt"
        file = open(file_path, "a")
        file.write("%s\n" % href)
        file.close()

    def append_transitional_follow_me_hrefs(self, href):
        file_path = os.path.dirname(__file__) + "/" + \
            self.username + "_transitional_follow_me_hrefs.txt"
        file = open(file_path, "a")
        file.write("%s\n" % href)
        file.close()

    def append_current_hrefs(self, href):
        file_path = os.path.dirname(__file__) + "/" + \
            self.username + "_cur_hrefs.txt"
        file = open(file_path, "a")
        file.write("%s\n" % href)
        file.close()
        file_path = os.path.dirname(__file__) + "/" + \
            self.username + "_cur_hrefs_time.txt"
        file = open(file_path, "a")
        file.write("%f\n" % time.time())
        file.close()

    def append_private_hrefs(self, href):
        file_path = os.path.dirname(__file__) + "/" + \
            self.username + "_prv_hrefs.txt"
        file = open(file_path, "a")
        file.write("%s\n" % href)
        file.close()

    def append_too_many_followers_hrefs(self, href):
        self.too_many_followers_hrefs.append(href)
        file_path = os.path.dirname(__file__) + "/" + self.username + "_" + \
            str(self.followers_limit) + "_too_many_followers_hrefs.txt"
        file = open(file_path, "a")
        file.write("%s\n" % href)
        file.close()

    def save_current_hrefs(self):
        file_path = os.path.dirname(__file__) + "/" + \
            self.username + "_cur_hrefs.txt"
        file = open(file_path, "w")
        for i in self.cur_hrefs:
            file.write("%s\n" % i)
        file.close()
        file_path = os.path.dirname(__file__) + "/" + \
            self.username + "_cur_hrefs_time.txt"
        file = open(file_path, "w")
        for i in self.cur_hrefs_time:
            file.write("%s\n" % i)
        file.close()

    def append_hrefs_that_follow_me(self, href):
        file_path = os.path.dirname(__file__) + "/" + \
            self.username + "_me_hrefs.txt"
        file = open(file_path, "a")
        file.write("%s\n" % href)
        file.close()

    def check_if_in_transitional_follow_me_hrefs(self, tab, href):
        for i in tab:
            if i == href:
                return True
        return False

    def final_update(self, hrefs):
        file_path = os.path.dirname(__file__) + "/" + \
            self.username + "_transitional_follow_me_hrefs.txt"
        file = open(file_path, "w")
        for i in hrefs:
            file.write("%s\n" % i)
        file.close()

    def hard_clear_current_hrefs(self, days):
        TWO_DAYS_IN_SECONDS = 172800
        FEW_DAYS_IN_SECONDS = days*24*60*60
        transitional_follow_me_hrefs = self.load_transitional_follow_me_hrefs()
        i = 0
        while i != len(self.cur_hrefs_time):
            if TWO_DAYS_IN_SECONDS <= (time.time() - self.cur_hrefs_time[i]) < FEW_DAYS_IN_SECONDS:
                if self.check_if_in_transitional_follow_me_hrefs(transitional_follow_me_hrefs, self.cur_hrefs[i]) == False:
                    if self.check_if_account_follow_me(self.cur_hrefs[i]) == False:
                        self.cur_hrefs.remove(self.cur_hrefs[i])
                        self.cur_hrefs_time.remove(self.cur_hrefs_time[i])
                        self.save_current_hrefs()
                        self.wait(5, 7)
                    else:
                        self.append_transitional_follow_me_hrefs(
                            self.cur_hrefs[i])
                        i += 1
                else:
                    i += 1
            elif (time.time() - self.cur_hrefs_time[i]) >= FEW_DAYS_IN_SECONDS:
                if self.check_if_account_follow_me(self.cur_hrefs[i]):
                    self.append_hrefs_that_follow_me(self.cur_hrefs[i])
                    self.unfollow(self.cur_hrefs[i])
                    try:
                        transitional_follow_me_hrefs.remove(self.cur_hrefs[i])
                    except:
                        pass
                    self.cur_hrefs.remove(self.cur_hrefs[i])
                    self.cur_hrefs_time.remove(self.cur_hrefs_time[i])
                    self.save_current_hrefs()
                    self.final_update(transitional_follow_me_hrefs)
                else:
                    try:
                        transitional_follow_me_hrefs.remove(self.cur_hrefs[i])
                    except:
                        pass
                    self.cur_hrefs.remove(self.cur_hrefs[i])
                    self.cur_hrefs_time.remove(self.cur_hrefs_time[i])
                    self.save_current_hrefs()
                self.wait(5, 7)
            else:
                i += 1

    def light_clear_current_hrefs(self):
        self.driver.get('https://www.instagram.com/' + self.username + '/')
        self.wait(3, 5)

        followed_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#react-root > section > main > div > header > section > ul > li:nth-child(3) > a > span')))
        followed_button.click()

        self.popup = WebDriverWait(self.driver, 6).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div/div/div[3]')))

        for i in range(int(int(followed_button.text)/10)):
            time.sleep(self.adaptation*0.5)
            self.driver.execute_script(
                'arguments[0].scrollTop = arguments[0].scrollHeight', self.popup)

        follow_buttons = []
        names = []

        follow_buttons_list = B(self.popup.get_attribute(
            'innerHTML'), 'html.parser').findAll('button', {'class': 'sqdOP'})

        for i in range(len(follow_buttons_list)):
            name = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'body > div.RnEpo.Yx5HN > div > div > div.isgrP > ul > div > li:nth-child({0}) > div > div.t2ksc > div.enpQJ > div.d7ByH > span > a'.format(i+1))))
            if name.text in self.cur_hrefs:
                if self.check_if_user_should_be_removed(name, DAYS_TO_UNFOLLOW) == True:
                    single_follow_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'body > div.RnEpo.Yx5HN > div > div > div.isgrP > ul > div > li:nth-child({0}) > div > div.Pkbci > button'.format(i+1))))
                    follow_buttons.append(single_follow_button)
                    names.append(name)

        buttons_and_names = np.column_stack((follow_buttons, names))

        for i in buttons_and_names:
            self.wait(1, 2)
            if i[0].text.lower() == 'obserwowanie':
                i[0].click()
                self.wait(1, 2)
                button = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'body > div:nth-child(19) > div > div > div > div.mt3GC > button.aOOlW.-Cab_')))
                button.click()
                self.remove_from_current_followed_users(i[1].text)
        self.wait(1, 2)

    def check_if_user_should_be_removed(self, user, days_to_unfollow):
        if time.time() - self.cur_hrefs_time[self.cur_hrefs.index(user)] >= days_to_unfollow*24*60*60:
            return True
        else:
            return False

    def remove_from_current_followed_users(self, href):
        i = self.cur_hrefs.index(href)
        self.cur_hrefs.remove(href)
        self.cur_hrefs_time.pop(i)
        path = os.path.dirname(__file__) + "/" + \
            self.username + "_cur_hrefs.txt"
        file = open(path, "w")
        for i in self.cur_hrefs:
            file.write("%s\n" % i)
        file.close()
        path = os.path.dirname(__file__) + "/" + \
            self.username + "cur_hrefs_times.txt"
        file = open(path, "w")
        for i in self.cur_hrefs_times:
            file.write("%s\n" % i)
        file.close()

    def check_if_account_follow_me(self, href):
        self.driver.get('https://www.instagram.com' + href)
        self.wait(1, 2)
        self.error()
        if self.is_account_existing():
            self.wait(1, 2)
            try:
                follow_button = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div[2]/button')))
            except:
                try:
                    follow_button = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div/button')))
                except:
                    print('ERROR: check_if_account_follow_me')

            if follow_button.text.lower() == 'obserwuj':
                return False
            follow_button.click()
            try:
                unfollow_button = WebDriverWait(self.driver, 8).until(EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[5]/div/div/div/div[3]/button[1]')))
            except:
                try:
                    unfollow_button = WebDriverWait(self.driver, 8).until(EC.presence_of_element_located(
                        (By.XPATH, '/html/body/div[6]/div/div/div/div[3]/button[1]')))
                except:
                    print('ERROR: check_if_account_follow_me')
            self.wait(1, 2)
            unfollow_button.click()
            self.wait(1, 2)

            try:
                follow_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div/button')))
                if follow_button.text.lower() == 'również obserwuj':
                    self.wait(1, 2)
                    follow_button.click()
                    self.wait(4, 6)
                    return True
                else:
                    return False
            except:
                print('ERROR: check_if_account_follow_me')
        else:
            return False

    def unfollow(self, href):
        self.driver.get('https://www.instagram.com' + href)
        try:
            follow_button = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="react-root"]/section/main/div/header/section/div[1]/div[1]/div/div[2]/button')))
        except:
            print('ERROR: unfollow')
        self.wait(1, 2)
        follow_button.click()
        try:
            unfollow_button = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[5]/div/div/div/div[3]/button[1]')))
        except:
            try:
                unfollow_button = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[6]/div/div/div/div[3]/button[1]')))
            except:
                print('ERROR: unfollow')
        self.wait(1, 2)
        unfollow_button.click()

    def followers_update(self, href):
        self.cur_hrefs.append(href)
        self.cur_hrefs_time.append(time.time())
        self.all_hrefs.append(href)
        self.append_all_hrefs(href)
        self.append_current_hrefs(href)

    def run_bot(self):
        likes = 0
        current_likes = 0
        follows = 0
        current_follows = 0
        hours_running = 0

        print('loging in : run')
        self.login()
        print('loging in : done')

        print('cleaning process : run')
        if self.clearing_mode == 'light':
            self.light_clear_current_hrefs(DAYS_TO_UNFOLLOW)
        else:
            self.hard_clear_current_hrefs(DAYS_TO_UNFOLLOW)
        print('cleaning proces : done')

        print('following process : run')
        while hours_running != self.hours:
            my_followed_accounts = self.get_my_followed_accounts_number()
            print('number of accounts you are following : {0}'.format(
                int(my_followed_accounts)))
            self.wait(4, 8)
            if my_followed_accounts + 60 > LIMIT_OF_FOLLOWED_ACCOUNTS:
                while my_followed_accounts + 60 > LIMIT_OF_FOLLOWED_ACCOUNTS:
                    print('ERR: followers limit used :', my_followed_accounts)
                    print('need to wait : 60.0m')
                    time.sleep(3600)
                    self.hard_clear_current_hrefs(DAYS_TO_UNFOLLOW)
                    my_followed_accounts = self.get_my_followed_accounts_number()
            else:
                print('searching accounts : run')
                self.get_specific_accounts()
                print('searching accounts : done')
                self.wait(4, 8)
                time_start = time.time()
                for href in self.hrefs:
                    self.driver.get('https://www.instagram.com' + href)
                    self.wait(1, 2)
                    self.error()
                    self.wait(4, 6)
                    try:
                        if self.is_account_public() and self.is_account_existing():
                            if self.get_followers_number() < self.followers_limit:
                                if follows < MAX_FOLLOWS_PER_HOUR:
                                    try:
                                        self.follow_account()
                                        follows += 1
                                        current_follows += 1
                                        print(
                                            'followed pages : ', current_follows)
                                        self.followers_update(href)
                                        self.wait(8, 12)
                                    except:
                                        print(
                                            'ERR: could not follow : still', current_follows)
                                if likes < MAX_LIKES_PER_HOUR:
                                    try:
                                        self.like_post()
                                        likes += 1
                                        current_likes += 1
                                        print("liked posts : ",
                                              current_likes)
                                        self.wait(8, 12)
                                    except:
                                        print(
                                            'ERR: could not like : still ', current_likes)
                                else:
                                    break
                            else:
                                self.wait(3, 5)
                                self.append_too_many_followers_hrefs(href)
                                print('ERR: too many followers')
                        else:
                            print('ERR: account is private')
                            self.append_private_hrefs(href)
                            self.wait(4, 5)
                        undetected = 1
                        increased = False
                    except:
                        print('ERR: unexpected problem')
                time_wait = 3600 - (time.time() - time_start)
                if time_wait > 0:
                    print('hourly limit has been used')
                    print('need to wait :', round((time_wait/60), 1), 'm')
                    time.sleep(time_wait)
                else:
                    print('time exceeded :', round((time_wait/60), 1), 'm')
                    print('need to wait : 10.0m')
                    time.sleep(600)
                follows = 0
                likes = 0
                hours_running += 1
        print('following process : done')
        self.closeBrowser()


if __name__ == '__main__':
    main()
