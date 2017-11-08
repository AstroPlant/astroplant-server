# AstroPlant server
This repository contains the code for the back-end and website of the AstroPlant system.

The AstroPlant kits communicate with the back-end to push data. The website allows users to view the data.

The server is built using the [Django](https://www.djangoproject.com/) framework.

# Configuration

The server requires a database to function. It has only been tested with MySQL/MariaDB.

Edit `server/settings.py`.

# Prepare static resources

The static javascript and css resources have to be prepared prior to running the server.

To do this, ensure npm is installed. Now install the project dependencies. In the root directory of the project, run:

```
npm install
```

Next, build the assets to static files:

```
npm run-script build
```

# Running the server

It is recommended to host the server through a webserver using `server/WSGI.py`, such as Nginx with uWGSI.

Alternatively, for development, run the server using:

```
> python manage.py runserver
```
