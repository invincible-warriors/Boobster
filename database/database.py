import random
import pymongo
import telegram

import config


class URLAlreadyExistsError(Exception):
    pass


class URLBlocked(Exception):
    pass


class URLNotFoundError(Exception):
    pass


class CategoryNotFoundError(Exception):
    pass


class CollectionNotFoundError(Exception):
    pass


class IsNotSorterError(Exception):
    pass


class SorterAlreadyExistsError(Exception):
    pass


class IsNotClientError(Exception):
    pass


class ClientAlreadyExistsError(Exception):
    pass


class Database:
    """
    Main class of MongoDB
    """
    def __init__(
        self,
        user=config.MONGO_DB_USER,
        password=config.MONGO_DB_PASSWORD,
        cluster=config.MONGO_DB_CLUSTER,
    ):
        self.mongo_client = pymongo.MongoClient(
            f"mongodb+srv://{user}:{password}@{cluster}.ejtej.mongodb.net/retryWrites=true&w=majority"
        )

    class DictToObj:
        def __init__(self, dictionary: dict):
            for key, value in dictionary.items():
                setattr(self, key, value)


class Photos(Database):
    """
    Subclass of MongoDB contains Photos Database
    """
    def __init__(
        self,
        user=config.MONGO_DB_USER,
        password=config.MONGO_DB_PASSWORD,
        cluster=config.MONGO_DB_CLUSTER,
    ):
        super().__init__(user, password, cluster)
        self.allowed_photos = self.mongo_client.get_database("Photos").get_collection("AllowedPhotosURLs")
        self.blocked_photos = self.mongo_client.get_database("Photos").get_collection("BlockedPhotosURLs")
        self.unsorted_photos = self.mongo_client.get_database("Photos").get_collection("UnsortedPhotosURLs")

    def add_to_allowed_photo_url(self, url: str, categories: list[str]) -> None:
        """
        Adds photo URL to the Photos.AllowedPhotosURLs database

        :param url: photo URL
        :param categories: photo categories
        :return: None
        :raises URLAlreadyExistsError: if url already exists
        :raises URLBlocked: if url in blacklist
        """
        if list(self.allowed_photos.find({"url": url})):
            raise URLAlreadyExistsError
        if list(self.blocked_photos.find({"url": url})):
            raise URLBlocked
        self.allowed_photos.insert_one({
            "url": url,
            "categories": categories
        })

    def delete_from_allowed_photo_url(self, url: str) -> None:
        """
        Deletes photo URL from the Photos.AllowedPhotosURLs database

        :param url: photo URL
        :return: None
        """
        self.allowed_photos.delete_one({"url": url})

    def add_to_unsorted_photo_url(self, url: str) -> None:
        """
        Adds photo URL to the Photos.UnsortedPhotosURLs database

        :param url: photo URL
        :return: None
        :raises URLAlreadyExistsError: if url already exists
        :raises URLBlocked: if url in blacklist
        """
        if list(self.unsorted_photos.find({"url": url})):
            raise URLAlreadyExistsError
        if list(self.blocked_photos.find({"url": url})):
            raise URLBlocked
        self.unsorted_photos.insert_one({"url": url})

    def delete_from_unsorted_photo_url(self, url: str) -> None:
        """
        Deletes photo URL from the Photos.UnsortedPhotosURLs database

        :param url: photo URL
        :return: None
        """
        self.unsorted_photos.delete_one({"url": url})

    def add_to_blocked_photo_url(self, url: str) -> None:
        """
        Adds photo URL to the Photos.BlockedPhotosURLs database

        :param url: photo URL
        :return: None
        :raises URLAlreadyExistsError: if url already exists
        """
        if list(self.blocked_photos.find({"url": url})):
            raise URLAlreadyExistsError
        self.blocked_photos.insert_one({"url": url})

    def get_photo_for_sorting(self) -> str:
        """
        Returns photo URL from the Photos.UnsortedPhotosURLs database

        :return: photo URL
        """
        return self.unsorted_photos.find_one()["url"]

    def delete_from_blocked_photo_url(self, url: str) -> None:
        """
        Deletes photo URL from the Photos.BlockedPhotosURLs database

        :param url: photo URL
        :return: None
        """
        self.blocked_photos.delete_one({"url": url})

    def get_one_random_photo_url(self) -> str:
        """
        Returns one random photo URL from the Photos.AllowedPhotosURLs database

        :return: photo URL
        """
        allowed_photos_data = [obj["url"] for obj in self.allowed_photos.find()]
        url = random.choice(allowed_photos_data)
        return url

    def get_five_random_photo_urls(self) -> list[str]:
        """
        Returns five random photos URLs from the Photos.AllowedPhotosURLs database

        :return: photos URLs
        """
        allowed_photos_data = [obj["url"] for obj in self.allowed_photos.find()]
        random.shuffle(allowed_photos_data)
        urls = allowed_photos_data[:5]
        return urls

    def get_one_photo_url_by_category(self, category: str) -> str:
        """
        Returns one photo URL by category from the Photos.AllowedPhotosURLs database

        :param category: photo URL category
        :return: photo URL
        """
        if category not in config.categories:
            raise CategoryNotFoundError
        allowed_photos_data = [obj["url"] for obj in self.allowed_photos.find() if category in obj["categories"]]
        url = random.choice(allowed_photos_data)
        return url

    def get_five_photo_by_category(self, category) -> list[str]:
        """
        Returns five photos URLs by category from the Photos.AllowedPhotosURLs database

        :param category: photo URL category
        :return: photos URLs
        """
        if category not in config.categories:
            raise CategoryNotFoundError
        allowed_photos_data = [obj["url"] for obj in self.allowed_photos.find() if category in obj["categories"]]
        random.shuffle(allowed_photos_data)
        urls = allowed_photos_data[:5]
        return urls

    def get_stats_of_photos(self) -> dict:
        """
        Statistic of number of photos in selected collections.

        :return: Dictionary with counters
        """
        allowed_photos_data = list(self.allowed_photos.find())
        allowed_photos_counter = {"all": len(allowed_photos_data)}
        for obj in allowed_photos_data:
            for category in obj["categories"]:
                if category in allowed_photos_counter.keys():
                    allowed_photos_counter[category] += 1
                else:
                    allowed_photos_counter[category] = 1

        unsorted_photos_data = self.unsorted_photos.find()
        unsorted_photos_counter = len(list(unsorted_photos_data))

        blocked_photos_data = self.blocked_photos.find()
        blocked_photos_counter = len(list(blocked_photos_data))

        counters = {
            config.Collections.allowed: allowed_photos_counter,
            config.Collections.unsorted: unsorted_photos_counter,
            config.Collections.blocked: blocked_photos_counter
        }

        return counters


