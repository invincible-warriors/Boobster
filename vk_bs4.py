import os

from bs4 import BeautifulSoup
import requests
import shutil
from selenium import webdriver


def get_urls_soup(path):
    driver = webdriver.Firefox()
    driver.get(f"https://vk.com/{path}")

    urls = []
    soup = BeautifulSoup(driver.page_source, "lxml")
    photos_data = soup.find_all("a", class_="page_post_thumb_wrap")
    for photo_data in photos_data:
        photo_url = photo_data["onclick"].split("[")[-1].split("]")[0].split(",")[0].replace("\\", "").replace('"', "")
        urls.append(photo_url)

    return urls


def save_photos(urls, path):
    for i in range(len(urls)):
        try:
            os.mkdir(f"photos/{path}")
        except Exception:
            pass
        with open(f"photos/{path}/{i + 1}.jpg", "wb") as f:
            photo = requests.get(urls[i], stream=True)
            if photo.ok:
                shutil.copyfileobj(photo.raw, f)
            print(photo, i)


if __name__ == "__main__":
    url_paths = [
        "imbabysss",
        "savage",
        "pictureeeeeeeeeee",
        "devotskii"
    ]

    for url_path in url_paths:
        urls = get_urls_soup(url_path)
        save_photos(urls, url_path)
