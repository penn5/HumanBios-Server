# HumanBios Server

## Setup
#### Python (3.7+)
```
$ python -m venv .venv
$ source .venv/bin/activate
$ python -m pip install -r requirements.txt
```
#### Update modules
```
$ git submodule update --init --recursive
```
#### Database
First configure aws  
**Important:** DynamoDB needs aws config even for local use, so we can just fill it with dummy data  
```
$ aws configure
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-west-2
Default output format [None]: json
```
Pull database image
```
docker pull amazon/dynamodb-local
```
Run database image
```
docker run -p 8000:8000 amazon/dynamodb-local
```
Database image `docker-compose.yml`:
```
version: "3.7"

services:
  dynamodb:
    container_name: dynamodb-local
    image: amazon/dynamodb-local
    restart: unless-stopped
    ports:
     - 8000:8000

networks:
  default:
    external:
      name: caddynet
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