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

import save_files


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


def search_by_day(last_update_day):

    ChromeOptions = Options()

    ChromeOptions.add_argument('--headless')

    prefs = {"profile.managed_default_content_settings.images": 2}
    ChromeOptions.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(chrome_options = ChromeOptions)

    time.sleep(3)

    driver.get("https://s1s1s1.com/works/date")

    time.sleep(3)

    urls = []

    items = driver.find_elements_by_xpath("//a[@class='item c-main-font-hover']")

    for item in items:
        
        issue_day = item.get_attribute('href')
        
        trim = issue_day.split('/')[-1]

        if trim > last_update_day:

            urls.append(issue_day)

        else:

            break

        time.sleep(3)

    cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]
    cookiestr = ";".join(item for item in cookie)

    driver.quit()
    
    return urls, cookiestr


def get_post(IssueDay_url, next_page, cookie):

    girls_card = []

    if next_page == 'none':

        page_html = get_html(IssueDay_url, cookie)

        page_soup = BeautifulSoup(page_html, 'html.parser')

        cards = page_soup.find_all("div", {'class':"c-card"})

        for card in cards:

            day = IssueDay_url.split('/')[-1]
            
            number = card.find("a", {'class':"img hover"})["href"].split('/')[-1]
            
            try:
                name = card.find("a", {'class': 'name c-main-font-hover'}).getText()
            except:
                name = 'multiple'
            
            title = card.find("p", {'class': 'text'}).getText()
            
            image = card.find("img")["data-src"]

            girls_card.append({'day': day, 'number': number, 'name': name, 'title': title, 'image': image})

    while not next_page == 'none':

        page_html = get_html(IssueDay_url, cookie)

        page_soup = BeautifulSoup(page_html, 'html.parser')

        cards = page_soup.find_all("div", {'class':"c-card"})

        for card in cards:

            day = IssueDay_url.split("/")[-1]

            number = card.find("a", {'class':"img hover"})["href"].split('/')[-1]

            try:
                name = card.find("a", {'class': 'name c-main-font-hover'}).getText()
            except:
                name = 'multiple'

            title = card.find("p", {'class': 'text'}).getText().strip()

            image = card.find("img")["data-src"]

            girls_card.append({'day': day, 'number': number, 'name': name, 'title': title, 'image': image})

            time.sleep(5)

            print(day, number, name, title, image)

        try:
            next_page = page_soup.find("a", {"rel": "next"})["href"]

        except:
            next_page = 'none'

        girl_url = next_page

    return girls_card


def Download_post(videos_intro, cookie):

    for video in videos_intro:

        dirpath = r'.\girls_video.\{0}'.format(video['name'])
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
       
        
def update_data(posts_url, cookie):

    for post in posts_url:

        html = get_html(post, cookie)

        soup = BeautifulSoup(html, "html.parser")

        try :
            next_page = soup.find("a", {"rel": "next"})["href"]
        except:
            next_page = 'none'
    
        print('get next page success')

        videos_intro = get_post(post, next_page, cookie)

        print('get video intro success')
    
        Download_post(videos_intro, cookie)

        print('Download all post image & video success')

        save_files.sql_saved(videos_intro)

        print('MySQL saved success')

        #save_files.json_saved_without_sql(video_issue, images)


def main(last_update_day):

    urls, cookie = search_by_day(last_update_day)
    
    update_data(urls, cookie)