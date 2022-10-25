from audioop import mul
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import re
from pathos.multiprocessing import ProcessPool
import time
import json

from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
chromedriver_autoinstaller.install()
chrome_options = Options()
ua = UserAgent()
userAgent = ua.random
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument(f"user-agent={userAgent}")
chrome_options.headless = True
chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

class Scraper():
    

    def __init__(self):
        self.urls = []
        self.titles = []
        self.headings = []
        self.links = []
        self.words = []
        self.final_dict = {}
        self.search_params = {}
        self.max_jobs = 100


    def test(self, urls):

        def get_page(url):
            try:
                driver = webdriver.Chrome(options=chrome_options)
                driver.get(url)
                print('got page')
                driver.implicitly_wait(5)
                page = driver.page_source
                driver.close()
                return page, url
            except:
                print('get page failed')
                return None

        pool = ProcessPool(nodes=len(urls)).uimap(get_page,urls)
        reddit_searches = []
        x = 1
        print(pool)

        for element in pool:
            reddit_searches.append(element)
            x+=1

        pool.join()
        return reddit_searches



    def reddit_function(self, urls):

        def get_reddit(url): 
            try:
                driver = webdriver.Chrome(options=chrome_options)
                driver.get(url)
                driver.implicitly_wait(10)
                page = driver.page_source
                driver.close()
                search = re.search(r'pre-wrap;">(.*)</pre></body>', page)
                if search: 
                    data = search.group(1)
                    r = json.loads(data)
                else:
                    return None, None
                a = pd.DataFrame(r['data']['children'])
                b = pd.DataFrame(a['data'].to_list())

                comp_search = re.search(r'\?q=(.*)&limit=', url, re.IGNORECASE)
                if comp_search:
                    company = comp_search.group(1)
                    company = company.replace('%20', ' ')
                    b['company'] = company
                else:
                    b['company'] = 'no company available'
                return b, url
            except:
                return None, None

        pool = ProcessPool(nodes=min(self.max_jobs, len(urls)))
        jobs = pool.uimap(get_reddit,urls)
        pool.close()
        reddit_searches = []
        x = 1
        for element, url in jobs:
            reddit_searches.append(element)
            x+=1
        pool.join()
        return pd.concat(reddit_searches)


    def get_many_jsons(self, urls):

        def get_reddit_post_page(url): 
            try:
                driver = webdriver.Chrome(options=chrome_options)
                driver.get(url)
                driver.implicitly_wait(10)
                page = driver.page_source
                search = re.search(r'pre-wrap;">(.*)</pre></body>', page)
                if search: 
                    data = search.group(1)
                    r = json.loads(data)
                    return r, url
            except:
                return None, None
        
        
        pool = ProcessPool(nodes=min(self.max_jobs, len(urls)))
        jobs = pool.uimap(get_reddit_post_page,urls)
        pool.close()
        reddit_searches = []
        x = 1
        for element, url in jobs:
            reddit_searches.append(element)
            x+=1
        pool.join()
        return reddit_searches
