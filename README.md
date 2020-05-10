# HumanBios Server

## Prerequisites
`docker`, `docker-compose`, `python3.7`|`python3.8+`  

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
$ cd db_models
$ docker-compose up -d
```
#### Run server
```
$ cd ..
$ docker-compose up -d
```

## Development (Not Dokerized)
# Soon..
"""
First configure aws  
**Important:** DynamoDB needs aws config even for local use, so we can just fill it with dummy data  
```
$ aws configure
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-west-2
Default output format [None]: json
```

Verify database 
```
$ aws dynamodb list-tables --endpoint-url http://localhost:8000
```

[Info] Deleting tables
```
$ aws dynamodb delete-table --table-name <table_name>
```

#### Docker build
```
$ docker build -t humanbios-server .
```
