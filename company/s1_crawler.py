import requests
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from lxml import etree

import avSave
from s1 import s1_updater
from avManager import avManager

manager = avManager()
manager.company = 's1'


def get_html(url):
    response = requests.get(url, headers = get_headers(), allow_redirects=True)
    return response.text # text return Unicode data -> get text


def get_headers():
    ua = UserAgent()
    headers = {'user-agent': ua.random, 'cookie': manager.cookie}
    return headers


def get_girls():

    ChromeOptions = Options()

    ChromeOptions.add_argument('--headless')

    prefs = {"profile.managed_default_content_settings.images": 2}
    ChromeOptions.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(chrome_options = ChromeOptions)

    time.sleep(5)

    driver.get("https://s1s1s1.com/actress")

    time.sleep(5)

    infos = driver.find_elements_by_xpath("//div[@class='p-hoverCard']")

    actresses = []

    for info in infos:

        actress = {'headshot': None, 'jp': None, 'en': None, 'ch': None, 'birth': None, 'company': None, 'body': None}

        root = etree.HTML(info.get_attribute('innerHTML'))

        jpname_list = root.xpath("//p[@class='name']")
        actress['jp'] = jpname_list[0].text

        enname_list = root.xpath("//p[@class='en c-main-font']")
        actress['en'] = enname_list[0].text

        url_list = root.xpath("//a[@class='img']")
        actress['url'] = url_list[0].get('href')

        headshot_list = root.xpath("//a[@class='img']/img")
        actress['headshot'] = headshot_list[0].get('data-src')

        actress['company'] = manager.company

        actresses.append(actress)

    cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]

    cookiestr = ";".join(item for item in cookie)

    driver.quit()

    return actresses, cookiestr


def get_post(actress, url):

    posts = []

    images = []

    page_html = get_html(url)

    page_soup = BeautifulSoup(page_html, 'html.parser')

    profs = page_soup.find("div", {'class':"p-profile__info"}).find_all("div", {'class':"item"})
    
    for prof in profs:
        try:
            t = prof.find("p", {'class':"th"}).getText().strip()
        except:
            t = ""
        
        if t == '誕生日':
            actress['birth'] = prof.find("p", {'class':"td"}).getText().strip()
        if t == '3サイズ':
            actress['body'] = prof.find("p", {'class':"td"}).getText().strip()
    
    cards = page_soup.find("div", {'class':"swiper-slide c-low--6"}).find_all("a", {'class':"item"})

    for card in cards:

        posts.append(card["href"])

        image = card.find("img")["data-src"]

        images.append(image)
    try:
        next_page = page_soup.find("a", {"rel": "next"})["href"]
    except:
        next_page = None

    while not next_page == 'none':

        page_html = get_html(next_page)

        page_soup = BeautifulSoup(page_html, 'html.parser')

        cards = page_soup.find("div", {'class':"swiper-slide c-low--6"}).find_all("a", {'class':"item"})

        for card in cards:

            posts.append(card["href"])

            image = card.find("img")["data-src"]

            images.append(image)

        try:
            next_page = page_soup.find("a", {"rel": "next"})["href"]

        except:
            break

        time.sleep(2)

    time.sleep(5)
    return posts, images


def get_video(cards, images, name):

    videos = []

    for card, image in zip(cards, images):

        page_html = get_html(card)

        page_soup = BeautifulSoup(page_html, 'html.parser')

        datas = page_soup.find_all("div", {"class": "td"})

        day = datas[1].find("a", {"class": "c-tag c-main-bg-hover c-main-font c-main-bd"})["href"];

        issue_day = day.split('/')[-1].strip()

        issue_number = card.split('/')[-1].split('?')[0]

        issue_title = page_soup.find("h2", {"class": "p-workPage__title"}).getText().strip()

        videos.append({'day': issue_day, 'number': issue_number, 'name': name, 'title': issue_title, 'cover': image, 'company': manager.company})

        time.sleep(3)
    
    return videos

        
def get_data(actress):

    posts, images = get_post(actress, actress['url'])

    videos = get_video(posts, images, actress['jp'])

    avSave.save_data(videos, manager.company, manager.sql_password)


def main(sql_password):

    start = time.time()
    
    actresses, cookie = get_girls()

    manager.cookie = cookie
    manager.sql_password = sql_password

    for actress in actresses:
        '''
        last_update_day = savefiles.check_day(actress['name'], manager.company, sql_password)

        if last_update_day:
            s1_updater.main(last_update_day['day'], actress, sql_password, cookie)

        else:
            get_data(actress)
        '''
        get_data(actress)
        print('{0} video items save complete.'.format(actress['name']))
    
    avSave.save_actresslist(actresses, sql_password)
    
    end = time.time()

    total_time = end - start

    hour = total_time // 3600

    min = (total_time - 3600 * hour) // 60

    sec = total_time - 3600 * hour - 60 * min

    print(f'Totel spend time:{int(hour)}h {int(min)}m {int(sec)}s')


