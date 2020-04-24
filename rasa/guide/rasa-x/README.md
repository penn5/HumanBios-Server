
# Rasa-X Server Installation Guide (from docs)
dependencies:
`sudo apt install docker.io docker-compose`  

sudo `mkdir /etc/rasa`  
`cd /etc/rasa`

sudo `wget -qO docker-compose.yml https://storage.googleapis.com/rasa-x-releases/0.27.6/docker-compose.ce.yml`  
sudo `wget -qO rasa_x_commands.py https://storage.googleapis.com/rasa-x-releases/0.27.6/rasa_x_commands.py`  
  
create config file and configure it:  
sudo `cp $(ProjectPath)/rasa/.env .env`  
sudo `vim .env`  
**proper password generator:**  
`openssl rand -base64 16`  

copy configuration files to the project dir 
sudo `cp $(ProjectPath)/rasa/credentials.yml credentials.yml`  
sudo `cp $(ProjectPath)/rasa/endpoints.yml endpoints.yml`  
sudo `cp $(ProjectPath)/rasa/enviroments.yml enviroments.yml`  

create folders for containers:  
sudo `mkdir /etc/rasa/auth`  
sudo `mkdir /etc/rasa/certs`  
sudo `mkdir /etc/rasa/credentials`  
sudo `mkdir /etc/rasa/models`  
sudo `mkdir /etc/rasa/logs`  
sudo `mkdir /etc/rasa/terms`  
sudo `mkdir /etc/rasa/db`  

[Rasa-X terms](https://storage.googleapis.com/rasa-x-releases/rasa_x_ee_license_agreement.pdf)  
sudo `touch /etc/rasa/terms/agree.txt`  

master access  
`sudo chgrp -R root /etc/rasa/* && sudo chmod -R 770 /etc/rasa/*`  
secure db  
`sudo chown -R 1001 /etc/rasa/db && sudo chmod -R 750 /etc/rasa/db`  

build images/deploy  
sudo `docker-compose up -d`  

update admin password (remember to change the `<PASSWORD>`)  
sudo `python rasa_x_commands.py create --update admin me <PASSWORD>`  