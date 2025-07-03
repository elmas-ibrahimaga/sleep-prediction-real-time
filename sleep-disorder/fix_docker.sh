#!/bin/bash

echo "Stopping and removing all containers..."
docker rm -f $(docker ps -aq)

echo "Bringing up services fresh..."
docker-compose up --force-recreate
