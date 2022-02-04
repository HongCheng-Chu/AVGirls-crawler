import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from lxml import etree

import savefiles
from FALENO import faleno_updater
from av_manager import AvManager

manager = AvManager()
manager.company = 'faleno'


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


def search_girls():

    ChromeOptions = Options()

    ChromeOptions.add_argument('--headless')
    ChromeOptions.add_argument('--disable-gpu')

    prefs = {"profile.managed_default_content_settings.images": 2}
    ChromeOptions.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(chrome_options = ChromeOptions)

    time.sleep(5)

    driver.get("https://faleno.jp/top/actress/")

    time.sleep(5)

    driver.find_element_by_link_text('は　い').click()

    time.sleep(5)

    infos = driver.find_elements_by_xpath("//li[@data-mh='group01']")
    
    actresses = []

    for info in infos:

        actress = {'headshot': None, 'jp': None, 'en': None, 'ch': None, 'birth': None, 'company': None, 'body': None, 'twitter': None, 'ig': None}

        # driver.find_element_by_xpath only read the first one element

        root = etree.HTML(info.get_attribute('innerHTML'))

        names = root.xpath("//div[@class='text_name']")
        for name in names:
            actress['jp'] = name.text

        ennames = root.xpath("//div[@class='text_name']/span")
        for en in ennames:
            actress['en'] = en.text

        urls = root.xpath("//div[@class='img_actress01']/a/@href")
        for url in urls:
            actress['url'] = url

        imgs = root.xpath("//div[@class='img_actress01']/a/figure/img/@src")
        for img in imgs:
            actress['headshot'] = img

        actress['company'] = manager.company

        actresses.append(actress)

    driver.quit()

    actresses.pop()

    return actresses


def get_post(actress):

    ChromeOptions = Options()

    ChromeOptions.add_argument('--headless')
    ChromeOptions.add_argument('--disable-gpu')

    prefs = {"profile.managed_default_content_settings.images": 2}
    ChromeOptions.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(chrome_options = ChromeOptions)

    time.sleep(5)

    driver.get('https://faleno.jp/top/')

    time.sleep(5)

    driver.find_element_by_link_text('は　い').click()

    time.sleep(5)

    posts = []
    
    driver.get(actress['url'])
    '''
    time.sleep(5)

    infos = driver.find_elements_by_xpath("//div[@class='waku_kanren01']")

    for info in infos:

        root = etree.HTML(info.get_attribute('innerHTML'))
        
        img_list = root.cssselect('a > img')
        image = img_list[0].get('src') 

        number_list = root.xpath("//div[@class='text_name']/a")
        number = number_list[0].get('href').split("/")[-2]

        title = img_list[0].get('alt')

        day_list = root.xpath("//div[@class='btn08']")
        day = day_list[0].text.split(" ")[0].replace("/", "-")

        posts.append({'day': day, 'number': number, 'name': actress, 'title': title, 'cover': image, 'company': manager.company})
    
    time.sleep(5)
    '''
    prof = driver.find_element_by_xpath("//div[@class='box_actress02_list clearfix']")

    root = etree.HTML(prof.get_attribute('innerHTML'))
    
    profs = root.xpath("//ul/li/p")
    actress['birth'] = profs[0].text
    actress['body'] = profs[2].text

    cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]

    cookiestr = ";".join(item for item in cookie)

    driver.quit()

    return posts, cookiestr


def download_video(videos):

    for video in videos:
        
        dirpath = r'.\Girls_video.\Faleno.\{0}'.format(video['name'])
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        image = get_content(video['image'])

        file_name = video['day'] + " " + video['number'] + " " + video['name'] + " " + video['title']

        file_path = r'.\Girls_video.\Faleno.\{0}\{1}.{2}'.format(video['name'], file_name, 'jpg')

        download_obj(image, file_path)

        try:
            download_obj(image, file_path)

            print('{0} download success'.format(file_name))

        except:
            print('{0} download fail'.format(file_name))


def get_data(actress):

    posts, cookie = get_post(actress)
    
    manager.cookie = cookie

    savefiles.save_data(posts, manager.company, manager.sql_password)

    '''
    download_video(posts, cookie)
   
    print('download success')
    '''


def main(sql_password):

    start = time.time()
    
    actresses = search_girls()
    
    manager.sql_password = sql_password
    '''
    for actress in actresses:
        
        last_update_day = savefiles.check_day(actress['jp'], manager.company, sql_password)

        if last_update_day:
            faleno_updater.main(last_update_day['day'], actress, sql_password)

        else:
            get_data(actress)

        print('{0} video items save complete.'.format(actress['jp']))
    '''
    for actress in actresses:

        posts, cookie = get_post(actress)
    savefiles.save_actresslist(actresses, sql_password)
    
    print(' Success !!!! ╮(╯  _ ╰ )╭')

    end = time.time()

    total_time = end - start

    hour = total_time // 3600

    min = (total_time - 3600 * hour) // 60

    sec = total_time - 3600 * hour - 60 * min

    print(f'Totel spend time:{int(hour)}h {int(min)}m {int(sec)}s')
    
