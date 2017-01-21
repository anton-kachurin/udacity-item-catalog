from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import func, create_engine
from sqlalchemy.ext.hybrid import hybrid_property

import sqlite3
import re

def latin_lower(s):
    """ Convert string to lower case,
    replace all non-latin or non-digit symbols with dashes,
    deduplicate and trim dashes
    """
    result = s.lower()
    result = re.sub("[^a-z0-9]", '-', result)
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
            return None

        return existing

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    author = Column(String(80), nullable=False)
    source = Column(String(1000), nullable=False)
    image = Column(String(1000), nullable=False)
    text = Column(String(10*1024), nullable=False)

    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship(Category)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    @hybrid_property
    def label(self):
        return latin_lower(self.title)

    @label.expression
    def label(cls):
        return func.latin_lower(cls.title)

    @property
    def initial(self):
        return self.text[:1]

    @property
    def serialize(self):
        obj = {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'source': self.source,
            'text': self.text
        }
        return obj

    @classmethod
    def add(cls, user, category, item):
        if user:
            item.user = user
        else:
            # TODO: throw 401 error
            return None

        count = cls.count(category, item.label)
        if count:
            return 'An article with similar title already exists'

        item.category = category
        session.add(item)
        session.commit()

        return None

    @classmethod
    def query(cls, category, label=None):
        result = session.query(cls).filter(cls.category==category)
        if label:
            result = result.filter(cls.label==label)

        return result

    @classmethod
    def get_all(cls, category):
        return cls.query(category).all()

    @classmethod
    def get_one(cls, category, label):
        existing = cls.query(category, label).first()
        if not existing:
            # TODO: throw 404 error
            return None

        return existing

    @classmethod
    def count(cls, category, label=None):
        return cls.query(category, label).count()


engine = create_engine('sqlite://', creator=engine_creator)

Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()
