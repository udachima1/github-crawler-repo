FROM python:3.8-slim-buster
LABEL name=innersource-crawler
LABEL version=1.0.0

WORKDIR /action/workspace
COPY requirements.txt

RUN python3 -m pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt \
    && apt-get -y update \
    && apt-get -y install --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
    
COPY src/ .

EXPOSE 5000

ENV GH_TOKEN=ghp-OdQJ71GTjhwoihfh99289Hzme
ENV TOPIC=inner-source
ENV ORGANIZATION=myorg-innersource

CMD ["/action/workspace/crawler.py"]
ENTRYPOINT ["python", "-u"]

# To run interactive debug on the docker container
# 1. Comment out the above CMD and ENTRYPOINT
# 2. Uncomment the ENTRYPOINT line below

# ENTRYPOINT ["bash"]
