#! /bin/bash

set -e

echo "Installing dependencies via apt.."
sudo apt update && sudo apt install -y git make screen curl

echo "Getting Docker.."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
rm get-docker.sh

echo "Adding user to docker group.."
sudo usermod -aG docker $USER

echo "Getting kubectl.."
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl

echo "Getting minikube.."
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
rm minikube-linux-amd64
