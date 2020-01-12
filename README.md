# AI Medical base application

The base of our final year project that we will be working off of later on.
This includes the web and mobile app as well as the server and database.

## Prerequisites

The following needs to be installed in order to run the application:
* Python3
* [Docker](https://docs.docker.com/install/)
* [Docker-composer](https://docs.docker.com/compose/install/)

## Setting up the dev environment

Start the instructions from the same directory as this README.

#### MongoDB and PostgreSQL

A Docker compose file has been created so that everything required to start the 
application can run from one command.

Make sure Docker and Docker-compose are installed and then run the following 
command replacing <path_to_code_checkout>:

`docker-compose -f <path_to_code_checkout>/build/docker-compose-dev.yml up`

Persistent volumes are used to keep the data even if the Docker containers are 
removed.

## Running the web application

Start the instructions from the same directory as this README.

#### Setting up the Python3 virtual environment

A bash shell script has been created to do this for you, however this will 
only work in Unix environments. 
If you are running windows or would prefer to setup the virtual environment 
manually, see the Windows environments section.

##### Unix environments

Run the shell script:

`./build/setup_venv.sh`

##### Windows environments

Create the virtual environment by running the following command in the base 
level project folder:

`python3 -m venv venv`

Activate the virtual environment:

`source venv/bin/activate`

Then install all requirements:

`pip install -r requirements.txt`

#### Start the server

First make sure the virtual environment is activated, if not run:

`source venv/bin/activate`

Make sure your database is up to data with the latest migrations (this must 
be done if your database is new) by running the following command:

`flask db upgrade`

Then start the server:

`flask run --port 5000`

Visit the following URL in your browser:

`http://127.0.0.1:5000/`
