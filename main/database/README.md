# Database structure

- ## Photos
    * ### AllowedPhotosURLs
        Contains information about sorted photos
        ```json
        {
            "_id": ObjectId,
            "url": PhotoURL,
            "categories": [
                list of categories
            ],
            "added_info": {
                "at": datetime.datetime.now(),
                "by": {
                    "id": telegram.user.id,
                    "first_name": telegram.user.first_name,
                    "username": telegram.user.username
                }
            },
            "hash": hash
        }
        ```
    * ### BlockedPhotosURLs
        Contains information about black listed photos
        ```json
        {
            "_id": ObjectId,
            "url": PhotoURL,
            "added_info": {
                "at": datetime.datetime.now(),
                "by": {
                    "id": telegram.user.id,
                    "first_name": telegram.user.first_name,
                    "username": telegram.user.username
                }
            }
        } 
        ```
    * ### UnsortedPhotosURLs
        Contains information about unsorted photos
        ```json
        {
            "_id": ObjectId,
            "url": PhotoURL
        } 
        ```

- ## Users
    * ### Sorters
        Contains information about sorters
        ```json
        {
            "_id": ObjectId,
            "user": {
                "id": telegram.user.id,
                "first_name": telegram.user.first_name,
                "username": telegram.user.username
            },
            "photos_counter": {
                "delete": number,
                "aesthetics": number,
                "nudes": number,
                "full_nudes": number,
            },
            "current_url": PhotoURL,
            "added_at": datetime.datetime.now()
        }
        ```
    * ### Clients 
        Contains information about clients
        ```json
        {
            "_id": ObjectId,
            "user": {
                "id": telegram.user.id,
                "first_name": telegram.user.first_name,
                "username": telegram.user.username
            },
            "photos_counter": {
                "aesthetics": number,
                "nudes": number,
                "full_nudes": number,
            },
            "added_at": datetime.datetime.now(),
            "last_seen": datetime.datetime.now()
        }
        ```