FROM mcr.microsoft.com/vscode/devcontainers/base:0-ubuntu-18.04

ENV C_FORCE_ROOT=True
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
RUN apt-get update -y
RUN apt install -y systemd python3-pip gnupg2
COPY ./ ./flask_crud_api
WORKDIR ./flask_crud_api
RUN pip3 install wheel
RUN pip3 install -r requirements.txt
checkout
cache restore
RUN mkdir -p .pip_cache
RUN pip3 install --cache-dir .pip_cache -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["/bin/bash", "-c", "./docker.sh"]

