#!/bin/sh

docker network create --subnet 10.0.0.0/8 --ip-range 10.100.0.0/16 iso
docker build /player -t player