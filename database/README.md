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
            ]
        } 
        ```
    * ### BlockedPhotosURLs
        Contains information about black listed photos
        ```json
        {
            "_id": ObjectId,
            "url": PhotoURL
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
            "current_url": PhotoURL
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
            }
        }
        ```