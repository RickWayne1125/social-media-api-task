# Social Media API

## How to build and run?

```shell
docker build -t social_media_api .
docker run -p 1125:5000 social_media_api
```

## Architecture

Every time a user makes a request, the app will first check if the data is in the cache. If it is, it will return the data from the cache. If it is not, it will query the database and store the data in the cache for future requests.

When the data is updated, the cache will be cleared.

```shell
+----------------+
|    Flask App   |
+----------------+
        |
+----------------+
|   Redis Cache  |
+----------------+
        |
+----------------+
|  SQL Database  |
+----------------+
```