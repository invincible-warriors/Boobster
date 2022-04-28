import json
import random
import config


class URLAlreadyExistsError(Exception):
    pass


class URLBlocked(Exception):
    pass


class URLNotFoundError(Exception):
    pass


class CategoryNotFoundError(Exception):
    pass


def add_photo_url(url: str, categories=None, file=config.Files.unsorted_photos) -> None:
    """
    Adds photo URL to the database

    :param str url: photo URL
    :param str file: path to the database
    :param list(str) categories: photo categories
    :return: None
    :raises URLAlreadyExistsError: if url already exists
    :raises URLBlocked: if url in blacklist
    """
    if categories is None:
        categories = ["aesthetics"]
    with open(file, "r") as photos_json:
        photos = json.load(photos_json)
        urls = [data_json["url"] for data_json in photos]
        if url in urls:
            raise URLAlreadyExistsError("URL already exists")
        with open(config.Files.blocked_photos, "r") as blocked_photos:
            if url in json.load(blocked_photos):
                raise URLBlocked("URL blocked")

        photos.append({
            "url": url,
            "categories": categories
        })

        with open(file, "w") as new_photos_json:
            json.dump(photos, new_photos_json, indent=2)


def remove_photo_url(url: str, file=config.Files.unsorted_photos) -> None:
    """
    Removes photo URL from the database

    :param str url: photo URL
    :param str file: path to the database
    :return: None
    :raises URLNotFoundError: if url not found
    """
    with open(config.Files.blocked_photos, "r") as blocked_photos:
        blocked_photos = list(set(json.load(blocked_photos)))
        blocked_photos.append(url)
        with open(config.Files.blocked_photos, "w") as blocked_photos_json:
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


def get_one_random_photo_url(file=config.Files.unsorted_photos) -> str:
    """
    Returns one random photo URL from the database

    :param str file: path to the database
    :return: photo url
    :rtype: str
    """
    with open(file, "r") as photos_json:
        photos = json.load(photos_json)
        urls = [data_json["url"] for data_json in photos]
        return random.choice(urls)


def get_five_random_photo_urls(file=config.Files.unsorted_photos) -> list[str]:
    """
    Returns five random photo URLs from the database

    :param str file: path to the database
    :return: photos urls
    :rtype: list(str)
    """
    with open(file, "r") as photos_json:
        photos = json.load(photos_json)
        urls = [data_json["url"] for data_json in photos]
        random.shuffle(urls)
        return urls[:5]


def get_one_photo_url_by_category(category: str, file=config.Files.unsorted_photos) -> str:
    """
    Returns one photo URL by category from the database

    :param str category: photo category
    :param str file: path to the database
    :return: photo url
    :rtype: str
    :raises CategoryNotFoundError: if category not found
    """
    with open(file, "r") as photos_json:
        photos = json.load(photos_json)
        if category not in config.categories:
            raise CategoryNotFoundError("Category not found")
        photos_by_category = [data_json["url"] for data_json in photos if category in data_json["categories"]]
        return random.choice(photos_by_category)


def get_five_photo_by_category(category: str, file=config.Files.unsorted_photos) -> list[str]:
    """
    Returns five photo URLs by category from the database.

    :param str category: photo category
    :param str file: path to the database
    :return: five photo URLs
    :rtype: list(str)
    :raises: CategoryNotFoundError: if category not found
    """
    with open(file, "r") as photos_json:
        photos = json.load(photos_json)
        if category not in config.categories:
            raise CategoryNotFoundError("Category not found")
        photos_by_category = [data_json["url"] for data_json in photos if category in data_json["categories"]]

        random.shuffle(photos_by_category)
        return photos_by_category[:5]


def get_number_of_photos(file=config.Files.unsorted_photos) -> tuple[int, dict[str, int]]:
    """
    Returns the total number of photos and the number of photos in each category

    :param str file: path to the database
    :return: (Total number of photos, {category_name: number of photos in category})
    :rtype: tuple(int, dict[str, int])
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


def new_filterer(user_id: int or str) -> bool:
    """
    Checks if user is new filterer

    :param int or str user_id: Telegram user id
    :return: True or False
    :rtype: bool
    """
    user_id = str(user_id)
    with open(config.Files.filterers, "r") as filterers:
        filterers = json.load(filterers)
        return not (user_id in filterers.keys())


def add_filterer(user_id: int or str) -> None:
    """
    Adds new filterer to database

    :param int or str user_id: Telegram user id
    :return: None
    """
    user_id = str(user_id)
    with open(config.Files.filterers, "r") as filterers:
        filterers = json.load(filterers)
        if not new_filterer(user_id):
            return
        filterers[user_id] = {
            "number": 0
        }
        with open(config.Files.filterers, "w") as filterers_json:
            json.dump(filterers, filterers_json, indent=2)


def set_current_url_filterer(user_id: int or str, photo_url: str) -> None:
    """
    Sets photo URL to this user

    :param int or str user_id: Telegram user id
    :param str photo_url: photo URL
    :return: None
    """
    user_id = str(user_id)
    with open(config.Files.filterers, "r") as filterers:
        filterers = json.load(filterers)
        filterers[user_id]["current_url"] = photo_url
        filterers[user_id]["number"] += 1
        with open(config.Files.filterers, "w") as filterers_json:
            json.dump(filterers, filterers_json, indent=2)


def get_current_url_filterer(user_id: int or str) -> str:
    """
    Returns photo URL of this user

    :param int or str user_id: Telegram user id
    :return: photo URL
    :rtype: str
    """
    user_id = str(user_id)
    with open(config.Files.filterers, "r") as filterers:
        filterers = json.load(filterers)
        return filterers[user_id]["current_url"]