class Users(Database):
    def __init__(
        self,
        user=config.MONGO_DB_USER,
        password=config.MONGO_DB_PASSWORD,
        cluster=config.MONGO_DB_CLUSTER,
    ):
        super().__init__(user, password, cluster)
        self.sorters = self.mongo_client.get_database("Users").get_collection("Sorters")
        self.clients = self.mongo_client.get_database("Users").get_collection("Clients")

    def is_sorter(self, user_id: int) -> bool:
        return bool(self.sorters.find_one({"user.id": user_id}))
    
    def add_sorter(self, user: telegram.User) -> None:
        if self.is_sorter(user.id):
            raise SorterAlreadyExistsError
        user = {
            "id": user.id,
            "first_name": user.first_name,
            "username": user.username
        }
        photos_counter = {
            "delete": 0,
            "aesthetics": 0,
            "nudes": 0,
            "full_nudes": 0
        }
        self.sorters.insert_one({
            "user": user,
            "photos_counter": photos_counter,
            "current_url": ""
        })

    def remover_sorter(self, user: telegram.User) -> None:
        if not self.is_sorter(user.id):
            raise IsNotSorterError
        self.sorters.delete_one({"user.id": user.id})

    def set_current_url_sorter(self, user: telegram.User, photo_url: str) -> None:
        if not self.is_sorter(user.id):
            raise IsNotSorterError
        self.sorters.update_one({"user.id": user.id}, {"$set": {"current_url": photo_url}})

    def get_current_url_sorter(self, user: telegram.User) -> str:
        if not self.is_sorter(user.id):
            raise IsNotSorterError
        return self.sorters.find_one({"user.id": user.id})["current_url"]

    def add_one_to_category_sorter(self, user: telegram.User, category: str) -> None:
        if not self.is_sorter(user.id):
            raise IsNotSorterError
        current_value = self.sorters.find_one({"user.id": user.id})["photos_counter"][category]
        self.sorters.update_one(
            {"user.id": user.id},
            {"$set": {f"photos_counter.{category}": current_value + 1}}
        )

    def get_stats_of_sorter(self, user: telegram.User):
        if not self.is_sorter(user.id):
            raise IsNotSorterError
        sorter = self.sorters.find_one({"user.id": user.id})
        counter = sorter["photos_counter"]
        return counter

    def is_client(self, user_id: int) -> bool:
        return bool(self.clients.find_one({"user.id": user_id}))

    def add_client(self, user: telegram.User) -> None:
        if self.is_client(user.id):
            raise ClientAlreadyExistsError
        user = {
            "id": user.id,
            "first_name": user.first_name,
            "username": user.username
        }
        photos_counter = {
            "aesthetics": 0,
            "nudes": 0,
            "full_nudes": 0
        }
        self.clients.insert_one({
            "user": user,
            "photos_counter": photos_counter,
        })

    def remove_client(self, user: telegram.User) -> None:
        if not self.is_client(user.id):
            raise IsNotClientError
        self.clients.delete_one({"user.id": user.id})

    def add_number_to_category_client(self, user: telegram.User, category: str, number: int) -> None:
        if not self.is_client(user.id):
            raise IsNotClientError
        current_value = self.clients.find_one({"user.id": user.id})["photos_counter"][category]
        self.clients.update_one(
            {"user.id": user.id},
            {"$set": {f"photos_counter.{category}": current_value + number}}
        )

    def get_stats_of_client(self, user: telegram.User) -> dict:
        if not self.is_client(user.id):
            raise IsNotClientError
        client = self.clients.find_one({"user.id": user.id})
        counter = client["photos_counter"]
        return counter
