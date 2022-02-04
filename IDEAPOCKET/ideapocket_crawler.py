import requests_html
from requests_html import HTMLSession
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from lxml import etree

import savefiles
from IDEAPOCKET import ideapocket_updater
from av_manager import AvManager

manager = AvManager()
manager.company = 'ideapocket'


def get_content(url):
    response = requests.get(url, headers = get_headers(), timeout = 10)
    return response.content # content return bytes(binary) data -> get image, video, file and etc


def download_obj(data, path):
    with open(path, "wb") as file:
        file.write(data)
        file.close()


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


def get_video(posts, covers, name):

    session = HTMLSession()

    videos = []

    for post, cover in zip(posts, covers):

        content = session.get(post, headers = get_headers())

        datas = content.html.find("div[class = 'td']")

        day = datas[1].find("a[class = 'c-tag c-main-bg-hover c-main-font c-main-bd']")[0].attrs["href"]
        
        issue_day = day.split('/')[-1].strip()
        
        issue_number = post.split('/')[-1].split('?')[0]

        issue_title = content.html.find("h2[class = 'p-workPage__title']")[0].text.strip()

        videos.append({'day': issue_day, 'number': issue_number, 'name': name, 'title': issue_title, 'cover': cover, 'company': avc_manager.company})

        time.sleep(3)
    
    return videos


'''
The following download function is choose on you.
Recommend to use MySQL download which is more quickly.
'''
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



