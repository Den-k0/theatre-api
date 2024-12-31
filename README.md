# Theatre API

API service for theatre management written in DRF


## Run with docker

Docker should be installed

```shell
docker-compose build
docker-compose up
```

## Demo

Test credentials (auto-created superuser):
* Username: admin@example.com
* Password: adminpassword


## Features

* JWT authenticated
* Admin panel /admin/
* Documentation is located at /api/doc/swagger/
* Managing reservations and tickets
* Creating plays with genres, actors
* Creating theatre halls
* Adding performances
* Filtering plays and performances

## Theatre Database Structure

![Theatre Database Structure](images/theatre_diagram.webp)

## Theatre Swagger Documentation
![Theatre Database Structure](images/swagger_doc_image_demo1.webp)
![Theatre Database Structure](images/swagger_doc_image_demo2.webp)
![Theatre Database Structure](images/swagger_doc_image_demo3.webp)
