import json
import random
from config import categories


class URLAlreadyExistsError(Exception):
    pass


class URLNotFoundError(Exception):
    pass


class CategoryNotFoundError(Exception):
    pass


def add_photo_url(url: str, categories=["aesthetics"]) -> None:
    """
    Adds photo URL to the database

    :param list(str) categories: photo categories
    :param str url: photo URL
    :return: None
    """
    with open("photos.json", "r") as photos_json:
        photos = json.load(photos_json)

        urls = [data_json["url"] for data_json in photos]
        if url in urls:
            raise URLAlreadyExistsError("URL already exists")

        photos.append({
            "url": url,
            "categories": categories
        })

        with open("photos.json", "w") as new_photos_json:
            json.dump(photos, new_photos_json, indent=2)
    photos_json.close()
    new_photos_json.close()


def remove_photo_url(url: str) -> None:
    """
    Removes photo URL from the database

    :param str url: photo URL
    :return: None
    """
    with open("photos.json", "r") as photos_json:
        photos = json.load(photos_json)
        new_photos = []

        urls = [data_json["url"] for data_json in photos]
        if url not in urls:
            raise URLNotFoundError("URL not found")

        for obj in photos:
            if obj["url"] != url:
                new_photos.append(obj)

        with open("photos.json", "w") as new_photos_json:
            json.dump(new_photos, new_photos_json, indent=2)
    photos_json.close()
    new_photos_json.close()


def get_one_random_photo_url() -> str:
    """
    Returns one random photo URL from the database

    :return: None
    """
    with open("photos.json", "r") as photos_json:
        photos = json.load(photos_json)
        urls = [data_json["url"] for data_json in photos]
        photos_json.close()
        return random.choice(urls)


def get_five_random_photo_urls() -> [str]:
    """
    Returns five random photo URLs from the database
    :return:
    """
    with open("photos.json", "r") as photos_json:
        photos = json.load(photos_json)
        urls = [data_json["url"] for data_json in photos]
        random.shuffle(urls)
        photos_json.close()
        return urls[:5]


def get_one_photo_url_by_category(category: str) -> str:
    """
    Returns one photo URL by category from the database

    :param str category: photo category
    :return: one photo URL
    """
    with open("photos.json", "r") as photos_json:
        photos = json.load(photos_json)
        if category not in categories:
            raise CategoryNotFoundError("Category not found")
        photos_by_category = [data_json["url"] for data_json in photos if category in data_json["categories"]]

        photos_json.close()
        return random.choice(photos_by_category)


def get_five_photo_by_category(category: str) -> [str]:
    """
    Returns five photo URLs by category from the database

    :param str category: photo category
    :return: five photo URLs
    """
    with open("photos.json", "r") as photos_json:
        photos = json.load(photos_json)
        if category not in categories:
            raise CategoryNotFoundError("Category not found")
        photos_by_category = [data_json["url"] for data_json in photos if category in data_json["categories"]]

        photos_json.close()
        random.shuffle(photos_by_category)
        return photos_by_category[:5]


def get_number_of_photos() -> (int, dict[str: int]):
    """
    Returns the total number of photos and the number of photos in each category

    :return: (Total number of photos, {category_name: number of photos in category})
    """
    with open("photos.json", "r") as photos_json:
        photos = json.load(photos_json)

        categories = []
        for photo_data in photos:
            for category in photo_data["categories"]:
                if category not in categories:
                    categories.append(category)

        counter = dict()
        for category in categories:
            counter[category] = len([1 for photo_data in photos if category in photo_data["categories"]])
        all_photos_number = len(photos)

        return all_photos_number, counter
