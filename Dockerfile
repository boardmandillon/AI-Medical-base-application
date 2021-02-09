##########################################################
# Dockerfile to build vulture base-application
# Based on python:3.7-buster
##########################################################

FROM python:3.7-slim-buster

# Create a user
RUN useradd -ms /bin/bash base-application

# Set working directory to the new user's home directory
WORKDIR /home/base-application

# Install dependencies
RUN apt-get update && apt-get install -y \
    libgtk2.0-dev

# Setup Python and install Python requirements
COPY build/requirements.txt requirements.txt
RUN python3.7 -m venv venv
RUN venv/bin/pip install --upgrade pip wheel setuptools
RUN venv/bin/pip install -r requirements.txt --no-cache-dir
RUN venv/bin/pip install gunicorn

# Install app
COPY app app
COPY migrations migrations
COPY base_application.py config.py build/boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP base_application.py
ENV LOG_TO_STDOUT False

RUN chown -R base-application:base-application ./
USER base-application

# Run app
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]