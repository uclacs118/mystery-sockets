#!/bin/sh

# Delete all old containers
echo "Deleting old containers and network..."
docker stop `docker ps -q --filter "network=iso"`
docker rm `docker ps -q --filter "network=iso"`
docker network rm iso
echo "Done!"

echo "Building player container..."
docker network create --subnet 10.0.0.0/8 --ip-range 10.100.0.0/16 iso
docker build /player -t player
echo "Done!"