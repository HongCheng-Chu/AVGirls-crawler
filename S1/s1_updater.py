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
from datetime import datetime

import savefiles


def get_html(url, cookie):
    response = requests.get(url, headers = get_headers(cookie), allow_redirects=True)
    return response.text # text return Unicode data -> get text


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


def get_cookie(url):

    ChromeOptions = Options()

    ChromeOptions.add_argument('--headless')

    prefs = {"profile.managed_default_content_settings.images": 2}
    ChromeOptions.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(chrome_options = ChromeOptions)

    time.sleep(5)

    driver.get(url)

    time.sleep(5)

    cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]

    cookiestr = ";".join(item for item in cookie)

    driver.quit()

    return cookiestr


def get_post(url, next_page, cookie):

    post_links = []

    image_links = []

    if next_page == 'none':

        page_html = get_html(url, cookie)

        page_soup = BeautifulSoup(page_html, 'html.parser')

        cards = page_soup.find("div", {'class':"swiper-slide c-low--6"}).find_all("a", {'class':"item"})

        for card in cards:

            post_links.append(card["href"])

            image = card.find("img")["data-src"]

            image_links.append(image)
            
        time.sleep(2)

    while not next_page == 'none':

        page_html = get_html(url, cookie)

        page_soup = BeautifulSoup(page_html, 'html.parser')

        cards = page_soup.find("div", {'class':"swiper-slide c-low--6"}).find_all("a", {'class':"item"})

        for card in cards:

            post_links.append(card["href"])

            image = card.find("img")["data-src"]

            image_links.append(image)

        try:
            next_page = page_soup.find("a", {"rel": "next"})["href"]

        except:
            next_page = 'none'

        url = next_page

        time.sleep(2)

    return post_links, image_links


def get_video(cards, images, actress, cookie, last_update_day):

    videos = []

    for card, image in zip(cards, images):

        page_html = get_html(card, cookie)

        page_soup = BeautifulSoup(page_html, 'html.parser')

        datas = page_soup.find_all("div", {"class": "td"})

        day = datas[1].find("a", {"class": "c-tag c-main-bg-hover c-main-font c-main-bd"})["href"];

        issue_day = day.split('/')[-1].strip()

        if issue_day < last_update_day:
            break

        issue_number = card.split('/')[-1].split('?')[0]

        issue_title = page_soup.find("h2", {"class": "p-workPage__title"}).getText().strip()

        videos.append({'day': issue_day, 'number': issue_number, 'name': actress, 'title': issue_title, 'video': image, 'company': 's1'})

        time.sleep(3)
    
    return videos


def Download_video(videos, cookie):

    for video in videos:
        
        dirpath = r'.\Girls_video.\{0}'.format(data['name'])
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        image = get_content(video['image'], cookie)

        file_type = video['image'].split('.')[-1]

        file_name = video['day'] + " " + video['number'] + " " + video['name'] + " " + video['title']

        file_path = r'.\girls_video.\{0}\{1}.{2}'.format(video['name'], file_name, file_type)

        try:
            download_obj(image, file_path)

            print('{0} download success'.format(file_name))

        except:
            print('{0} download fail'.format(file_name))

        time.sleep(2)
       
        
def get_data(actress, url, cookie, last_update_day):

    html = get_html(url, cookie)

    soup = BeautifulSoup(html, "html.parser")

    try :
        next_page = soup.find("a", {"rel": "next"})["href"]
    except:
        next_page = 'none'
    
    print('get next page success')

    posts, images = get_post(url, next_page, cookie)
    
    print('get post success')

    videos = get_video(posts, images, actress, cookie, last_update_day)

    print('get issue data success')

    savefiles.sql_saved(videos, 's1')

    print('MySQL saved success')
    
    '''
    Download function is choose to you.

    Download_video(videos, cookie)

    print('Download all post image & video success')
    '''
    


def main(last_update_day, actress, url):
    
    cookie = get_cookie(url)
   
    get_data(actress, url, cookie, last_update_day)