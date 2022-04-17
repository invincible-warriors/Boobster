import os
from bs4 import BeautifulSoup
import requests
import shutil
from selenium import webdriver


def check_correct_photo(css_classes):
    return "page_post_thumb_wrap" in css_classes and "image_cover" in css_classes and ("page_post_thumb_video" not in css_classes)


driver = webdriver.Firefox()
driver.get(f"https://vk.com/savage")

soup = BeautifulSoup(driver.page_source, "lxml")
posts_data = soup.find_all("div", class_="wall_text")
for post_data in posts_data:
    photos_data = post_data.find_all("a", class_=check_correct_photo)
    print(photos_data)