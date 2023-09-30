import os
from bs4 import BeautifulSoup
import random
import platform

class AnyWebScraper():
    def __init__(self):
        pass
    
    def webScrape(self, url):
        """
        Input: url to web scrape
        Output: Return A BeautifulSoup Object 
        """
        operating_sys = platform.system().lower()
        DIR = "anywebscraper/curl-impersonate/" + operating_sys
        files = os.listdir(DIR)
        chromes_files = [f for f in files if "chrome" in f and "android" not in f]
        file_exe = random.choice(chromes_files)
        
        result = os.system(DIR +"/" + file_exe +" "+ url + " > any-web-scraper.txt")
        
        while "any-web-scraper.txt" not in os.listdir():
            result = os.system(DIR +"/" + file_exe +" "+ url + " > any-web-scraper.txt")
        
        file = open('any-web-scraper.txt', 'r', encoding='utf-8', errors='ignore')
        response = file.read()
        file.close()
        
        if "any-web-scraper.txt" in os.listdir():
            os.remove("any-web-scraper.txt")

        soup = BeautifulSoup(response, 'html.parser')
        return soup
