import requests_html
from requests_html import HTMLSession
from requests_html import AsyncHTMLSession
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from lxml import etree
import asyncio

import avSave
#from moodyz import mooodyz_updater
from avManager import avManager

manager = avManager()
manager.company = 'moodyz'

asession = AsyncHTMLSession()


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

    driver.get('https://moodyz.com/actress')
    
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


async def get_post(actress):

    posts = []

    covers = []

    next_page = actress['url']

    while not next_page == 'none':

        content = await asession.get(next_page, headers = get_headers())

        # get profiles

        if actress['birth'] == None and actress['body'] == None:

            profs = content.html.find("div[class = 'p-profile__info']")[0].find("div[class = 'item']")
    
            for prof in profs:
                try:
                    t = prof.find("p[class = 'th']")[0].text.strip()
                except:
                    t = ""

                actress['birth'] = prof.find("p[class = 'td']")[0].text.strip() if t == '誕生日' else None

                actress['body'] = prof.find("p[class = 'td']")[0].text.strip() if t == '3サイズ' else None

        # get video post

        cards = content.html.find("div[class = 'swiper-slide c-low--6']")[0].find("a[class = 'item']")

        for card in cards:

            post = card.attrs["href"]

            posts.append(post)

            cover = card.find("img")[0].attrs["data-src"]

            covers.append(cover)

        # get next page

        try:
            next_page = content.html.find("a[rel = 'next']")[0].attrs["href"]

        except:
            next_page = 'none'

        await asyncio.sleep(2)
    
    return posts, covers


async def get_video():

    actress = manager.actress

    posts, covers = await get_post(actress)
    
    # get video data

    videos = []
    
    for post, cover in zip(posts, covers):

        content = await asession.get(post, headers = get_headers())

        datas = content.html.find("div[class = 'td']")

        day = datas[1].find("a[class = 'c-tag c-main-bg-hover c-main-font c-main-bd']")[0].attrs["href"]
        
        issue_day = day.split('/')[-1].strip()
        
        issue_number = post.split('/')[-1].split('?')[0]

        issue_title = content.html.find("h2[class = 'p-workPage__title']")[0].text.strip()

        videos.append({'day': issue_day, 'number': issue_number, 'name': actress['jp'], 'title': issue_title, 'cover': cover, 'company': manager.company})

        await asyncio.sleep(2)
    
    return videos
       
        
async def get_data():

    videos = await get_video()

    #avSaves.save_data(videos, manager.company, manager.sql_password)

    
def main(sql_password):

    start = time.time()
    
    actresses, cookie = get_girls()

    manager.cookie = cookie
    manager.sql_password = sql_password

    for actress in actresses:
        '''
        last_update_day = avSaves.check_day(actress['jp'], manager.company, sql_password)

        if last_update_day:
            ideapocket_updater.main(last_update_day['day'], actress, sql_password, cookie)

        else:
            get_data(actress)
        '''
        manager.actress = actress

        asession.run(get_data)
        
        print('{0} video items save complete.'.format(actress['jp']))

    print(actresses)
    #avSave.save_actresslist(actresses, sql_password)
    
    print(' Success !!!! ╮ (╯  _ ╰ )╭')
    
    end = time.time()

    total_time = end - start

    hour = total_time // 3600

    min = (total_time - 3600 * hour) // 60

    sec = total_time - 3600 * hour - 60 * min

    print(f'Totel spend time:{int(hour)}h {int(min)}m {int(sec)}s')