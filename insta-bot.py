from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as B
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.keys import Keys

import matplotlib.pyplot as plt
import time
import random
import os
import re
import pandas as pd
import getpass
import logging

DRIVER = None
DAYS_TO_UNFOLLOW = 7
MAX_FOLLOWED_PER_HOUR = 150
FOLLOWED_LIMIT = 7500
MAX_FOLLOWING = 1000
TARGETS = "kamil_szymczak,jakubroskosz,karolina_pisarek,thenitrozyniak,isamupt,kacperblonsky,gordziejewska.biznes,czarny_polak_,adam.lochynski,sukcespl,kuuuubs,pudzianofficial,sawardega_wataha,zacefron,alexcosta,littlemooonster96,cristiano"

#wujekrada,wojtekgola,boxdel,

def main():
    global DRIVER
    print('WELCOME TO INSTAGRAM BOT\n')

    username = input('login : ')
    password = getpass.getpass('password : ')
    targets = input('targets : ')
    hours = input('how many hours should run? : ')
    limit = input('followers limit that BOT should follow : ')

    service = Service(executable_path='C:\Program Files\Google\chromedriver.exe')
    options = webdriver.ChromeOptions()
    DRIVER = webdriver.Chrome(service=service, options=options)

    IGBot = InstagramBot(username, password, targets, hours, limit)
    IGBot.run()

class Delay():
    DELAY = 8

    def delay(self, delay=None):
        if not delay:
            time.sleep(self.DELAY + random.randint(0, 4))
        else:
            time.sleep(delay)


class TimeLock(Delay):
    def __init__(self, url, wait_until_page_changes=False):
        super().__init__()
        self.__url = url
        self.__web_driver_wait = WebDriverWait(DRIVER, 10)
        self.__wait_until_page_changes = wait_until_page_changes

    def __enter__(self):
        self.delay()
        DRIVER.get(self.__url)
        self.delay()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__wait_until_page_changes:
            self.__web_driver_wait.until(EC.url_changes(self.__url))
        self.delay()


