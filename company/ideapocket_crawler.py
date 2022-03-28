import requests_html
from requests_html import HTMLSession
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from lxml import etree

import avSave
from ideapocket import ideapocket_updater
from avManager import avManager

manager = avManager()
manager.company = 'ideapocket'


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

    driver.get('https://ideapocket.com/actress')
    
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

        headshot_list = root.xpath("//div[@class='c-card main']/a/img/@data-src")
        actress['headshot'] = headshot_list[0]

        url_list = root.xpath("//a[@class='img']/@href")
        actress['url'] = url_list[0]

        actress['company'] = manager.company

        actresses.append(actress)
    
    cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]

    cookiestr = ";".join(item for item in cookie)

    driver.quit()

    return actresses, cookiestr


def get_post(actress, url):

    session = HTMLSession()

    posts = []

    covers = []

    content = session.get(url, headers = get_headers())

    profs = content.html.find("div[class = 'p-profile__info']")[0].find("div[class = 'item']")
    
    for prof in profs:
        try:
            t = prof.find("p[class = 'th']")[0].text.strip()
        except:
            t = ""
        
        if t == '誕生日':
            actress['birth'] = prof.find("p[class = 'td']")[0].text.strip()
        if t == '3サイズ':
            actress['body'] = prof.find("p[class = 'td']")[0].text.strip()
    
    cards = content.html.find("div[class = 'swiper-slide c-low--6']")[0].find("a[class = 'item']")
        
    for card in cards:

        post = card.attrs["href"]

        posts.append(post)

        cover = card.find("img")[0].attrs["data-src"]

        covers.append(cover)
            
    time.sleep(2)

    try:
        next_page = content.html.find("a[rel = 'next']")[0].attrs["href"]
    except:
        next_page = None

    while not next_page == 'none':

        content = session.get(url, headers = get_headers())

        cards = content.html.find("div[class = 'swiper-slide c-low--6']")[0].find("a[class = 'item']")

        for card in cards:

            post = card.attrs["href"]

            posts.append(post)

            cover = card.find("img")[0].attrs["data-src"]

            covers.append(cover)

        try:
            next_page = content.html.find("a[rel = 'next']")[0].attrs["href"]

        except:
            next_page = 'none'

        url = next_page

        time.sleep(2)
    
    time.sleep(3)
    return posts, covers
       
        
def get_data(actress):

    posts, covers = get_post(actress, actress['url'])

    videos = get_video(posts, covers, actress['jp'])

    savefiles.save_data(videos, manager.company, manager.sql_password)

    
def main(sql_password):

    start = time.time()

    actresses, cookie = get_girls()

    manager.cookie = cookie
    manager.sql_password = sql_password

    for actress in actresses:
        
        last_update_day = savefiles.check_day(actress['jp'], manager.company, sql_password)

        if last_update_day:
            ideapocket_updater.main(last_update_day['day'], actress, sql_password, cookie)

        else:
            get_data(actress)
        
        print('{0} video items save complete.'.format(actress['jp']))
    
    savefiles.save_actresslist(actresses, sql_password)
    
    print(' Success !!!! ╮(╯  _ ╰ )╭')
    
    end = time.time()

    total_time = end - start

    hour = total_time // 3600

    min = (total_time - 3600 * hour) // 60

    sec = total_time - 3600 * hour - 60 * min

    print(f'Totel spend time:{int(hour)}h {int(min)}m {int(sec)}s')



