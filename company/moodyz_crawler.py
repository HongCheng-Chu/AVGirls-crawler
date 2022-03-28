import requests_html
from requests_html import HTMLSession
from requests_html import AsyncHTMLSession
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import asyncio

#from company import mooodyz_updater
from avManager import avManager

manager = avManager()
session = HTMLSession()


def get_headers():
    ua = UserAgent()
    headers = {'user-agent': ua.random, 'cookie': manager.cookie}
    return headers


def get_girls():

    ChromeOptions = Options()

    ChromeOptions.add_argument('--headless')
    ChromeOptions.add_argument('--disable-gpu')

    prefs = {"profile.managed_default_content_settings.images": 2}
    ChromeOptions.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(chrome_options = ChromeOptions)

    time.sleep(5)

    page = 'https://moodyz.com/works/list/reserve'

    driver.get(page)
    
    time.sleep(5)

    actresses = []
    
    while page:

        infos = driver.find_elements_by_xpath("//a[@class='name c-main-font-hover']")
        
        for info in infos:

            actress = {'headshot': None, 'jp': None, 'en': None, 'ch': None, 'birth': None, 'company': None, 'body': None, 'url': None}

            url = info.get_attribute('href')
            jpname = info.text

            isExist = next((item for item in actresses if  item['url'] == url), None)

            if isExist == None:
                actress['url'] = url
                actress['jp'] = jpname
                actress['company'] = manager.company
                actresses.append(actress)
        
        try:
            page = driver.find_element_by_xpath("//a[@rel='next']").get_attribute('href')
            driver.get(page)
            time.sleep(5)

        except:
            break
    
    cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]

    cookiestr = ";".join(item for item in cookie)
    
    driver.quit()

    return actresses, cookiestr


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


async def get_video(post, cover):

    actress = manager.actress

    content = session.get(post, headers = get_headers())

    await asyncio.sleep(5)

    video_data = content.html.find("div[class = 'td']")

    day = (video_data[1].find("a[class = 'c-tag c-main-bg-hover c-main-font c-main-bd']"))[0].attrs["href"]
        
    issue_day = (day.split('/'))[-1].strip()
        
    issue_number = (post.split('/'))[-1].split('?')[0]

    issue_title = (content.html.find("h2[class = 'p-workPage__title']"))[0].text.strip()

    video = {'day': issue_day, 'number': issue_number, 'name': actress['jp'], 'title': issue_title, 'cover': cover, 'company': manager.company}

    return video
       
        
async def get_data():

    posts, covers = get_post()
    
    # async start

    #loop = asyncio.get_event_loop()

    tasks = []
    
    for post, cover in zip(posts, covers):

        #task = loop.create_task(get_video(post, cover))
        task = asyncio.create_task(get_video(post, cover))

        tasks.append(task)

    #done, _ = loop.run_until_complete(asyncio.wait(tasks))
    videos = await asyncio.gather(*tasks)
    print(videos)
    #videos = [t for t in done]

    #loop.run_until_complete(loop.shutdown_asyncgens())

    manager.save_video(videos)

    
def main(sql_password):

    start = time.time()

    manager.company = 'moodyz'
    manager.sql_password = sql_password

    actresses, cookie = get_girls()
    
    manager.cookie = cookie
    
    for actress in actresses:

        manager.actress = actress
        '''
        last_video_issue_day = manager.get_day(actress['jp'])

        if last_video_issue_day:
            
            moodyz_updater(actress, cookie, company, sql_password, last_video_issue_day)

        else:

            get_data()
        '''

        asyncio.run(get_data())
        
        print('{0} video items save complete.'.format(actress['jp']))
    
    manager.save_actress(actresses)
    
    print(' Success !!!! ╮ (╯  _ ╰ )╭')
    
    end = time.time()

    total_time = end - start
    hour = total_time // 3600
    min = (total_time - 3600 * hour) // 60
    sec = total_time - 3600 * hour - 60 * min
    print(f'Totel spend time:{int(hour)}h {int(min)}m {int(sec)}s')