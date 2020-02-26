##########################################################
# Dockerfile to build vulture base-application
# Based on python:3.7-alpine
##########################################################

FROM python:3.7-alpine

# Create a user
RUN adduser -D vulture

# Set working directory to the new user's home directory
WORKDIR /home/vulture

# Install dependencies
RUN echo "@testing http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN \
    apk add --update --no-cache py3-numpy py3-pandas@testing && \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

# Setup Python and install Python requirements
COPY build/requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt --no-cache-dir
RUN venv/bin/pip install gunicorn

RUN apk --purge del .build-deps

# Install app
COPY app app
COPY migrations migrations
COPY base_application.py config.py build/boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP base_application.py

RUN chown -R vulture:vulture ./
USER vulture

# Run app
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]