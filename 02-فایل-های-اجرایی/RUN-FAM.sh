#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
sudo docker load -i fam-docker-images.tar
sudo docker compose up -d
sudo docker compose ps
