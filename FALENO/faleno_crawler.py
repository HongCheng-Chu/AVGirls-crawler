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
from datetime import datetime

import savefiles
from FALENO import faleno_updater


def get_content(url, cookie):
    response = requests.get(url, headers = get_headers(cookie), timeout = 10)
    return response.content # content return bytes(binary) data -> get image, video, file and etc


def download_obj(data, path):
    with open(path, "wb") as file:
        file.write(data)
        file.close()


def get_headers(cookie):
    ua = UserAgent()
    headers = {'user-agent': ua.random, 'cookie': cookie}
    return headers


def search_girls():

    ChromeOptions = Options()

    ChromeOptions.add_argument('--headless')
    ChromeOptions.add_argument('--disable-gpu')

    prefs = {"profile.managed_default_content_settings.images": 2}
    ChromeOptions.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(chrome_options = ChromeOptions)

    time.sleep(5)

    driver.get("https://faleno.jp/top/actress/")

    time.sleep(5)

    driver.find_element_by_link_text('は　い').click()

    time.sleep(5)

    infos = driver.find_elements_by_xpath("//li[@data-mh='group01']")
    
    actresses = []

    profs = []

    for info in infos:

        # driver.find_element_by_xpath only read the first one element

        root = etree.HTML(info.get_attribute('innerHTML'))

        names = root.xpath("//div[@class='text_name']")
        for name in names:
            actresses.append(name.text)

        urls = root.xpath("//div[@class='img_actress01']/a/@href")
        for url in urls:
            profs.append(url)

    driver.quit()

    return actresses, profs


def get_post(actress, url):

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

        posts.append({'day': day, 'number': number, 'name': actress, 'title': title, 'image': image, 'company': 'faleno'})

    cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]

    cookiestr = ";".join(item for item in cookie)

    driver.quit()

    return posts, cookiestr


def download_video(videos, cookie):

    for video in videos:
        
        dirpath = r'.\Girls_video.\Faleno.\{0}'.format(video['name'])
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        image = get_content(video['image'], cookie)

        file_name = video['day'] + " " + video['number'] + " " + video['name'] + " " + video['title']

        file_path = r'.\Girls_video.\Faleno.\{0}\{1}.{2}'.format(video['name'], file_name, 'jpg')

        download_obj(image, file_path)

        try:
            download_obj(image, file_path)

            print('{0} download success'.format(file_name))

        except:
            print('{0} download fail'.format(file_name))


def get_data(actress, url):

    posts, cookie = get_post(actress, url)

    print('get post & cookie success')

    download_video(posts, cookie)
   
    print('download success')

    for post in posts:

        post['company'] = 'faleno'

    savefiles.sql_saved(posts, 'faleno')

    print('sql success')


def main():

    start = time.time()

    actresses, urls = search_girls()

    for actress, url in zip(actresses, urls):
        
        last_update = savefiles.check_day(actress, 'faleno')

        if last_update:
            faleno_updater.main(last_update['day'], actress, url)

        else:
            get_data(actress, url)
    
    print(' Success !!!! ╮(╯  _ ╰ )╭')

    end = time.time()

    total_time = end - start

    hour = total_time // 3600

    min = (total_time - 3600 * hour) // 60

    sec = total_time - 3600 * hour - 60 * min

    print(f'Totel spend time:{int(hour)}h {int(min)}m {int(sec)}s')
    
