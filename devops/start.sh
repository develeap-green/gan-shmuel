#!/bin/bash

docker compose up -d

docker network connect gan-shmuel_nginx-network devops-nginx-1 