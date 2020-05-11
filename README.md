# HumanBios Server

## Prerequisites
`docker`, `docker-compose`, `python3.7`|`python3.8+`  
Make sure to create docker network for the containers
`docker network create caddynet`  

## Production
#### Get code
```
$ git clone git@github.com:HumanbiOS/HumanBios-Server.git
```
or
```
$ git clone https://github.com/HumanbiOS/HumanBios-Server.git
```
#### Update submodules
```
$ git submodule update --init --recursive
```
#### Setup .env
```
$ cp .env.example .env  
```
**Fill `.env`**  
#### Build container
```
$ docker build -t humanbios-server .
```
#### Database
Pull database image
```
$ docker pull amazon/dynamodb-local
```
Run database image
```
$ cd docker/db
$ docker-compose up -d
```
#### Run server
```
$ cd ..
$ docker-compose up -d
```

## Development (Not Dokerized)
#### Get code
```
$ git clone git@github.com:HumanbiOS/HumanBios-Server.git
```
or
```
$ git clone https://github.com/HumanbiOS/HumanBios-Server.git
```
#### Update submodules
```
$ git submodule update --init --recursive
```
#### Setup .env
```
$ cp .env.example .env  
```
**Fill `.env`**  
#### Database
Pull database image
```
$ docker pull amazon/dynamodb-local
```
Run database image
```
$ cd docker/db
$ docker-compose up -d
```
#### Run server
(return to the root dir of the project)
```
$ cd ../..
```
start app
```
$ python server.py
```