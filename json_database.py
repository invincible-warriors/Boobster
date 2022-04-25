import json
import random
from config import categories, Files


class URLAlreadyExistsError(Exception):
    pass


class URLBlocked(Exception):
    pass


class URLNotFoundError(Exception):
    pass


class CategoryNotFoundError(Exception):
    pass


def add_photo_url(url: str, categories=None, file=Files.unsorted_photos) -> None:
    """
    Adds photo URL to the database

    :param file:
    :param list(str) categories: photo categories
    :param str url: photo URL
    :return: None
    """
    if categories is None:
        categories = ["aesthetics"]
    with open(file, "r") as photos_json:
        photos = json.load(photos_json)
        urls = [data_json["url"] for data_json in photos]
        if url in urls:
            raise URLAlreadyExistsError("URL already exists")
        with open(Files.blocked_photos, "r") as blocked_photos:
            if url in json.load(blocked_photos):
                raise URLBlocked("URL blocked")

        photos.append({
            "url": url,
            "categories": categories
        })

        with open(file, "w") as new_photos_json:
            json.dump(photos, new_photos_json, indent=2)


def remove_photo_url(url: str, file=Files.unsorted_photos) -> None:
    """
    Removes photo URL from the database

    :param str url: photo URL
    :return: None
    """
    with open(Files.blocked_photos, "r") as blocked_photos:
        blocked_photos = list(set(json.load(blocked_photos)))
        blocked_photos.append(url)
        with open(Files.blocked_photos, "w") as blocked_photos_json:
            json.dump(blocked_photos, blocked_photos_json, indent=2)

    with open(file, "r") as photos_json:
        photos = json.load(photos_json)
        new_photos = []

        urls = [data_json["url"] for data_json in photos]
        if url not in urls:
            raise URLNotFoundError("URL not found")

        for obj in photos:
            if obj["url"] != url:
                new_photos.append(obj)

        with open(file, "w") as new_photos_json:
            json.dump(new_photos, new_photos_json, indent=2)


def get_one_random_photo_url(file=Files.unsorted_photos) -> str:
    """
    Returns one random photo URL from the database

    :return: None
    """
    with open(file, "r") as photos_json:
        photos = json.load(photos_json)
        urls = [data_json["url"] for data_json in photos]
        return random.choice(urls)


def get_five_random_photo_urls(file=Files.unsorted_photos) -> [str]:
    """
    Returns five random photo URLs from the database
    :return:
    """
    with open(file, "r") as photos_json:
        photos = json.load(photos_json)
        urls = [data_json["url"] for data_json in photos]
        random.shuffle(urls)
        return urls[:5]


def get_one_photo_url_by_category(category: str, file=Files.unsorted_photos) -> str:
    """
    Returns one photo URL by category from the database

    :param str category: photo category
    :return: one photo URL
    """
    with open(file, "r") as photos_json:
        photos = json.load(photos_json)
        if category not in categories:
            raise CategoryNotFoundError("Category not found")
        photos_by_category = [data_json["url"] for data_json in photos if category in data_json["categories"]]
        return random.choice(photos_by_category)


def get_five_photo_by_category(category: str, file=Files.unsorted_photos) -> [str]:
    """
    Returns five photo URLs by category from the database

    :param str category: photo category
    :return: five photo URLs
    """
    with open(file, "r") as photos_json:
        photos = json.load(photos_json)
        if category not in categories:
            raise CategoryNotFoundError("Category not found")
        photos_by_category = [data_json["url"] for data_json in photos if category in data_json["categories"]]

        random.shuffle(photos_by_category)
        return photos_by_category[:5]


def get_number_of_photos(file=Files.unsorted_photos) -> (int, dict[str: int]):
    """
    Returns the total number of photos and the number of photos in each category

    :return: (Total number of photos, {category_name: number of photos in category})
    """
    with open(file, "r") as photos_json:
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


def new_filterer(user_id):
    user_id = str(user_id)
    with open(Files.filterers, "r") as filterers:
        filterers = json.load(filterers)
        return not (user_id in filterers.keys())


def add_filterer(user_id):
    user_id = str(user_id)
    with open(Files.filterers, "r") as filterers:
        filterers = json.load(filterers)
        if not new_filterer(user_id):
            return
        filterers[user_id] = {
            "number": 0
        }
        with open(Files.filterers, "w") as filterers_json:
            json.dump(filterers, filterers_json, indent=2)


def set_current_url_filterer(user_id, photo_url):
    user_id = str(user_id)
    with open(Files.filterers, "r") as filterers:
        filterers = json.load(filterers)
        filterers[user_id]["current_url"] = photo_url
        filterers[user_id]["number"] += 1
        with open(Files.filterers, "w") as filterers_json:
            json.dump(filterers, filterers_json, indent=2)


def get_current_url_filterer(user_id):
    user_id = str(user_id)
    with open(Files.filterers, "r") as filterers:
        filterers = json.load(filterers)
        return filterers[user_id]["current_url"]
