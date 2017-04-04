# Material Design Resource Catalog

This project is a part of Udacity Full-Stack Developer Nanodegree.

It presents an application that provides a list of items
(demonstrational resources related to Material Design in this case)
within a variety of categories as well as provide a user registration
(via Google+ and Facebook oAuth2) and authentication system.

Registered users have an ability to post, edit and delete their items.

This work is a RESTful web application built on Python framework Flask
and SQLAlchemy ORM.


### Installation

Assuming Ubuntu is used:

1. Install Flask, PostgreSQL with its PL/Python extension, SQLAlchemy, and pip:
  ```
  sudo apt-get -qqy update &&
  sudo apt-get -qqy upgrade &&
  sudo apt-get -qqy install postgresql python-psycopg2 postgresql-plpython &&
  sudo apt-get -qqy install python-flask python-sqlalchemy &&
  sudo apt-get -qqy install python-pip
  ```

2. Required pip packages:
  ```
  sudo pip install bleach &&
  sudo pip install oauth2client &&
  sudo pip install requests &&
  sudo pip install httplib2 &&
  sudo pip install redis &&
  sudo pip install passlib &&
  sudo pip install itsdangerous &&
  sudo pip install flask-httpauth
  ```

3. After copying files to the server, create a database and populate it:
  ```
  sudo su postgres
  psql

  CREATE USER catalog WITH PASSWORD 'password';
  CREATE DATABASE catalog;

  \c catalog

  GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO catalog;
  CREATE EXTENSION plpythonu;
  UPDATE pg_language SET lanpltrusted = true WHERE lanname = 'plpythonu';
  \q
  exit
  ```

  `./populate_db.py`

  alternatively, if some items are also required:

  `./populate_db.py -i`

4. Create `config.py` file with the content:
  ```python
  DEBUG = True # or False for production
  SECRET_KEY = 'a-secret-key-of-your-choice-here'
  ```

5. Create files `g_client_secrets.json`(must be generated and downloaded from [Google Developer's Console](https://console.developers.google.com))
and `fb_client_secrets.json`(generate credentials at [Facebook for Developers](https://developers.facebook.com/)).

  ```
  nano fb_client_secrets.json
  {
    "web": {
      "app_id": "your-app-id",
      "app_secret": "your-app-secret"
    }
  }
  ```

6. Run the project:

  `python project.py`

### License

Anton Kachurin, 2017, [Apache License v2.0](http://www.apache.org/licenses/LICENSE-2.0)

### Credits

[Material design alphabet](http://mougino.free.fr/material/)

Icon pack by [Jurre Houtkamp](https://dribbble.com/jurrehoutkamp)

[Material design icons](https://www.materialpalette.com/icons)
