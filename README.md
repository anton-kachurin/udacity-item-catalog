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

1. Install Flask, SQLAlchemy, and pip:
  ```
  apt-get -qqy update
  apt-get -qqy install python-flask python-sqlalchemy
  apt-get -qqy install python-pip
  ```

2. Required pip packages:
  ```
  pip install bleach
  pip install oauth2client
  pip install requests
  pip install httplib2
  pip install redis
  pip install passlib
  pip install itsdangerous
  pip install flask-httpauth
  ```
3. After copying files to the server, populate the database with categories:

  `./populate_db.py`

  alternatively, if some items are also required:

  `./populate_db.py -i`

4. Create `config.py` file with the content:
  ```python
  DEBUG = True # or False for production
  SECRET_KEY = 'a-secret-key-of-your-choice-here'
  ```

5. Run the project:

  `python project.py`

### License

Anton Kachurin, 2016, [Apache License v2.0](http://www.apache.org/licenses/LICENSE-2.0)

### Credits

[Material design alphabet](http://mougino.free.fr/material/)

Icon pack by [Jurre Houtkamp](https://dribbble.com/jurrehoutkamp)

[Material design icons](https://www.materialpalette.com/icons)
