import requests
import os
import time
import json
import random
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from lxml import etree
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import savefiles


def get_post(last_update_day, actress, url):

    ChromeOptions = Options()

    ChromeOptions.add_argument('--headless')
    ChromeOptions.add_argument('--disable-gpu')

    prefs = {"profile.managed_default_content_settings.images": 2}
    ChromeOptions.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(chrome_options = ChromeOptions)

    time.sleep(5)

    driver.get('https://faleno.jp/top/')

    time.sleep(5)

    driver.find_element_by_link_text('は　い').click()

    time.sleep(5)

    posts = []

    driver.get(url)

    time.sleep(10)

    infos = driver.find_elements_by_xpath("//div[@class='waku_kanren01']")

    for info in infos:

        root = etree.HTML(info.get_attribute('innerHTML'))
        
        img_list = root.cssselect('a > img')
        image = img_list[0].get('src') 

        number_list = root.xpath("//div[@class='text_name']/a")
        number = number_list[0].get('href').split("/")[-2]

        title = img_list[0].get('alt')

        day_list = root.xpath("//div[@class='btn08']")
        day = day_list[0].text.split(" ")[0].replace("/", "-")

        if(day <= last_update_day):
            break

        posts.append({'day': day, 'number': number, 'name': actress, 'title': title, 'image': image})

    cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]

    cookiestr = ";".join(item for item in cookie)

    driver.quit()

    return posts, cookiestr


def main(last_update_day, name, url):

    posts, cookie = get_post(last_update_day, name, url)

    print("get videos data success")

    print(posts)

    if posts:

        for post in posts:

            post['company'] = 'faleno'

    try:
        savefiles.sql_saved(posts, 'faleno')
    except:
        print('Do not have new video')

    print('SQL saved success')