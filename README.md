# AI Medical base application

The base of our final year project that we will be working off of later on.

## Prerequisites

The following needs to be installed in order to run the application:
* Python3 
    
    The following versions have been tested: 3.7
* [Docker](https://docs.docker.com/install/)
* [Docker-composer](https://docs.docker.com/compose/install/)

## Deploying the application

The Flask server and all dependencies can be run without having access to the 
code. This is done by using the Docker images stored on our remote Docker 
repository.

Run the following command replacing <path_to_code_checkout>:

`docker-compose -f <path_to_code_checkout>/build/docker-compose.yml up`

Alternatively the docker-compose.yml file can be copied separately from the 
rest of the code checkout, in which case the absolute path to the 
Docker-compose file should be supplied in place of the -f argument.

---

**Note:** 

Our remote Docker repository is at:
https://gitlab.com/comp3931-vulture/base-application/container_registry/

---

## Working on the application

The Flask server can be run using docker-compose by mounting the code checkout 
in the Docker container. Changes to the code are automatically copied into the
deployed Docker containers. This allows developers to work on the application
without having to worry about the environment they are using and any 
dependencies the service has.

Run the following command replacing <path_to_code_checkout>:

`docker-compose -f <path_to_code_checkout>/build/docker-compose-dev.yml up`

## Running the Flask server manually

The Flask server and Celery can be run separately from the dependencies, 
which can be run using Docker-compose.

### Setting up the dev environment

Start the instructions from the same directory as this README.

#### Required packages

The following command must be run to make sure you have all the required 
packages:

`sudo apt-get install redis-server`

#### MongoDB and PostgreSQL

A Docker compose file has been created so that everything required to start the 
application can run from one command.

Make sure Docker and Docker-compose are installed and then run the following 
command replacing <path_to_code_checkout>:

`docker-compose -f <path_to_code_checkout>/build/docker-compose-services.yml up`

Persistent volumes are used to keep the data even if the Docker containers are 
removed.

### Running the web application

Start the instructions from the same directory as this README.

#### Setting up the Python3 virtual environment

A bash shell script has been created to do this for you, however this will 
only work in Unix environments. 
If you are running windows or would prefer to setup the virtual environment 
manually, see the Windows environments section.

##### Unix environments

Run the setup_venv shell script file:

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

---

**Note:** 

The host of the flask server can be specified using the `--host` flag. 
Set this as `0.0.0.0` to use the machines IP address.

--- 

Visit the following URL in your browser:

`http://127.0.0.1:5000/`

#### Start a Celery worker
Start Celery workers to listen to the Redis queue with the following command:

`celery worker -A celery_worker.celery --loglevel=info`

#### Start Celery beat
Start Celery beat for sending scheduled tasks to the Redis queue with the 
following command:

`celery beat -A celery_worker.celery --loglevel=info`

## Removing a Docker-compose deployment

See the Docker-compose CLI docs: https://docs.docker.com/compose/reference/overview/

Use the Docker-compose down command to remove a deployment. 

This might not delete all volumes however. If this is the case you can view 
all volumes manually using `docker volume list` and then delete them 
individually using:
 
`docker volume rm <volume_ids>`

## Creating a super user

You can create a user with admin privileges via the command line using:

`flask cli_admin createsuperuser`

Which will then prompt you to enter a name, email and password.

This user can be used to login to the admin interface at: `<host>/admin`
