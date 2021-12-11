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

import save_files
import s1_updater


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


def search_by_name(actresses):

    ChromeOptions = Options()

    ChromeOptions.add_argument('--headless')

    prefs = {"profile.managed_default_content_settings.images": 2}
    ChromeOptions.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(chrome_options = ChromeOptions)

    time.sleep(5)

    driver.get("https://s1s1s1.com/top")

    time.sleep(5)

    actresses_url = []

    for actress in actresses:

        driver.find_element_by_name("keyword").send_keys(actress, Keys.ENTER)

        actresses_url.append(driver.current_url)

        time.sleep(5)

    cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]
    cookiestr = ";".join(item for item in cookie)

    return actresses_url, cookiestr


def get_post(girl_url, next_page, cookie):

    post_links = []

    image_links = []

    if next_page == 'none':

        page_html = get_html(girl_url, cookie)

        page_soup = BeautifulSoup(page_html, 'html.parser')

        cards = page_soup.find_all("div", {'class':"c-card"})

        for card in cards:

            post_links.append(card.find("a", {'class':"img hover"})["href"])

            image = card.find("img")["data-src"]

            image_links.append(image)
            
            time.sleep(5)

    while not next_page == 'none':

        page_html = get_html(girl_url, cookie)

        page_soup = BeautifulSoup(page_html, 'html.parser')

        cards = page_soup.find_all("div", {'class':"c-card"})

        for card in cards:

            post_links.append(card.find("a", {'class':"img hover"})["href"])

            image = card.find("img")["data-src"]

            image_links.append(image)
            
            time.sleep(5)

        try:
            next_page = page_soup.find("a", {"rel": "next"})["href"]

        except:
            next_page = 'none'

        girl_url = next_page

        time.sleep(5)

    return post_links, image_links


def get_video(girl_cards, video_img, name, cookie):

    video_issue = []

    for card, img in zip(girl_cards, video_img):

        page_html = get_html(card, cookie)

        page_soup = BeautifulSoup(page_html, 'html.parser')

        datas = page_soup.find_all("div", {"class": "td"})

        day = datas[1].find("a", {"class": "c-tag c-main-bg-hover c-main-font c-main-bd"})["href"];

        issue_day = day.split('/')[-1].strip()

        issue_number = card.split('/')[-1].strip()

        issue_title = page_soup.find("h2", {"class": "p-workPage__title"}).getText().strip()

        video_issue.append({'day': issue_day, 'number': issue_number, 'name': name, 'title': issue_title, 'image': img})

        time.sleep(5)
    
    return video_issue


def Download_video(video_issue, cookie):

    for data in video_issue:
        
        dirpath = r'.\Girls_video.\{0}'.format(data['name'])
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        image = get_content(data['image'], cookie)

        file_type = data['image'].split('.')[-1]

        file_name = data['day'] + " " + data['number'] + " " + data['name'] + " " + data['title']

        file_path = r'.\girls_video.\{0}\{1}.{2}'.format(data['name'], file_name, file_type)

        try:
            download_obj(image, file_path)

            print('{0} download success'.format(file_name))

        except:
            print('{0} download fail'.format(file_name))
       
        
def get_data(girls_url, girl_name, cookie):

    iter = 0

    for girl_url in girls_url:

        html = get_html(girl_url, cookie)

        soup = BeautifulSoup(html, "html.parser")

        try :
            next_page = soup.find("a", {"rel": "next"})["href"]
        except:
            next_page = 'none'
    
        print('get next page success')

        posts, images = get_post(girl_url, next_page, cookie)

        print('get post success')

        video_issue = get_video(posts, images, girl_name[iter], cookie)

        print('get issue data success')
    
        Download_video(video_issue, cookie)

        print('Download all post image & video success')

        iter = iter + 1

        save_files.sql_saved(video_issue)

        print('MySQL saved success')

        #save_files.json_saved_without_sql(video_issue, images)


def main():

    start = time.time()

    try:

        if os.path.isfile(".\last_update_day"):

            with open('last_update_day.txt', 'r') as file:
        
                last_update = file.readline().rstrip('\n')
        
        s1_updater.main(last_update)

    except:

        actresses = []

        with open('s1_GirlsList.txt', 'r', encoding='utf8') as names:

            for name in names:

                actresses.append(name.rstrip('\n'))

        url, cookie = search_by_name(actresses)

        get_data(url, actresses, cookie)

    today = str(datetime.now()).split(" ")[0]

    with open('.\last_update_day.txt', 'w') as file:
        file.write(today)
        file.close()

    print(' Success !!!! ╮(╯  _ ╰ )╭')

    end = time.time()

    total_time = end - start

    hour = total_time // 3600

    min = (total_time - 3600 * hour) // 60

    sec = total_time - 3600 * hour - 60 * min

    print(f'Totel spend time:{int(hour)}h {int(min)}m {int(sec)}s')