class InstagramBot(Delay):
    def __init__(self, username, password, targets, hours, limit):
        super().__init__()
        targets = TARGETS if targets == "" else targets

        logging.basicConfig(filename='./logs/bot.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)

        self.username = username
        self.password = password
        self.targets = targets.split(",")
        self.hours = 24 if hours == "" else hours
        self.limit = MAX_FOLLOWING if limit == "" else float(limit)

        self.__users_data = self.__load_users_data()
        self.__web_driver_wait = WebDriverWait(DRIVER, 100)
        self.__instagram_url = "https://www.instagram.com"
    
    def __make_report(self):
        df = pd.read_csv(f'./data/{self.username}_users_data.csv')
        if len(df) > 0:
            df_all = df.groupby('target').size().reset_index(name='count_all')
            df = df[df['followedback'] == True]
            df = df.groupby('target').size().reset_index(name='count_followedback')
            merged_df = pd.merge(df_all, df, on='target', how='left').fillna(0)
            merged_df['ratio'] = round(merged_df['count_followedback'] / merged_df['count_all'], 3)
            merged_df = merged_df.sort_values(by='ratio', ascending=False).reset_index().drop('index', axis=1)

            merged_df.to_csv('./archive/report.csv', index=False)

            merged_df = merged_df.rename(columns={'ratio': 'followsback_ratio'})
            merged_df.plot(x='target', y=['followsback_ratio'], kind='bar')
            plt.xlabel('')
            plt.savefig('./archive/followsback_ratio_report.png', bbox_inches="tight")

            plt.clf()

            merged_df = merged_df.rename(columns={'count_followedback': 'followsback_count'})
            merged_df.sort_values(by='followsback_count', ascending=False).plot(x='target', y=['followsback_count'], kind='bar')
            plt.xlabel('')
            plt.savefig('./archive/followsback_count_report.png', bbox_inches="tight")
            return True
        else:
            return False

    def __log(self, message, mode='info'):
        if mode == 'info':
            logging.info(message)
            print(f'    info - {message}')
        elif mode == 'error':
            logging.error(message)
            print(f'    err - {message}')
        else:
            logging.info(message)
            print(f'{message}')

    def __load_users_data(self):
        if not os.path.isfile(f"./data/{self.username}_users_data.csv"):
            df = pd.DataFrame({"username": [], "time": [], "followed": [], "private": [], "notavaliable": [], "toomanyfollowers": [], "liked": [], "target": [], "followedback": [], "cantunfollow": []})
            df.to_csv(f"./data/{self.username}_users_data.csv", index=False)
        return pd.read_csv(f"./data/{self.username}_users_data.csv")

    def __login(self):
        with TimeLock(self.__instagram_url, wait_until_page_changes=True):
            username_textbox = self.__web_driver_wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='username']")))
            password_textbox = self.__web_driver_wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='password']")))
            username_textbox.clear()
            username_textbox.send_keys(self.username)
            password_textbox.clear()
            password_textbox.send_keys(self.password)
            password_textbox.send_keys(Keys.RETURN)
        
    def __get_users_to_unfollow(self, days_to_unfollow):
        records = self.__users_data[['username', 'time', 'followed', 'cantunfollow']].to_records(index=False)
        usernames = []
        count_cantunfollow = 0

        for (username, t, followed, cantunfollow) in records:
            if time.time() - int(t) >= days_to_unfollow*24*60*60 and followed == True and cantunfollow == False:
                usernames.append(username)
            if cantunfollow:
                count_cantunfollow += 1
        return usernames, count_cantunfollow

    def __save_users_data(self):
        self.__users_data.to_csv(f"./data/{self.username}_users_data.csv", index=False)

    def __unmark_followed_user(self, user, followedback, cantunfollow):
        self.__users_data.loc[self.__users_data['username'] == user, 'followed'] = False
        self.__users_data.loc[self.__users_data['username'] == user, 'followedback'] = followedback
        self.__users_data.loc[self.__users_data['username'] == user, 'cantunfollow'] = cantunfollow
        self.__save_users_data()
    
    def __find_component_by_text(self, text):
        try:
            xpath = f"//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'{text}')]"
            return WebDriverWait(DRIVER, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except:
            return None
        
    def __check_if_text_in_page_source(self, text):
        return text in DRIVER.page_source

    def __clear_current_followed_users(self):
        users_to_unfollow, count_cantunfollow = self.__get_users_to_unfollow(DAYS_TO_UNFOLLOW)
        self.__log(message=f'users to unfollow: {len(users_to_unfollow)} (can\'t unfollow: {count_cantunfollow})', mode='info')

        if len(users_to_unfollow) > 0:
            for i in users_to_unfollow:
                with TimeLock(f'{self.__instagram_url}/{i}/'):
                    self.__account_lockout_detection()            
                    button = self.__find_component_by_text('obserwowanie')
                    if button:
                        button.click()
                        self.delay()
                        
                        button = self.__find_component_by_text('przestań obserwować')
                        button.click()
                        self.delay()

                        followedback_a = True if self.__find_component_by_text('także obserwuj') else False
                        followedback_b = True if self.__find_component_by_text('również obserwuj') else False

                        self.__unmark_followed_user(i, followedback_a or followedback_b, False)
                        self.__log(message=f'user has been unfollowed: {i}', mode='info')
                        continue
                    
                    button = self.__find_component_by_text('także obserwuj')
                    if button:
                        self.__unmark_followed_user(i, True, False)
                        self.__log(message=f'user has been already unfollowed: {i}', mode='info')
                        continue

                    button = self.__find_component_by_text('obserwuj')
                    if button:
                        self.__unmark_followed_user(i, False, False)
                        self.__log(message=f'user has been already unfollowed: {i}', mode='info')
                        continue
                    
                    self.__log(message=f'user is unavailable: {i}', mode='error')
                    self.__mark_error(i)
    
    def __mark_error(self, user):
        self.__users_data.loc[self.__users_data['username'] == user, 'cantunfollow'] = True
        self.__save_users_data()

    def __get_following_number(self):
        text = self.__find_component_by_text('obserwujących')
        if text == None:
            text = self.__find_component_by_text('obserwujący')
            if text == None:
                return None
            else:
                text = text.text.lower()
                return int(re.sub(r'\D', '', text))
        else:
            text = text.text.lower()
            if 'tys.' in text or 'mln' in text:
                return MAX_FOLLOWING + 1
            else:
                return int(re.sub(r'\D', '', text))

    def __get_followed_number(self):
        return int(self.__find_component_by_text('obserwowani:').text.lower().replace('obserwowani: ', ''))
    
    def __get_users_to_follow_list_part(self, source_name, current_list, times):
        with TimeLock(f'{self.__instagram_url}/{source_name}/followers'):
            self.__account_lockout_detection()
            
            if not self.__check_if_account_private():
                users_to_follow = []
                limited = True if self.__check_if_text_in_page_source('może zobaczyć wszystkich obserwujących') else False
                body = WebDriverWait(DRIVER, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body')))

                if not limited:
                    popup = DRIVER.find_element(By.CLASS_NAME, '_aano')
                    for _ in range(times):
                        DRIVER.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', popup)
                        self.delay(3)
                
                users = B(body.get_attribute('innerHTML'), 'html.parser').select('div > div > div > div > div > div > div > div > div > a > div > div > span')
                
                for i in users:
                    name = i.get_text()
                    if not name in self.__users_data['username'].tolist() and not name in current_list:
                        users_to_follow.append((name, source_name))
            else:
                self.__log(message=f'user is private: {source_name}', mode='error')
                return [], True

        return users_to_follow, limited

    def __get_targets_based_on_report(self):
        try:
            targets = pd.read_csv('archive/report.csv')['target'].tolist()
            not_visited_targets = list(set(self.targets) - set(targets))
            
            if len(not_visited_targets) > 0:
                rand_target = random.choice(not_visited_targets)
                targets.insert(0, rand_target)
                not_visited_targets.remove(rand_target)
                return targets + not_visited_targets
            return targets
        except:
            return self.targets

    def __get_users_to_follow_list(self):
        users_to_follow, drop_from_targets = [], []
        i = 7
        done = False
        targets = self.__get_targets_based_on_report()

        while len(users_to_follow) < MAX_FOLLOWED_PER_HOUR:
            for j in targets:
                tmp_list, limited = self.__get_users_to_follow_list_part(j, [k[1] for k in users_to_follow], i)
                users_to_follow += tmp_list
                self.__log(message=f'searched users: {len(users_to_follow)}', mode='info')
                if limited:
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
        self.__save_users_data() 

    def __like_post(self):
        try:
            photo = DRIVER.find_element(By.XPATH,'//a[contains(@href,"/p/")]')
            photo.click()

            self.delay()

            button = DRIVER.find_element(By.CSS_SELECTOR, '[aria-label="Lubię to!"]')
            button.click()

            return True
        except:
            return False

    def __account_lockout_detection(self):
        while True:
            self.delay()
            if self.__check_if_text_in_page_source('Coś poszło nie tak'):
                extra_wait = random.randint(0, 60)
                self.__log(message=f'your account has probably been temporarily blocked. Work will resume in {round(60+extra_wait, 1)}m', mode='error')
                self.delay(3600 + extra_wait*60)
                DRIVER.refresh()
            else:
                break

    def __check_if_account_private(self):
        return self.__check_if_text_in_page_source('To konto jest prywatne')

    def __follow_user(self):
        button = self.__find_component_by_text('obserwuj')
        if button:
            button.click()
            self.delay()
            return True
        else:
            return False
        
    def __following_loop(self, users_to_follow):
        follows = 0
        likes = 0

        for username in users_to_follow:
            with TimeLock(f'{self.__instagram_url}/{username[0]}/'):
                self.__account_lockout_detection()

                followed_flag = False
                private_flag = False
                notavaliable_flag = False
                toomanyfollowers_flag = False
                liked_flag = False

                following_number = self.__get_following_number()
                
                if following_number == None:
                    notavaliable_flag = True
                    self.__log(message=f'user is unavailable: {username[0]}', mode='error')
                elif following_number > self.limit:
                    toomanyfollowers_flag = True
                    self.__log(message=f'too many followers: {username[0]}', mode='error')
                else:
                    if self.__check_if_account_private():
                        private_flag = True
                        self.__log(message=f'user is private: {username[0]}', mode='error')
                    
                    if not private_flag and not notavaliable_flag and not toomanyfollowers_flag:
                        status = self.__follow_user()

                        if status:
                            followed_flag = True
                            follows += 1
                            self.__log(message=f'user has been followed: {username[0]} ({follows})', mode='info')
                        else:
                            notavaliable_flag = True
                            self.__log(message=f'user is unavailable: {username[0]}', mode='error')
                        
                        liked_flag = self.__like_post()

                        if liked_flag:
                            likes += 1
                            self.__log(message=f'{username[0]} photo has been liked ({likes})', mode='info')
                        else:
                            self.__log(message=f'can\'t like {username[0]} photo', mode='error')

                self.__add_to_users_data(username[0], followed_flag, private_flag, notavaliable_flag, toomanyfollowers_flag, liked_flag, username[1], False, False)

    def run(self):
        self.__log('loging in : run', mode='else')
        self.__login()
        self.__log('loging in : done', mode='else')

        hours = 0

        while hours < int(self.hours):
            self.__log('clearing : run', mode='else')
            self.__clear_current_followed_users()
            self.__log('clearing : done', mode='else')

            self.__log('making report : run', mode='else')
            status = self.__make_report()
            if status:
                self.__log('making report : done', mode='else')
            else:
                self.__log(message=f'not enough data to create a report yet', mode='error')
                self.__log('making report : done', mode='else')
            
            with TimeLock(f'{self.__instagram_url}/{self.username}/'):
                self.__account_lockout_detection()
                my_followed_number = self.__get_followed_number()
                self.__log(message=f'my followed users number: {my_followed_number}', mode='info')

            if my_followed_number + MAX_FOLLOWED_PER_HOUR >= FOLLOWED_LIMIT:
                self.__log(message=f'too many followed users : {my_followed_number}', mode='error')
                self.__log(message=f'process\'ll start again in : 60.0m', mode='info')
                self.delay(3600)
            else:
                self.__log('searching : run', mode='else')
                users_to_follow = self.__get_users_to_follow_list()
                self.__log('searching : done', mode='else')

                start = time.time()
                self.__log('following : run', mode='else')
                self.__following_loop(users_to_follow)
                self.__log('following : done', mode='else')
                stop = time.time()

                wait = 3600-(stop-start)
                extra_wait = random.randint(0, 20)
                self.__log('hourly limit used', mode='else')
                self.__log(f'need to wait : {round(wait/60, 1) if wait > 0 else 30+extra_wait, "m"}', mode='else')

                self.delay(wait) if wait > 0 else self.delay(1800 + extra_wait*60)
                hours += 1

main()