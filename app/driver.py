from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def init_driver(headless=False):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    return webdriver.Chrome(options=chrome_options)
