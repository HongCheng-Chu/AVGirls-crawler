import requests_html
from requests_html import HTMLSession
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
from lxml import etree

import avSave
from avManager import avManager

manager = avManager()
manager.company = 'ideapocket'


def get_headers():
    ua = UserAgent()
    headers = {'user-agent': ua.random, 'cookie': manager.cookie}
    return headers


def get_post(url, next_page):

    session = HTMLSession()

    posts = []

    covers = []

    content = session.get(url, headers = get_headers())

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

        time.sleep(3)

    return posts, covers


def get_video(posts, covers, name):

    session = HTMLSession()

    videos = []

    for post, cover in zip(posts, covers):

        content = session.get(post, headers = get_headers())

        datas = content.html.find("div[class = 'td']")

        day = datas[1].find("a[class = 'c-tag c-main-bg-hover c-main-font c-main-bd']")[0].attrs["href"]
        
        issue_day = day.split('/')[-1].strip()

        if issue_day <= manager.update:
            break
        
        issue_number = post.split('/')[-1].split('?')[0]

        issue_title = content.html.find("h2[class = 'p-workPage__title']")[0].text.strip()

        videos.append({'day': issue_day, 'number': issue_number, 'name': name, 'title': issue_title, 'cover': cover, 'company': manager.company})

        time.sleep(3)
    
    return videos
       
        
def get_data(actress):

    posts, covers = get_post(actress, actress['url'])

    videos = get_video(posts, covers, actress['jp'])

    avSave.save_data(videos, manager.company, manager.sql_password)


def main(last_update_day, actress, sql_password, cookie):
    
    manager.cookie = cookie
    manager.sql_password = sql_password
    manager.update = last_update_day
   
    get_data(actress)




