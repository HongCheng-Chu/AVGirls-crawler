import requests_html
from requests_html import HTMLSession
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
from lxml import etree

import savefiles
from av_manager import AvManager

avc_manager = AvManager()
avc_manager.company = 'IDEAPOCKET'


def get_content(url):
    response = requests.get(url, headers = get_headers(), timeout = 10)
    return response.content # content return bytes(binary) data -> get image, video, file and etc


def download_obj(data, path):
    with open(path, "wb") as file:
        file.write(data)
        file.close()


def get_headers():
    ua = UserAgent()
    headers = {'user-agent': ua.random, 'cookie': avc_manager.cookie}
    return headers


def get_post(url, next_page):

    session = HTMLSession()

    posts = []

    covers = []

    if next_page == 'none':

        content = session.get(url, headers = get_headers())

        cards = content.html.find("div[class = 'swiper-slide c-low--6']")[0].find("a[class = 'item']")
        
        for card in cards:

            post = card.attrs["href"]

            posts.append(post)

            cover = card.find("img")[0].attrs["data-src"]

            covers.append(cover)
            
        time.sleep(3)

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

        if issue_day <= avc_manager.update:
            break
        
        issue_number = post.split('/')[-1].split('?')[0]

        issue_title = content.html.find("h2[class = 'p-workPage__title']")[0].text.strip()

        videos.append({'day': issue_day, 'number': issue_number, 'name': name, 'title': issue_title, 'cover': cover, 'company': avc_manager.company})

        time.sleep(3)
    
    return videos


def Download_video(videos):

    for video in videos:
        
        dirpath = r'.\Girls_video.\{0}'.format(data['name'])
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        image = get_content(video['image'])

        file_type = video['image'].split('.')[-1]

        file_name = video['day'] + " " + video['number'] + " " + video['name'] + " " + video['title']

        file_path = r'.\girls_video.\{0}\{1}.{2}'.format(video['name'], file_name, file_type)

        try:
            download_obj(image, file_path)

            print('{0} download success'.format(file_name))

        except:
            print('{0} download fail'.format(file_name))

        time.sleep(2)
       
        
def get_data(actress, url):

    session = HTMLSession()

    content = session.get(url, headers = get_headers())

    try :
        next_page = content.html.find("a[rel = 'next']")[0].attrs["href"]

    except:
        next_page = 'none'

    posts, covers = get_post(url, next_page)

    videos = get_video(posts, covers, actress['name'])

    savefiles.save_data(videos, avc_manager.company, avc_manager.sql_password)
    
    '''
    Download function is choose to you.

    Download_video(videos, cookie)

    print('Download all post image & video success')
    '''


def main(last_update_day, actress, url, sql_password, cookie):
    
    avc_manager.cookie = cookie
    avc_manager.sql_password = sql_password
    avc_manager.update = last_update_day
   
    get_data(actress, url)




