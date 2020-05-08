#!/bin/bash

docker image rm gbex_gbex --force
docker container rm gbex_db_1 --force
docker volume rm gbex_pgdata --force
docker volume rm gbex_shared_volume --force
docker container prune
docker volume prune
docker image prune