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
Make & launch db
```
$ mkdir db-build
$ cd db-build
$ curl -O https://s3-us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.zip
$ unzip dynamodb_local_latest.zip
$ rm dynamodb_local_latest.zip
$ nohup java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb &
$ echo $! > save_pid.txt
```
Create tables
```
$ python -m db_models
```
Verify tables
```
$ aws dynamodb list-tables --endpoint-url http://localhost:8000
```

[Optional] Deleting tables
```
$ aws dynamodb delete-table --table-name <table_name>
```

#### Docker build
```
$ docker build -t humanbios-server .
```