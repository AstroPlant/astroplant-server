# AstroPlant server
This repository contains the code for the back-end and website of the AstroPlant system.

The AstroPlant kits communicate with the back-end to push data. The website allows users to view the data.

The server is built using the [Django](https://www.djangoproject.com/) framework.

# Documentation

Full documentation can be found [here](https://astroplant-server.readthedocs.io/en/latest/index.html).

# Configuration

The server requires a database to function. It has only been tested with MySQL/MariaDB.

Edit `server/settings.py`.

# Prepare static resources

The static JavaScript and CSS resources have to be prepared prior to running the server.

To do this, ensure npm is installed. Now install the project dependencies. In the root directory of the project, run:

```bash
npm install
```

Next, build the assets to static files:

```bash
npm run-script build
```

# Database

Prepare the database by running:

```bash
python manage.py migrate
```

Note that for development versions (non-release) it might be necessary to perform an additional `makemigrations` step:

```bash
python manage.py makemigrations
python manage.py migrate
```

If you would like to include some default data provided by AstroPlant, such as measurement types and official perihperal device definitions, load the AstroPlant fixture.

```bash
python manage.py loaddata astroplant
```

# Running the server

It is recommended to host the server through a webserver using `server/WSGI.py`, such as Nginx with uWGSI. See also [the AstroPlant server deployment repository](https://github.com/AstroPlant/astroplant-server-deployment).

Alternatively, for development, run the server using:

```bash
python manage.py runserver
```
