#!/bin/sh

docker-compose build
docker-compose push

HOST=$1
URL=$2
FACTOR=200

ssh -o StrictHostKeychecking=no -tt -i breakthrough-bot.pem $HOST <<-'ENDSSH'
sudo systemctl start docker
sudo docker stop /selenium /bot
sudo docker rm /bot

sudo docker run -d --net=bridge --shm-size=2g --name selenium selenium/standalone-chrome:3.141.59
sudo docker start /selenium
sudo docker pull gott50/breakthrough-bot
sudo docker images --no-trunc | grep '<none>' | awk '{ print $3 }' | xargs -r sudo docker rmi -f
exit
ENDSSH

ssh -o StrictHostKeychecking=no -tt -i breakthrough-bot.pem $HOST "sudo docker run -d --net=bridge --link selenium:selenium --name bot -e URL=$URL -e FACTOR=$FACTOR gott50/breakthrough-bot"

