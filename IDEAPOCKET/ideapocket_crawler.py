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

avc_manager = AvManager()
avc_manager.company = 'ideapocket'


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


def search_girls():

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

        root = etree.HTML(info.get_attribute('innerHTML'))

        name_list = root.xpath("//p[@class='name']")

        headshot_list = root.xpath("//div[@class='c-card main']/a/img/@data-src")

        url_list = root.xpath("//a[@class='img']/@href")

        actresses.append({'name': name_list[0].text, 'headshot': headshot_list[0], 'url': url_list[0]})

    cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]

    cookiestr = ";".join(item for item in cookie)

    driver.quit()

    return actresses, cookiestr


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
            
        time.sleep(2)

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

    
def main(sql_password):

    start = time.time()

    actresses, cookie = search_girls()

    avc_manager.cookie = cookie
    avc_manager.sql_password = sql_password

    savefiles.save_actresslist(actresses, sql_password, avc_manager.company)
    
    for actress in actresses:
        
        last_update_day = savefiles.check_day(actress['name'], avc_manager.company, sql_password)

        if last_update_day:
            ideapocket_updater.main(last_update_day['day'], actress, actress['url'], sql_password, cookie)

        else:
            get_data(actress, actress['url'])

        print('{0} video items save complete.'.format(actress['name']))
    
    print(' Success !!!! ╮(╯  _ ╰ )╭')
    
    end = time.time()

    total_time = end - start

    hour = total_time // 3600

    min = (total_time - 3600 * hour) // 60

    sec = total_time - 3600 * hour - 60 * min

    print(f'Totel spend time:{int(hour)}h {int(min)}m {int(sec)}s')



