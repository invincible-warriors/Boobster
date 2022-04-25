import time
import logging

from alive_progress import alive_bar
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from config import paths, ColoredSymbols, Colors, console_width
from json_database import *


logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def get_urls_soup(path: str) -> [str]:
    """
    Returns a list of photo urls

    :param str path: The path of community or public
    :return: the list of photo urls
    :rtype: list[str]
    """

    urls = []

    start_time = time.perf_counter()
    driver = webdriver.Firefox()
    driver.get(f"https://vk.com/{path}")

    checked_posts = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    clicked_close = False
    wall_posts = driver.find_element(By.ID, "page_wall_posts")
    post_id = wall_posts.find_element(By.CSS_SELECTOR, "div._post.post.page_block").get_attribute("id")
    while True:
        if post_id not in checked_posts:
            logger.info(post_id)
            post = wall_posts.find_element(By.ID, post_id)
            photos = post.find_elements(By.CSS_SELECTOR, "a.page_post_thumb_wrap.image_cover")
            for photo in photos:
                # checks if photo is photo and not a fucking video
                if "page_post_thumb_video" in photo.get_attribute("class"):
                    continue
                photo_url = photo.get_attribute("onclick") \
                    .split("[")[-1].split("]")[0].split(",")[0].replace("\\", "").replace('"', "")
                urls.append(photo_url)

        try:
            checked_posts.append(post_id)
            new_post_id = wall_posts.find_element(
                By.XPATH, f"//div[@id='{post_id}']/following-sibling::div"
            ).get_attribute("id")
            if not new_post_id:
                raise ValueError
            post_id = new_post_id
        except Exception as e:
            photos, photo = [None] * 2
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

            if not clicked_close:
                clicked_close = True
                WebDriverWait(driver, 20).until(
                    expected_conditions.visibility_of_all_elements_located((By.CLASS_NAME, "UnauthActionBox__close"))
                )
                driver.find_element(By.CLASS_NAME, "UnauthActionBox__close").click()

            time.sleep(.5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

            post_id = wall_posts.find_element(
                By.XPATH, f"//div[@id='{post_id}']/following-sibling::div"
            ).get_attribute("id")

            if not post_id:
                break

    driver.close()
    logger.info(f"Ended in {time.perf_counter() - start_time}s. Found {len(urls)} urls")

    return urls


def save_info(func):
    def inner(*args, **kwargs):
        photos_number_before, counter_before = get_number_of_photos()

        func(*args, **kwargs)

        photos_number_after, counter_after = get_number_of_photos()
        total_added_photos_number = photos_number_after - photos_number_before
        total_added_photos_number_counter = {}
        for category, number in counter_after.items():
            total_added_photos_number_counter[category] = counter_after[category] - counter_before.get(category, 0)

        total_added_photos_number_counter_formatted = ("\n" + f"[{ColoredSymbols.vertical}] - ").join(
            [f"{category}: {Colors.purple}{number}{Colors.white} new photos were added" for category, number
             in total_added_photos_number_counter.items()]
        )

        info_text = " INFO ".center(console_width - 4, "-")
        print(
            f"\n[{ColoredSymbols.info}] {info_text}\n"
            f"[{ColoredSymbols.vertical}] A total of "
            f"{Colors.blue}{total_added_photos_number}{Colors.white} photos were added\n"
            f"[{ColoredSymbols.vertical}] By categories:\n"
            f"[{ColoredSymbols.vertical}] - {total_added_photos_number_counter_formatted}\n\n"
        )

    return inner


@save_info
def save_photos(urls: [str], path: str) -> None:
    """
    Saves photos to database

    :param list(str) urls: List of photo urls
    :param str path: The path of community or public
    :return: None
    """
    global_url = f"https://vk.com/{path}"
    formatted_url = f" {global_url} ".center(console_width - 4, "-")
    print(f"[{ColoredSymbols.info}] {formatted_url}")

    with alive_bar(len(urls), force_tty=True, dual_line=True, title=global_url) as bar:
        for url in urls:
            time.sleep(.005)
            short_url = url.split('/')[-1].split('?')[0]
            short_url = short_url[:20] + "..." + short_url[60:]

            try:
                if path in ["yorksthebrand", "youisbeautifulpeople", "chloe_777", "ostanovimypain",
                            "aestheticfeels"]:
                    add_photo_url(url, categories=["nudes"])
                else:
                    add_photo_url(url)
                print(
                    f"[{ColoredSymbols.add}] {Colors.green}Successfully added{Colors.white} {short_url}"
                )

            except Exception as e:
                print(
                    f"[{ColoredSymbols.warn}] {Colors.red}{e}{Colors.white} {short_url}"
                )

            bar.text = f"Saving {short_url}"
            bar()


@save_info
def main():
    # with alive_bar(len(paths), force_tty=True) as main_bar:
    for url_path in paths:
        urls = get_urls_soup(url_path)
        save_photos(urls, url_path)
        # main_bar()


if __name__ == "__main__":
    main()
