#!/bin/sh

docker-compose build
docker-compose push

HOST=$1
URL=$2

ssh -o StrictHostKeychecking=no -tt -i breakthrough-bot.pem $HOST <<-'ENDSSH'
sudo systemctl start docker
sudo docker stop /selenium /bot
sudo docker rm /bot

sudo docker run -d --net=bridge --shm-size=128M --name selenium selenium/standalone-chrome:3.141.59
sudo docker start /selenium

exit
ENDSSH

ssh -o StrictHostKeychecking=no -tt -i breakthrough-bot.pem $HOST "sudo docker run -d --net=bridge --link selenium:selenium --name bot -e URL=$URL gott50/breakthrough-bot"

