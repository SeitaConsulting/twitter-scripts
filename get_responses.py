from twitterlib import TwitterLib
from bs4 import BeautifulSoup
from requests_oauthlib import OAuth1Session
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import config
import csv
import datetime
import json
import re
import time
import urllib.request

import chromedriver_binary

def get_responses(tweet_id, mode, driver):
    url = 'https://twitter.com/sawakiseita/status/' + str(tweet_id) + '/' + mode
    print('Tweet:')
    print(url)
    driver.get(url)

    time.sleep(5)
    print('Log: page opened.')

    #print('Source:')
    #print(driver.page_source)
    time.sleep(2)
    
    driver.execute_script("var element = document.getElementsByClassName('css-1dbjc4n r-16y2uox r-1wbh5a2 r-1dqxon3')[0];var a = setInterval(function() {element.scrollBy(0, 250); console.log(element.innerHTML);}, 100);")

    time.sleep(20)
    print('Log: data gotten.')

    source = ''
    for entry in driver.get_log('browser'):
        source = source + entry['message']
    source = source.encode().decode('unicode-escape')
    
    pattern = '<span class.*?>@(.*?)</span>'    
    user_ids = re.findall(pattern, source, re.S)
    user_ids = list(set([i for i in user_ids if not '</a>' in i]))

    print('Log: finish for this tweet.')
    print(len(user_ids))
    print(user_ids)
    return user_ids

def login(un, pw, driver):
    url = "https://twitter.com/login"
    driver.get(url)
            
    time.sleep(5)
    print('Log: page opened.')  
    #print(self.driver.page_source)
            
    username = driver.find_element_by_name('session[username_or_email]')
    password = driver.find_element_by_name('session[password]')
    username.send_keys(un)
    time.sleep(2)
    password.send_keys(pw)
    time.sleep(2)
    print('Log: username and password typed.')
    
    password.send_keys(Keys.ENTER)
    time.sleep(5)
    print('Log: logged in.')

if __name__ == '__main__':
    print('Started at', datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

    # init
    #twitterlib
    t = TwitterLib(config)
    #selenium
#    d = DesiredCapabilities.CHROME
#    d['goog:loggingPrefs'] = { 'browser':'ALL' }
    options = Options()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--headless')
    options.add_argument('--window-size=1280,1024')
    options.add_argument("--enable-javascript")
    options.add_argument("user-data-dir=" + config.wd + '/cache')
    driver = webdriver.Chrome(
        chrome_options=options,
        executable_path='/bin/chromedriver',
#        desired_capabilities=d
    )
    login('DoitAllRightNow', 'Vistyle1234!', driver)
    exit()
    
    # get tweet_ids from twilog with deltadays
    now = datetime.datetime.now()
    url = 'https://twilog.org/sawakiseita/date-{0:%y%m%d}'.format(now-datetime.timedelta(days=config.deltadays))
    print('Twilog')
    print(url)
    html = urllib.request.urlopen(url).read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.find_all('article')
    tweet_ids = []
    for element in elements:
        tweet_ids.append(element['id'][2:])
    print('Tweets')
    print(len(tweet_ids))
    print(tweet_ids)
        
    # screen_names
    screen_names = []
    for mode in ['likes', 'retweets']:
        for tweet_id in tweet_ids:
            screen_names += get_responses(tweet_id, mode, driver)
            #break # for only one tweet
    screen_names = list(set(screen_names))
    print('Screen Names:')
    print(len(screen_names))
    print(screen_names)
    
    # convert to user_ids
    user_ids = t.screen_names_to_user_ids(screen_names)
    print('User IDs:')
    print(len(user_ids))
    print(user_ids)
    
    # add to responses.csv
    now = datetime.datetime.now()
    date = '{0:%y%m%d}'.format(now-datetime.timedelta(days=config.deltadays))
    t.set_to_responses(date, user_ids)
    
    # del
    driver.quit()
    
    print('Ended at', datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
