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

import save_files


def search_girls(last_update):

    ChromeOptions = Options()

    ChromeOptions.add_argument('--headless')
    ChromeOptions.add_argument('--disable-gpu')

    prefs = {"profile.managed_default_content_settings.images": 2}
    ChromeOptions.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(chrome_options = ChromeOptions)

    time.sleep(5)

    driver.get("https://faleno.jp/top/")

    time.sleep(5)

    driver.find_element_by_link_text('は　い').click()

    time.sleep(5)
    
    posts = []

    page = "https://faleno.jp/top/work/"

    while not page == 'none':

        driver.get(page)

        time.sleep(5)

        infos = driver.find_elements_by_xpath("//div[@class='waku_kanren01']")

        out_day = ''

        for info in infos:

            root = etree.HTML(info.get_attribute('innerHTML'))

            day_list = root.xpath("//div[@class='btn08']")
            day = day_list[0].text.split(" ")[0].replace("/", "-")
            print(day)
            out_day = day

            if day < last_update:
                break
        
            img_list = root.cssselect('a > img')
            image = img_list[0].get('src') 
            #print(image)

            number_list = root.xpath("//div[@class='text_name']/a")
            number = number_list[0].get('href').split("/")[-2]
            #print(number)

            title = img_list[0].get('alt') 
            #print(title)

            actress_list = root.xpath("//div[@class='text_kanren01 clearfix']/p")
            actress = actress_list[0].text
            #print(actress)

            posts.append({'day': day, 'number': number, 'name': actress, 'title': title, 'image': image})

        if out_day < last_update:
            break
        
        try:
            page = driver.find_elements_by_xpath("//a[@class='nextpostslink'").get_attirbute('href')

        except:
            page = 'none'

        print(page)

    driver.quit()

    return posts


def main(day):

    posts = search_girls(day)

    print("videos data download success")

    save_files.sql_saved(posts)

    print('SQL saved success')