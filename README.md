# AI Medical base application

The base of our final year project that we will be working off of later on.
This includes the web and mobile app as well as the server and database.

## Running the web application

Start the instructions from the same directory as this README.

#### First setup the Python3 virtual environment

Create the virtual environment by running the following command in the base level project folder:
`python3 -m venv venv`

Activate the virtual environment:
`source venv/bin/activate`

Then install all requirements:
`pip install -r requirements.txt`

#### Then run the server

`flask run --port 5000`

Visit the following URL in your browser:
`http://127.0.0.1:5000/`
