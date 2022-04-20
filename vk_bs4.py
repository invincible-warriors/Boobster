import os
from bs4 import BeautifulSoup
import requests
import shutil
from selenium import webdriver
from config import paths
from json_database import *


def check_correct_photo(args: str) -> bool:
    """
    Checks whether the item is a required photo

    :param str args: CSS classes of the item
    :return: True if the item is the right photo, otherwise false
    :rtype: bool
    """
    if args is None:
        return False
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
        photos_data = post_data.find_all("a", attrs={
            "class": check_correct_photo,
            "aria-label": "photo"
        })
        for photo_data in photos_data:
            photo_url = photo_data["onclick"].split("[")[-1].split("]")[0].split(",")[0].replace("\\", "").replace('"', "")
            urls.append(photo_url)
    driver.close()

    return urls


def save_photos(urls: [str], path: str) -> None:
    """
    Saves photos to database

    :param list(str) urls: List of photo urls
    :param str path: The path of community or public
    :return: None
    """

    print(f"[*] {'-' * 10} https://vk.com/{path} {'-' * 10}")
    photos_number_before, counter_before = get_number_of_photos()

    for url in urls:
        short_url = url.split('/')[-1].split('?')[0]
        try:
            if path in ["yorksthebrand", "youisbeautifulpeople", "chloe_777", "ostanovimypain", "aestheticfeels"]:
                add_photo_url(url, categories=["nudes"])
            else:
                add_photo_url(url)
            print(f"[+] Successfully added {short_url}")
        except Exception as e:
            print(e, short_url)

    photos_number_after, counter_after = get_number_of_photos()

    total_added_photos_number = photos_number_after - photos_number_before
    total_added_photos_number_counter = {}
    for category, number in counter_after.items():
        total_added_photos_number_counter[category] = counter_after[category] - counter_before.get(category, 0)

    total_added_photos_number_counter_formatted = "\n".join(
        [f"{category}: {number} new photos were added" for category, number
         in total_added_photos_number_counter.items()]
    )

    print(f"\nA total of {total_added_photos_number} photos were added\n"
          f"By categories:\n{total_added_photos_number_counter_formatted}")


def main():
    photos_number_before, counter_before = get_number_of_photos()

    for url_path in paths:
        urls = get_urls_soup(url_path)
        save_photos(urls, url_path)

    photos_number_after, counter_after = get_number_of_photos()

    total_added_photos_number = photos_number_after - photos_number_before
    total_added_photos_number_counter = {}
    for category, number in counter_after.items():
        total_added_photos_number_counter[category] = counter_after[category] - counter_before.get(category, 0)

    total_added_photos_number_counter_formatted = "\n".join(
        [f"{category}: {number} new photos were added" for category, number
         in total_added_photos_number_counter.items()]
    )

    print(f"\n\nA total of {total_added_photos_number} photos were added\n"
          f"By categories:\n{total_added_photos_number_counter_formatted}\n"
          f"\nTotal photos number: {photos_number_after}")


if __name__ == "__main__":
    main()
