import datetime
import random

import pymongo
import telegram

from main.config import config


class URLAlreadyExistsError(Exception):
    pass


class PhotoAlreadyExistsError(Exception):
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
        """
        Checks if user is sorter

        :param user_id: telegram.User.id
        :return: True or False
        """
        return bool(self.sorters.find_one({"user.id": user_id}))

    def add_sorter(self, user: telegram.User) -> None:
        """
        Adds user as sorter

        :param user: telegram.User
        :return: None
        """
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
            "added_at": datetime.datetime.now(),
            "current_url": ""
        })

    def remove_sorter(self, user: telegram.User) -> None:
        """
        Removes user as sorter

        :param user: telegram.User
        :return: None
        """
        if not self.is_sorter(user.id):
            raise IsNotSorterError
        self.sorters.delete_one({"user.id": user.id})

    def set_current_photo_sorter(self, user: telegram.User, photo: dict[str, str]) -> None:
        """
        Sets url as current sorter's url

        :param user: telegram.User
        :param photo: dict of photo URL and hash
        :return: None
        """
        if not self.is_sorter(user.id):
            raise IsNotSorterError
        self.sorters.update_one(
            {"user.id": user.id},
            {"$set": {
                "photo.url": photo["url"],
                "photo.hash": photo["hash"]
            }}
        )

    def get_current_photo_sorter(self, user: telegram.User) -> str:
        """
        Returns currents sorter's url

        :param user: telegram.User
        :return: sorter's URL
        """
        if not self.is_sorter(user.id):
            raise IsNotSorterError
        return self.sorters.find_one({"user.id": user.id})["photo"]

    def add_one_to_category_sorter(self, user: telegram.User, category: str) -> None:
        """
        Adds one point to sorter's category

        :param user: telegram.User
        :param category: name of category
        :return: None
        """
        if not self.is_sorter(user.id):
            raise IsNotSorterError
        current_value = self.sorters.find_one({"user.id": user.id})["photos_counter"][category]
        self.sorters.update_one(
            {"user.id": user.id},
            {"$set": {
                f"photos_counter.{category}": current_value + 1,
                "last_seen": datetime.datetime.now()
            }}
        )

    def get_stats_of_sorter(self, user: telegram.User) -> dict:
        """
        Returns statistics of sorter

        :param user: telegram.User
        :return: statistics dict of sorter
        """
        if not self.is_sorter(user.id):
            raise IsNotSorterError
        sorter = self.sorters.find_one({"user.id": user.id})
        counter = sorter["photos_counter"]
        counter["all"] = sum(counter.values())
        return counter

    def get_stats_of_all_sorters(self, sorting: str | None = None) -> list:
        """
        Returns statistics of all users

        :param sorting: type of sorting (ASC|DESC|None)
        :return: list of statistics dicts of sorters
        """
        data = list(self.sorters.find({}, {"_id": 0}))
        for i in range(self.sorters.count_documents({})):
            data[i]["photos_counter"]["all"] = sum(data[i]["photos_counter"].values())
        if sorting:
            data.sort(key=lambda obj: obj["photos_counter"]["all"], reverse=(sorting == "ASC"))
        return data

    def is_client(self, user_id: int) -> bool:
        """
        Checks if user is clients

        :param user_id: telegram.User.id
        :return: True of False
        """
        return bool(self.clients.find_one({"user.id": user_id}))

    def add_client(self, user: telegram.User) -> None:
        """
        Adds user as client

        :param user: telegram.User
        :return: None
        """
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
            "added_at": datetime.datetime.now()
        })

    def remove_client(self, user: telegram.User) -> None:
        """
        Removes user as client

        :param user: telegram.User
        :return: None
        """
        if not self.is_client(user.id):
            raise IsNotClientError
        self.clients.delete_one({"user.id": user.id})

    def add_number_to_category_client(self, user: telegram.User, category: str, number: int) -> None:
        """
        Adds one point to client's category

        :param user: telegram.User
        :param category: name of category
        :param number: number of points
        :return: None
        """
        if not self.is_client(user.id):
            self.add_client(user)
        current_value = self.clients.find_one({"user.id": user.id})["photos_counter"][category]
        self.clients.update_one(
            {"user.id": user.id},
            {"$set": {
                f"photos_counter.{category}": current_value + number,
                "last_seen": datetime.datetime.now()
            }}
        )

    def get_stats_of_client(self, user: telegram.User) -> dict:
        """
        Returns statistics of client

        :param user: telegram.User
        :return: statistics dict of client
        """
        if not self.is_client(user.id):
            raise IsNotClientError
        client = self.clients.find_one({"user.id": user.id})
        counter = client["photos_counter"]
        counter["all"] = sum(counter.values())
        return counter

    def get_stats_of_all_clients(self) -> list:
        data = list(self.clients.find({}, {"_id": 0}))
        for i in range(self.clients.count_documents({})):
            data[i]["photos_counter"]["all"] = sum(data[i]["photos_counter"].values())
        return data


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
        self.sorter_urls_stack = []

    def add_to_allowed_photo(self, photo: dict[str, str], user: telegram.User | str, categories: list[str]) -> None:
        """
        Adds photo URL to the Photos.AllowedPhotosURLs database

        :param photo: dict of photo URL and hash
        :param user: telegram User who added the photo
        :param categories: photo categories
        :return: None
        """
        if isinstance(user, telegram.User):
            added_by = {
                "id": user.id,
                "first_name": user.first_name,
                "username": user.username
            }
        else:
            added_by = user
        self.allowed_photos.insert_one({
            "url": photo["url"],
            "categories": categories,
            "added_info": {
                "at": datetime.datetime.now(),
                "by": added_by
            },
            "hash": photo["hash"]
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
        """
        self.unsorted_photos.insert_one({"url": url})

    def delete_from_unsorted_photo_url(self, url: str) -> None:
        """
        Deletes photo URL from the Photos.UnsortedPhotosURLs database

        :param url: photo URL
        :return: None
        """
        self.unsorted_photos.delete_one({"url": url})

    def add_to_blocked_photo_url(self, url: str, user: telegram.User | str) -> None:
        """
        Adds photo URL to the Photos.BlockedPhotosURLs database

        :param url: photo URL
        :param user: telegram User who added the photo
        :return: None
        """
        if isinstance(user, telegram.User):
            added_by = {
                "id": user.id,
                "first_name": user.first_name,
                "username": user.username
            }
        else:
            added_by = user
        self.blocked_photos.insert_one({
            "url": url,
            "added_info": {
                "at": datetime.datetime.now(),
                "by": added_by
            }
        })

    def delete_from_blocked_photo_url(self, url: str) -> None:
        """
        Deletes photo URL from the Photos.BlockedPhotosURLs database

        :param url: photo URL
        :return: None
        """
        self.blocked_photos.delete_one({"url": url})

    def create_sorter_urls_stack(self):
        self.sorter_urls_stack = list(self.unsorted_photos.find({}, {"_id": 0, "url": 1, "hash": 1}).limit(100))

    def get_photo_for_sorting(self) -> str:
        """
        Returns photo URL from the Photos.UnsortedPhotosURLs database

        :return: photo URL
        """
        if not self.sorter_urls_stack:
            self.create_sorter_urls_stack()
        photo = self.sorter_urls_stack.pop()
        return photo

    def get_one_random_photo_url(self) -> str:
        """
        Returns one random photo URL from the Photos.AllowedPhotosURLs database

        :return: photo URL
        """
        with self.allowed_photos.aggregate([{"$sample": {"size": 1}}]) as photos_data:
            url = list(photos_data)[0]["url"]
        return url

    def get_five_random_photo_urls(self) -> list[str]:
        """
        Returns five random photos URLs from the Photos.AllowedPhotosURLs database

        :return: photos URLs
        """
        urls = []
        with self.allowed_photos.aggregate([{"$sample": {"size": 5}}]) as photos_data:
            for photo in photos_data:
                urls.append(photo["url"])
        return urls

    def get_one_photo_by_category(self, category: str) -> str:
        """
        Returns one photo URL by category from the Photos.AllowedPhotosURLs database

        :param category: photo URL category
        :return: photo URL
        """
        if category not in config.categories:
            raise CategoryNotFoundError
        with self.allowed_photos.aggregate([
            {"$match": {
                "categories": {"$in": [category]}
            }},
            {"$sample": {"size": 1}}
        ]) as photos_data:
            url = list(photos_data)[0]["url"]
        return url

    def get_five_photo_by_category(self, category) -> list[str]:
        """
        Returns five photos URLs by category from the Photos.AllowedPhotosURLs database

        :param category: photo URL category
        :return: photos URLs
        """
        if category not in config.categories:
            raise CategoryNotFoundError
        urls = []
        with self.allowed_photos.aggregate([
            {"$match": {
                "categories": {"$in": [category]}
            }},
            {"$sample": {"size": 5}}
        ]) as photos_data:
            for photo in photos_data:
                urls.append(photo["url"])
        return urls

    def get_stats_of_photos(self) -> dict:
        """
        Statistic of number of photos in selected collections.

        :return: Dictionary with counters
        """
        allowed_photos_data = list(self.allowed_photos.find())
        allowed_photos_counter = {"all": self.allowed_photos.count_documents({})}
        for obj in allowed_photos_data:
            for category in obj["categories"]:
                if category in allowed_photos_counter.keys():
                    allowed_photos_counter[category] += 1
                else:
                    allowed_photos_counter[category] = 1

        unsorted_photos_counter = self.unsorted_photos.count_documents({})
        blocked_photos_counter = self.blocked_photos.count_documents({})

        counters = {
            config.Collections.allowed: allowed_photos_counter,
            config.Collections.unsorted: unsorted_photos_counter,
            config.Collections.blocked: blocked_photos_counter
        }

        return counters


photos = Photos()
users = Users()
