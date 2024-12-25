#!/bin/sh

# Delete all old containers
echo "Deleting old orphaned containers..."
docker stop `docker ps -q --filter "ancestor=player"`
docker rm `docker ps -q --filter "ancestor=player"`
# docker network rm iso
echo "Done!"

echo "Building player container..."
# docker network create --subnet 10.0.0.0/8 --ip-range 10.100.0.0/16 iso
docker build /player -t player
echo "Done!"