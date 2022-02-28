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

import avSave
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


def get_post(actress, url):

    posts = []

    images = []

    page_html = get_html(url)

    page_soup = BeautifulSoup(page_html, 'html.parser')
    
    cards = page_soup.find("div", {'class':"swiper-slide c-low--6"}).find_all("a", {'class':"item"})

    for card in cards:

        posts.append(card["href"])

        image = card.find("img")["data-src"]

        images.append(image)

    next_page = page_soup.find("a", {"rel": "next"})["href"]

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

        time.sleep(3)

    time.sleep(3)

    return posts, images


def get_video(cards, images, name):

    videos = []

    for card, image in zip(cards, images):

        page_html = get_html(card)

        page_soup = BeautifulSoup(page_html, 'html.parser')

        datas = page_soup.find_all("div", {"class": "td"})

        day = datas[1].find("a", {"class": "c-tag c-main-bg-hover c-main-font c-main-bd"})["href"];

        issue_day = day.split('/')[-1].strip()

        if issue_day < manager.update:
            break

        issue_number = card.split('/')[-1].split('?')[0]

        issue_title = page_soup.find("h2", {"class": "p-workPage__title"}).getText().strip()

        videos.append({'day': issue_day, 'number': issue_number, 'name': name, 'title': issue_title, 'cover': image, 'company': manager.company})

        time.sleep(3)
    
    return videos
       
        
def get_data(actress):

    posts, images = get_post(actress, actress['url'])

    videos = get_video(posts, images, actress['jp'])
    
    avSave.save_data(videos, manager.company, manager.sql_password)


def main(last_update_day, actress, sql_password, cookie):
    
    manager.cookie = cookie
    manager.sql_password = sql_password
    manager.update = last_update_day
   
    get_data(actress)