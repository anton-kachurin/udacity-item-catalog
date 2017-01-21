from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import func, create_engine
from sqlalchemy.ext.hybrid import hybrid_property

import sqlite3
import re

def latin_lower(s):
    """ Convert string to lower case,
    replace all non-latin symbols with dashes,
    deduplicate and trim dashes
    """
    result = s.lower()
    result = re.sub("[^a-z]", '-', result)
    result = re.sub("-+", '-', result)
    result = re.sub("^-", '', result)
    result = re.sub("-$", '', result)

    return result;

def engine_creator():
    con = sqlite3.connect('catalog.db')
    con.create_function("latin_lower", 1, latin_lower)
    return con

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    picture = Column(String(50*1024))

    @classmethod
    def by_email(cls, email):
        return session.query(cls).filter_by(email=email).first()

    @classmethod
    def create(cls, email, username, picture):
        existing = cls.by_email(email)
        if not existing:
            user = cls(username=username, email=email, picture=picture)
            session.add(user)
            session.commit()
            return user
        else:
            return existing

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    image = Column(String(50), nullable=False)
    color = Column(String(6), nullable=False)

    @hybrid_property
    def path(self):
        return latin_lower(self.title)

    @path.expression
    def path(cls):
        return func.latin_lower(cls.title)

    @property
    def initial(self):
        if not self.image:
            return self.title[:1]
        else:
            return ''

    @property
    def serialize(self):
        obj = {
            'id': self.id,
            'title': self.title,
            'path': self.path
        }
        return obj

    @classmethod
    def add_all(cls, obj):
        for item in obj:
            category = cls(**item)
            session.add(category)

        session.commit()

    @classmethod
    def get_all(cls):
        categories = session.query(cls).all()

        return categories

    @classmethod
    def get_one(cls, path):
        existing = session.query(cls).filter(cls.path==path).first()
        if not existing:
            # TODO: throw 404 error
            pass

        return existing

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    label = Column(String(80), nullable=False)
    description = Column(String(1000), nullable=False)
    link = Column(String(1000), nullable=False)

    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship(Category)

    @property
    def serialize(self):
        obj = {
            'id': self.id,
            'name': self.name,
            'label': self.label,
            'description': self.description,
            'link': self.link
        }
        return obj

    @classmethod
    def get_all(cls, category):
        pass

    @classmethod
    def get_one(cls, category, label):
        pass

engine = create_engine('sqlite://', creator=engine_creator)

Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()
