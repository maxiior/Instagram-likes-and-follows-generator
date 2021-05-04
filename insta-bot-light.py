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

driver = 0

PATH = "D:\\Python\\chromedriver.exe"
DAYS_TO_UNFOLLOW = 7
FOLLOWED_LIMIT = 7500
ADAPTATION_LEVEL = 2
MAX_FOLLOWED_PER_HOUR = 150


def main():
    global driver
    print('WELCOME TO IGBOT\n')

    login = input('Login: ')
    password = input('Password: ')
    target = input('Target: ')
    hours = input('How many hours should run?: ')
    driver = webdriver.Chrome(PATH)
    IGBot = InstagramBot(login, password, target, hours, driver)
    IGBot.run_bot()


class InstagramBot:
    def __init__(self, username, password, target, hours, driver):
        self.username = username
        self.driver = driver
        self.password = password
        self.target = target
        self.hours = hours
        self.adaptation = ADAPTATION_LEVEL
        self.current_followed_users_names = self.load_current_followed_data()
        self.current_followed_users_times = self.load_current_followed_data(
            'times')
        self.private_users_names = self.load_private_users()
        self.archived_users = self.load_archived_users()

    def load_current_followed_data(self, data='names'):
        tab = []
        if data == 'names':
            path = os.path.dirname(__file__) + "/" + \
                self.username + "_current_followed_users_names.txt"
        else:
            path = os.path.dirname(__file__) + "/" + \
                self.username + "_current_followed_users_times.txt"
        try:
            file = open(path, "r")
            for i in file:
                tab.append(i[:-1])
            file.close()
        except:
            file = open(path, "w")
            file.close()
        return tab

    def load_private_users(self):
        tab = []
        path = os.path.dirname(__file__) + "/" + \
            self.username + "_private_users_names.txt"
        try:
            file = open(path, "r")
            for i in file:
                tab.append(i[:-1])
            file.close()
        except:
            file = open(path, "w")
            file.close()
        return tab

    def load_archived_users(self):
        tab = []
        path = os.path.dirname(__file__) + "/" + \
            self.username + "_archived_users.txt"
        try:
            file = open(path, "r")
            for i in file:
                tab.append(i[:-1])
            file.close()
        except:
            file = open(path, "w")
            file.close()
        return tab

    def closeBrowser(self):
        self.driver.close()

    def login(self):
        self.driver.get("https://www.instagram.com/")
        time.sleep(2)
        user_name_elem = self.driver.find_element_by_xpath(
            "//input[@name='username']")
        user_name_elem.clear()
        user_name_elem.send_keys(self.username)
        password_elem = self.driver.find_element_by_xpath(
            "//input[@name='password']")
        password_elem.clear()
        password_elem.send_keys(self.password)
        password_elem.send_keys(Keys.RETURN)
        time.sleep(5)

    def get_my_follow_number(self, followers=True):
        followers = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#react-root > section > main')))
        sflw = B(followers.get_attribute('innerHTML'), 'html.parser')
        followers = sflw.findAll('span', {'class': 'g47SY'})
        i = 1
        if followers == False:
            i = 2
        f = followers[i].getText().replace(
            '.', '').replace(',', '.').replace(' ', '')
        if 'tys' in f:
            f = float(f[:-3])*10**3
            return f
        elif 'mln' in f:
            f = float(f[:-3])*10**6
            return f
        else:
            return float(f)

    def add_user_to_archive(self, name):
        self.archived_users.append(name)
        path = os.path.dirname(__file__) + "/" + \
            self.username + "_archived_users.txt"
        file = open(path, "a")
        file.write("%s\n" % name)
        file.close()

    def go_to_my_profile(self):
        self.driver.get('https://www.instagram.com/' + self.username + '/')

    def get_followers_list(self, user, times):
        self.driver.get('https://www.instagram.com/' + user + '/')
        time.sleep(self.adaptation*random.randint(3, 5))

        followers_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#react-root > section > main > div > header > section > ul > li:nth-child(2) > a > span')))
        followers_button.click()

        try:
            self.popup = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div/div/div[2]')))
        except:
            self.popup = WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div[2]')))

        for i in range(times):
            time.sleep(self.adaptation*0.5)
            self.driver.execute_script(
                'arguments[0].scrollTop = arguments[0].scrollHeight', self.popup)

        follow_buttons = []
        names = []

        b_popup = B(self.popup.get_attribute('innerHTML'), 'html.parser')
        follow_buttons_list = b_popup.findAll('button', {'class': 'sqdOP'})

        for i in range(len(follow_buttons_list)):
            single_follow_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'body > div.RnEpo.Yx5HN > div > div > div.isgrP > ul > div > li:nth-child({0}) > div > div.Pkbci > button'.format(i+1))))
            name = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'body > div.RnEpo.Yx5HN > div > div > div.isgrP > ul > div > li:nth-child({0}) > div > div.t2ksc > div.enpQJ > div.d7ByH > span > a'.format(i+1))))
            follow_buttons.append(single_follow_button)
            names.append(name)

        buttons_and_names = np.column_stack((follow_buttons, names))

        checked_buttons_and_names = []

        for i in buttons_and_names:
            if i[0].text.lower() == 'obserwuj':
                checked_buttons_and_names.append(i)

        return checked_buttons_and_names

    def follow(self, followers_list):
        i = 1
        for follower in followers_list:
            time.sleep(self.adaptation*random.randint(3, 5))
            if follower[0].text.lower() == 'obserwuj':
                follower[0].click()
                if self.check_if_private_account(i, follower[1].text) == False and follower[1].text not in self.archived_users:
                    print(' user followed : {0}'.format(follower[1].text))
                    self.append_current_followed_users(follower[1].text)
                else:
                    print(' account is private : {0}'.format(follower[1].text))
                    self.private_users_names.append(follower[1].text)
                    path = os.path.dirname(__file__) + "/" + \
                        self.username + "_private_users_names.txt"
                    file = open(path, "a")
                    file.write("%s\n" % follower[1].text)
                    file.close()
            i += 1

    def append_current_followed_users(self, user):
        self.current_followed_users_names.append(user)
        self.current_followed_users_times.append(time.time())
        path = os.path.dirname(__file__) + "/" + \
            self.username + "_current_followed_users_names.txt"
        file = open(path, "a")
        file.write("%s\n" % user)
        file.close()
        path = os.path.dirname(__file__) + "/" + \
            self.username + "_current_followed_users_times.txt"
        file = open(path, "a")
        file.write("%s\n" % time.time())
        file.close()

    def check_if_private_account(self, i, name):
        time.sleep(self.adaptation*random.randint(1, 2))
        if name in self.private_users_names:
            return True
        try:
            button = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'body > div.RnEpo.Yx5HN > div > div > div.isgrP > ul > div > li:nth-child({0}) > div > div.Pkbci > button'.format(i))))
            if button.text.lower() == 'wysłane zaproszenie':
                button.click()
                time.sleep(self.adaptation*random.randint(1, 2))
                button = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'body > div:nth-child(19) > div > div > div > div.mt3GC > button.aOOlW.-Cab_')))
                button.click()
                return True
            else:
                return False
        except:
            return False

    def clear_followed_users(self):
        self.go_to_my_profile()
        time.sleep(self.adaptation*random.randint(3, 5))

        followed_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#react-root > section > main > div > header > section > ul > li:nth-child(3) > a > span')))
        followed_button.click()

        self.popup = WebDriverWait(self.driver, 6).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div/div/div[2]')))

        followed = int(followed_button.text)/10

        for i in range(int(followed)):
            time.sleep(self.adaptation*0.5)
            self.driver.execute_script(
                'arguments[0].scrollTop = arguments[0].scrollHeight', self.popup)

        follow_buttons = []
        names = []

        b_popup = B(self.popup.get_attribute('innerHTML'), 'html.parser')
        follow_buttons_list = b_popup.findAll('button', {'class': 'sqdOP'})

        for i in range(len(follow_buttons_list)):
            name = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'body > div.RnEpo.Yx5HN > div > div > div.isgrP > ul > div > li:nth-child({0}) > div > div.t2ksc > div.enpQJ > div.d7ByH > span > a'.format(i+1))))
            if name.text in self.current_followed_users_names:
                if self.check_if_user_should_be_removed(name, DAYS_TO_UNFOLLOW) == True:
                    single_follow_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'body > div.RnEpo.Yx5HN > div > div > div.isgrP > ul > div > li:nth-child({0}) > div > div.Pkbci > button'.format(i+1))))
                    follow_buttons.append(single_follow_button)
                    names.append(name)

        buttons_and_names = np.column_stack((follow_buttons, names))

        for i in buttons_and_names:
            time.sleep(self.adaptation*random.randint(1, 2))
            if i[0].text.lower() == 'obserwowanie':
                i[0].click()
                time.sleep(self.adaptation*random.randint(1, 2))
                button = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'body > div:nth-child(19) > div > div > div > div.mt3GC > button.aOOlW.-Cab_')))
                button.click()
                self.remove_from_current_followed_users(i[1].text)
        time.sleep(self.adaptation*random.randint(1, 2))

    def remove_from_current_followed_users(self, name):
        i = self.current_followed_users_names.index(name)
        self.current_followed_users_names.remove(name)
        self.current_followed_users_times.pop(i)
        path = os.path.dirname(__file__) + "/" + \
            self.username + "_current_followed_users_names.txt"
        file = open(path, "w")
        for i in self.current_followed_users_names:
            file.write("%s\n" % i)
        file.close()
        path = os.path.dirname(__file__) + "/" + \
            self.username + "_current_followed_users_times.txt"
        file = open(path, "w")
        for i in self.current_followed_users_times:
            file.write("%s\n" % i)
        file.close()
        self.add_user_to_archive(name)

    def check_if_user_should_be_removed(self, user, days_to_unfollow=7):
        t = time.time()
        i = self.current_followed_users_names.index(user)
        if t - self.current_followed_users_times[i] >= days_to_unfollow*24*60*60:
            return True
        else:
            return False

    def run_bot(self):
        print('loging in : run')
        self.login()
        print('loging in : done')

        print('cleaning : run')
        self.clear_followed_users()
        print('cleaning : done')

        h = 0

        while h < int(self.hours):
            self.go_to_my_profile()
            followed_users_number = self.get_my_follow_number(followers=False)
            if followed_users_number + MAX_FOLLOWED_PER_HOUR >= FOLLOWED_LIMIT:
                print('err : too many followed users : {0}'.format(
                    followed_users_number))
                print('process\'ll start again in : 60.0m')
                time.sleep(3600)
                print('cleaning : run')
                self.clear_followed_users()
                print('cleaning : done')
            else:
                print('searching : run')
                followers_list = []
                i = 13
                while len(followers_list) < MAX_FOLLOWED_PER_HOUR:
                    followers_list = self.get_followers_list(self.target, i)
                    i += 1
                followers_list = followers_list[:MAX_FOLLOWED_PER_HOUR]
                print('searching : done')

                start = time.time()
                print('following : run')
                self.follow(followers_list)
                stop = time.time()

                wait = 60 - (stop - start)/60
                print('hourly limit used')
                print('need to wait :', round(wait, 1), 'm')
                time.sleep(3600-(stop-start))
                h += 1

        print('following : done')


if __name__ == '__main__':
    main()
