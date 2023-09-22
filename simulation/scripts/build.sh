#!/bin/bash

eval $(minikube docker-env)
docker compose build