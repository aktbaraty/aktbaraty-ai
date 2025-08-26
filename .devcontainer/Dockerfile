FROM mcr.microsoft.com/devcontainers/python:3.11

RUN apt-get update &&     DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends       git-lfs wget curl build-essential cmake       && rm -rf /var/lib/apt/lists/*

RUN git lfs install
WORKDIR /workspaces/aktbaraty-ai
