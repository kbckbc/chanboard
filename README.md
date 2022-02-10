

## Table of contents
* [Go to chanboard](#go-to-chanboard)
* [General info](#general-info)
* [Technologies](#technologies)
* [How to run](#how-to-run)


## Go to chanboard
[chanboard](http://34.125.24.66)

## General info
This is a simple board project implemented with various technique.
However, all the core functions are implemented.
Membership registration, login, posting, uploading attachments, and writing comments are all implemented.
After creating an image with docker, it was launched as an instance on Google Cloud Service.
It's a simple project, but I hope it helps at least one person.


## Technologies
Project is created with:
* Web framework : Flask
* Database : Mongodb
* Web server : Nginx
* UI : Bootstrap
* Server : Google cloud
* Etc : Docker


## How to run
Once download the source code, run below
```
docker build -t chanboard .
docker network create <network name>
docker run --name mongo --net <network name> -v /mongodb/db:/data/db -d -p 27017:27017 --restart always mongo
docker run -d --name chanboard --net <network name> -p 80:80 chanboard
```
