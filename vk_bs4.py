import os
from bs4 import BeautifulSoup
import requests
import shutil
from selenium import webdriver
from config import paths


def check_correct_photo(args: str) -> bool:
    """
    Checks whether the item is a required photo

    :param str args: CSS classes of the item
    :return: True if the item is the right photo, otherwise false
    :rtype: bool
    """

    return all(
        class_ in args for class_ in [
            "page_post_thumb_wrap",
            "image_cover"
        ]
    ) and not any(
        class_ in args for class_ in [
            "page_post_thumb_video"
        ]
    )


def get_urls_soup(path: str) -> [str]:
    """
    Returns a list of photo urls

    :param str path: The path of community or public
    :return: the list of photo urls
    :rtype: list[str]
    """

    driver = webdriver.Firefox()
    driver.get(f"https://vk.com/{path}")

    urls = []
    soup = BeautifulSoup(driver.page_source, "lxml")
    posts_data = soup.find_all("div", class_="wall_text")
    for post_data in posts_data:
        photos_data = post_data.find_all("a", class_=check_correct_photo)
        for photo_data in photos_data:
            photo_url = photo_data["onclick"].split("[")[-1].split("]")[0].split(",")[0].replace("\\", "").replace('"', "")
            urls.append(photo_url)
    driver.close()

    return urls


def save_photos(urls: [str], path: str) -> None:
    """
    Saves photos to dir

    :param list(str) urls: List of photo urls
    :param str path: The path of community or public
    :return: None
    """

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


def main():
    url_paths = paths

    for url_path in url_paths:
        urls = get_urls_soup(url_path)
        save_photos(urls, url_path)


if __name__ == "__main__":
    main()
