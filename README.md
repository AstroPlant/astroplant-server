# AstroPlant server
This repository contains the code for the back-end and website of the AstroPlant
system.

The AstroPlant kits communicate with the back-end to push data.
The website allows users to view the data.

The server is built using the [Django](https://www.djangoproject.com/)
framework.

# Documentation

Full documentation can be found 
[here](https://astroplant-server.readthedocs.io/en/latest/index.html).

# Getting started

Clone the repository and `cd` into it.

This project has runtime dependencies on Python 3.6 and an accessible MySQL
connection.
Node 8 is used at build-time to prepare static resources.
Required Python dependencies are listed in `requirements.txt` and can be
installed with pip:

```shell
$ pip install -r requirements.txt
```

## Nix
Optionally, you can use Nix to emulate a virtual environment (see `shell.nix`):

```shell
$ nix-shell
```

this installs Python 3.6 and Node 8 and makes them available in your shell
environment for the duration of the shell session. It also creates a `_build`
subdirectory and uses it as a virtual Python environment for packages.

## Database

The server requires a database to function.
It has only been tested with MySQL/MariaDB.

### Creating a database:

To create a development database and a local user able to login without a
password perform e.g.:

```shell
$ sudo mysql
> CREATE DATABASE astroplant;
> CREATE USER 'astroplant'@'localhost';
> GRANT ALL PRIVILEGES ON astroplant.* TO 'astroplant'@'localhost';
```

### Configure AstroPlant

If you set a password, or are using a name for the database or user other than
`astroplant`, open `server/settings.py` and configure the `DATABASES` key.

### Prepare the database

There have been no releases yet and as such migrations are not yet kept track
of.

Create the initial migration yourself:

```shell
$ python manage.py makemigrations
```

Prepare the database by running:

```shell
$ python manage.py migrate
```

If you would like to include some default data provided by AstroPlant, such as
measurement types and official peripheral device definitions, load the
AstroPlant fixture.

```shell
$ python manage.py loaddata astroplant
```

## Prepare static resources

The static JavaScript and CSS resources have to be compiled prior to running the
server.

To do this, ensure Node 8 and npm are installed.
Now install the project dependencies--in the root directory of the project, run:

```shell
$ npm install
```

Next, build the assets to static files:

```shell
$ npm run-script build
```

## Run the server

It is recommended to host the server through a webserver using `server/WSGI.py`,
such as Nginx with uWGSI.
See also [the AstroPlant server deployment repository](https://github.com/AstroPlant/astroplant-server-deployment).

Alternatively, for development, run the server using:

```shell
$ python manage.py runserver
```
