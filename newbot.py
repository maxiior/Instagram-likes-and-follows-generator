from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as B

from selenium.webdriver.common.keys import Keys

import time
import random
import os
import re
import pandas as pd
import getpass

DRIVER = None
DAYS_TO_UNFOLLOW = 7
MAX_FOLLOWED_PER_HOUR = 150
FOLLOWED_LIMIT = 7500
MAX_FOLLOWING = 1000
TARGETS = "jakubroskosz,karolina_pisarek,thenitrozyniak,isamupt,kacperblonsky,gordziejewska.biznes,czarny_polak_,adam.lochynski,sukcespl,kuuuubs,pudzianofficial,sawardega_wataha,zacefron,alexcosta,kamil_szymczak,littlemooonster96"

#wujekrada,wojtekgola,boxdel,

def main():
    global DRIVER
    print('WELCOME TO INSTAGRAM BOT\n')

    username = input('login : ')
    password = getpass.getpass('password : ')
    targets = input('targets : ')
    hours = input('how many hours should run? : ')
    limit = input('followers limit that BOT should follow : ')
    DRIVER = webdriver.Chrome()
    IGBot = InstagramBot(DRIVER, username, password, targets, hours, limit)
    IGBot.run()

class InstagramBot:
    def __init__(self, driver, username, password, targets, hours, limit):
        targets = TARGETS if targets == "" else targets

        self.driver = driver
        self.username = username
        self.password = password
        self.targets = targets.split(",")
        self.hours = 24 if hours == "" else hours
        self.limit = MAX_FOLLOWING if limit == "" else float(limit)

        self.__adaptation = 2
        self.__users_data = self.__load_users_data()
        self.__web_driver_wait = WebDriverWait(self.driver, 100)
        self.__instagram_url = "https://www.instagram.com/"
        self.__current_url = None
    
    def __load_users_data(self):
        if not os.path.isfile(f"./data/{self.username}_users_data.csv"):
            df = pd.DataFrame({"username": [], "time": [], "followed": [], "private": [], "notavaliable": [], "toomanyfollowers": [], "liked": [], "target": [], "followedback": [], "cantunfollow": []})
            df.to_csv(f"./data/{self.username}_users_data.csv", index=False)
        return pd.read_csv(f"./data/{self.username}_users_data.csv")

    def __login(self):
        self.driver.get(self.__instagram_url)
        self.__current_url = self.driver.current_url

        username_textbox = self.__web_driver_wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='username']")))
        password_textbox = self.__web_driver_wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='password']")))
        username_textbox.clear()
        username_textbox.send_keys(self.username)
        password_textbox.clear()
        password_textbox.send_keys(self.password)
        password_textbox.send_keys(Keys.RETURN)
    
    def __wait_until_page_changes(self):
        self.__web_driver_wait.until(EC.url_changes(self.__current_url))
        
    def __get_users_to_unfollow(self, days_to_unfollow):
        records = self.__users_data[['username', 'time', 'followed']].to_records(index=False)
        usernames = []
        for (username, t, followed) in records:
            if time.time() - int(t) >= days_to_unfollow*24*60*60 and followed == True:
                usernames.append(username)
        return usernames

    def __save_users_data(self):
        self.__users_data.to_csv(f"./data/{self.username}_users_data.csv", index=False)

    def __unmark_followed_user(self, user, followedback, cantunfollow):
        self.__users_data.loc[self.__users_data['username'] == user, 'followed'] = False
        self.__users_data.loc[self.__users_data['username'] == user, 'followedback'] = followedback
        self.__users_data.loc[self.__users_data['username'] == user, 'cantunfollow'] = cantunfollow
        self.__save_users_data()

    def __clear_current_followed_users(self):
        users_to_unfollow = self.__get_users_to_unfollow(DAYS_TO_UNFOLLOW)
        print(f'    info - users to unfollow: {len(users_to_unfollow)}')

        if len(users_to_unfollow) != 0:
            
            for i in users_to_unfollow:
                self.driver.get(f'{self.__instagram_url}{i}/')
                time.sleep(6)

                try:
                    button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@id, "mount_0_0")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div[1]/button/div/div[1]')))

                    time.sleep(6)

                    if button.text.lower() == 'obserwowanie':
                        button.click()
                        time.sleep(6)
                        button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div/div[8]')))
                        button.click()
                        time.sleep(6)

                        try:
                            button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@id, "mount_0_0")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div/button/div/div')))
                        except:
                            button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@id, "mount_0_0")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div[1]/button/div/div')))

                        followedback = True if button.text.lower() == 'również obserwuj' else False

                        self.__unmark_followed_user(i, followedback, False)
                        print(f'    info - user has been unfollowed: {i}')
                    elif button.text.lower() == 'również obserwuj':
                        self.__unmark_followed_user(i, True, False)
                        print(f'    info - user has been already unfollowed: {i}')
                    elif button.text.lower() == 'obserwuj':
                        self.__unmark_followed_user(i, False, False)
                        print(f'    info - user has been already unfollowed: {i}')
                except:
                    print(f'    err - user is unavailable: {i}')
                    self.__mark_error(i)
                    time.sleep(8)
    
    def __mark_error(self, user):
        self.__users_data.loc[self.__users_data['username'] == user, 'cantunfollow'] = True
        self.__save_users_data()

    def __get_following_number(self):
        try:
            following_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@id, "mount_0_0")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[2]/a/span/span')))
            return int(re.sub(r'\D', '', following_button.text))
        except:
            try:
                following_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@id, "mount_0_0")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[2]/span/span')))
                return int(re.sub(r'\D', '', following_button.text))
            except:
                return -1

    def __get_followed_number(self):
        followed_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@id, "mount_0_0")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[3]/a')))

        return int(re.sub(r'\D', '', followed_button.text))
    
    def __get_users_to_follow_list_part(self, username, current_list, times):
        self.driver.get(f'{self.__instagram_url}{username}/')
        users_to_follow = []
        flag = False

        following_button = self.__web_driver_wait.until(EC.presence_of_element_located((By.XPATH, '//*[contains(@id, "mount_0_0")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[2]/a')))
        following_button.click()

        try:
            self.popup = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]')))
        except:
            self.popup = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]')))

        limited = False

        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f'/html/body/div[5]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[1]/span')))
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', self.popup)
            flag = True
            limited = True
        except:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f'/html/body/div[6]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[1]/span')))
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', self.popup)
            flag = True
            limited = True
            
        
        if not limited:
            for _ in range(times):
                self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', self.popup)
                time.sleep(2)

        time.sleep(5)
        follow_buttons_list = B(self.popup.get_attribute('innerHTML'), 'html.parser').findAll('button', string="Obserwuj") + B(self.popup.get_attribute('innerHTML'), 'html.parser').findAll('button', string="Obserwowanie")

        div_1 = 5
        div_2 = 2
        found = False

        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f'/html/body/div[5]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div/div/div[2]/div/div/div/div/div/a/div/div/span')))
            found = True
        except:
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f'/html/body/div[5]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[1]/div/div[1]/div/div/div/div[2]/div/div/div/div/div/a/div/div/span')))
                div_2 = 1
                found = True
            except:
                div_1 = 6
        
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f'/html/body/div[6]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div/div/div[2]/div/div/div/div/div/a/div/div/span')))
            found = True
        except:
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f'/html/body/div[6]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[1]/div/div[1]/div/div/div/div[2]/div/div/div/div/div/a/div/div/span')))
                div_2 = 1
                found = True
            except:
                pass

        if not found:
            print('    err - xpath not found')
            exit()

        for idx, _ in enumerate(follow_buttons_list):
            name = self.__web_driver_wait.until(EC.presence_of_element_located((By.XPATH, f'/html/body/div[{div_1}]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[{div_2}]/div/div[{idx+1}]/div/div/div/div[2]/div/div/div/div/div/a/div/div/span')))

            if not name.text in self.__users_data['username'].tolist() and not name.text in current_list:
                users_to_follow.append((name.text, username))

        return users_to_follow, flag

    def __get_users_to_follow_list(self):
        users_to_follow, drop_from_targets = [], []
        i = 13
        done = False
        targets = self.targets

        while len(users_to_follow) < MAX_FOLLOWED_PER_HOUR:
            for j in targets:
                tmp_list, flag = self.__get_users_to_follow_list_part(j, [k[1] for k in users_to_follow], i)
                users_to_follow += tmp_list
                print(f'    info - searched users: {len(users_to_follow)}')
                if flag:
                    drop_from_targets.append(j)
                if len(users_to_follow) >= MAX_FOLLOWED_PER_HOUR:
                    done = True
                    break
            
            for j in drop_from_targets:
                targets.remove(j)
            drop_from_targets = []

            if done:
                break
            i += 1

        return users_to_follow[:MAX_FOLLOWED_PER_HOUR]

    def __add_to_users_data(self, username, followed, private, notavaliable, toomanyfollowers, liked, target, followedback, cantunfollow):
        row = {'username': username, 'time': time.time(), "followed": followed, "private": private, "notavaliable": notavaliable, "toomanyfollowers": toomanyfollowers, "liked": liked, "target": target, "followedback": followedback, "cantunfollow": cantunfollow}
        self.__users_data.loc[len(self.__users_data)] = row
        self.__users_data.to_csv(f"./data/{self.username}_users_data.csv", index=False)

    def __like_post(self):
        try:
            number_of_posts = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@id, "mount_0_0")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/ul/li[1]/span/span')))
            number_of_posts = int(number_of_posts.text)
        except:
            number_of_posts = 1

        if number_of_posts > 0:
            try:
                post = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@id, "mount_0_0")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/div[3]/article/div[1]/div/div[1]/div[1]/a')))
            except:
                try:
                    post = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@id, "mount_0_0")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/div[3]/article/div/div/div[1]/div[1]/a')))
                except:
                    try:
                        post = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@id, "mount_0_0")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/div[3]/article/div/div/div/div[1]/a')))
                    except:
                        return False
            try:
                post.click()
                time.sleep(4)
                like_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@id, "mount_0_0")]/div/div/div[3]/div/div/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/section[1]/span[1]/div/div')))
                like_button.click()
                time.sleep(4)

                print(f'    info - post has been liked')
                
                return True
            except:
                return False
        else:
            return False

    def __account_lockout_detection(self):
        while True:
            try:
                div = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@id, "mount_0_0")]/div/div/div[2]/div/div/div/div[1]/div[1]/div/div[1]/span')))

                if div.text.lower() == 'coś poszło nie tak':
                    print(f'    err - your account has probably been temporarily blocked. Work will resume in 60.0m')
                    time.sleep(3600)
            except:
                break

    def __follow_user(self):
        try:
            button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@id, "mount_0_0")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div[1]/button/div/div')))
        except:
            try:
                button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@id, "mount_0_0")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div/button/div/div')))
            except:
                return -1

        try:
            button.click()
            time.sleep(5)

            if button.text.lower() == 'wysłane zaproszenie':
                button.click()
                time.sleep(4)
                
                button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[1]/div/div[2]/div/div/div/div/div/div/button[1]')))
                button.click()
                time.sleep(4)
                return 1
            else:
                button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[contains(@id, "mount_0_0")]/div/div/div[2]/div/div/div/div[1]/div[1]/div[2]/div[2]/section/main/div/header/section/div[1]/div[1]/div/div[1]/button/div/div[1]')))

                if button.text.lower() == 'obserwowanie':
                    return 0
                else:    
                    return -1
        except:
            return -1
        
    def __following_loop(self, users_to_follow):
        for username in users_to_follow:
            self.driver.get(f'{self.__instagram_url}{username[0]}/')
            self.__wait_until_page_changes()
            time.sleep(self.__adaptation*random.randint(6, 14))
            self.__current_url = self.driver.current_url

            self.__account_lockout_detection()

            followed_flag = False
            private_flag = False
            notavaliable_flag = False
            toomanyfollowers_flag = False
            liked_flag = False

            following_number = self.__get_following_number()
            
            if following_number == -1:
                notavaliable_flag = True
                print(f'    err - user is unavailable: {username[0]}')
            elif following_number > self.limit:
                toomanyfollowers_flag = True
                print(f'    err - too many followers: {username[0]}')
            else:
                status = self.__follow_user()
                if status == 1:
                    private_flag = True
                    print(f'    err - user is private: {username[0]}')
                elif status == -1:
                    notavaliable_flag = True
                    print(f'    err - user is unavailable: {username[0]}')
                elif status == 0:
                    followed_flag = True
                    print(f'    info - user has been followed: {username[0]}')
            
            liked_flag = self.__like_post()
            self.__add_to_users_data(username[0], followed_flag, private_flag, notavaliable_flag, toomanyfollowers_flag, liked_flag, username[1], False, False)

    def run(self):
        print('loging in : run')
        self.__login()
        print('loging in : done')
        self.__wait_until_page_changes()

        hours = 0

        while hours < int(self.hours):
            print('clearing : run')
            self.__clear_current_followed_users()
            print('clearing : done')
            time.sleep(4)
            
            self.driver.get(f'{self.__instagram_url}{self.username}/')
            my_followed_number = self.__get_followed_number()
            print(f'    info - my followed users number: {my_followed_number}')
            time.sleep(4)

            if my_followed_number + MAX_FOLLOWED_PER_HOUR >= FOLLOWED_LIMIT:
                print(f'    err - too many followed users : {my_followed_number}')
                print('process\'ll start again in : 60.0m')
                time.sleep(3600)
            else:
                print('searching : run')
                users_to_follow = self.__get_users_to_follow_list()
                print('searching : done')

                start = time.time()
                print('following : run')
                self.__following_loop(users_to_follow)
                stop = time.time()

                wait = 60 - (stop - start)/60
                print('hourly limit used')
                print('need to wait :', round(wait, 1) if wait > 0 else 30, 'm')

                wait = 3600-(stop-start)

                if wait > 0:
                    time.sleep(wait)
                else:
                    time.sleep(1800)

                hours += 1

main()