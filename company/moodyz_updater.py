import requests_html
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import asyncio

from avManager import avManager

manager = avManager()

session = HTMLSession()


def get_headers():
    ua = UserAgent()
    headers = {'user-agent': ua.random, 'cookie': manager.cookie}
    return headers


def get_post():

    actress = manager.actress

    posts = []

    covers = []

    next_page = actress['url']

    while not next_page == 'none':

        content = session.get(next_page, headers = get_headers())

        # get profiles
        
        if actress['en'] == None:

            actress['en'] = (content.html.xpath("//div[@class='c-title-main']/div/p"))[0].text.strip()

            actress['headshot'] = (content.html.xpath("//img[@class='u-hidden--sp lazyload']/@data-src"))[0]

            profs = (content.html.find("div[class = 'p-profile__info']"))[0].find("div[class = 'item']")
    
            for prof in profs:

                try:
                    t = prof.find("p[class = 'th']")[0].text.strip()
                except:
                    t = ""

                actress['birth'] = (prof.find("p[class = 'td']"))[0].text.strip() if t == '誕生日' else None

                actress['body'] = (prof.find("p[class = 'td']"))[0].text.strip() if t == '3サイズ' else None

        # get video post

        cards = (content.html.find("div[class = 'swiper-slide c-low--6']"))[0].find("a[class = 'item']")

        for card in cards:

            posts.append(card.attrs["href"])

            covers.append((card.find("img"))[0].attrs["data-src"])

        try:
            next_page = (content.html.find("a[rel = 'next']"))[0].attrs["href"]

        except:
            next_page = 'none'

        time.sleep(2)

    return posts, covers


def get_video(posts, covers):

    actress = manager.actress

    videos = []

    for post, cover in zip(posts, covers):

        content = session.get(post, headers = get_headers())

        datas = content.html.find("div[class = 'td']")

        day = (datas[1].find("a[class = 'c-tag c-main-bg-hover c-main-font c-main-bd']"))[0].attrs["href"]
        
        issue_day = (day.split('/'))[-1].strip()

        if issue_day <= manager.lastUpdateDay:
            break
        
        issue_number = (post.split('/'))[-1].split('?')[0]

        issue_title = (content.html.find("h2[class = 'p-workPage__title']"))[0].text.strip()

        videos.append({'day': issue_day, 'number': issue_number, 'name': actress['jp'], 'title': issue_title, 'cover': cover, 'company': manager.company})

    return videos

def get_data():

    posts, covers = get_post()
    
    videos = get_videos(posts, covers)

    manager.save_data(videos)


def main(actress, cookie, company, sql_password, last_video_issue_day):

    manager.actress = actress
    manager.cookie = cookie
    manager.company = company
    manager.sql_password = sql_password
    manager.lastUpdateDay = last_video_issue_day

    get_data()

