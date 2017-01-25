from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import func, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.hybrid import hybrid_property

import sqlite3, re

class NotAuthenticated(Exception):
    """ Raised in case of 401 error:
        user needs to authenticate themself before performing the operation
    """
    pass

class NotAuthorized(Exception):
    """ Raised in case of 403 error:
        the operation is forbidden for currently authenticated user
    """
    pass

class NotFound(Exception):
    """ Raised in case of 404 error:
        an item couldn't be found
    """
    pass

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
        """ Retrieve User entry by given email;
        return `None` or an object
        """
        return session.query(cls).filter_by(email=email).first()

    @classmethod
    def create(cls, email, username, picture):
        """ Create a new User entry and return it;
        if entry with given email already exists, just return it
        """
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

    # `path` is a URI-compatible version of `title` property
    @hybrid_property
    def path(self):
        return latin_lower(self.title)

    @path.expression
    def path(cls):
        return func.latin_lower(cls.title)

    # the first symbol of the `title` by default,
    # but an empty string if `image` is not empty
    @property
    def initial(self):
        if not self.image:
            return self.title[:1]
        else:
            return ''

    # JSON representation of the entry, with decorative properties left out
    @property
    def serialized(self):
        obj = {
            'id': self.id,
            'title': self.title,
            'path': self.path
        }
        return obj

    @classmethod
    def add_all(cls, obj):
        """ Create Category entries by given list """
        for item in obj:
            category = cls(**item)
            session.add(category)

        session.commit()

    @classmethod
    def get_all(cls):
        """ Get all entries """
        categories = session.query(cls).all()

        return categories

    @classmethod
    def get_one(cls, path):
        """ Retrieve one entry by given `path`;
        error is raised if nothing is found
        """
        existing = session.query(cls).filter(cls.path==path).first()
        if not existing:
            raise NotFound

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

    # `label` is URI-compatible version of `title` property
    @hybrid_property
    def label(self):
        return latin_lower(self.title)

    @label.expression
    def label(cls):
        return func.latin_lower(cls.title)

    # the first letter of the `text` property
    @property
    def initial(self):
        return self.text[:1]

    # JSON representation of the entry
    @property
    def serialized(self):
        obj = {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'source': self.source,
            'image': self.image,
            'text': self.text
        }
        return obj

    @classmethod
    def add(cls, user, category, item):
        """ Add `user` and `category` properties to given Item entry
        and save it to db;
        `category` is expected to be a valid Category entry;
        `user` might be missing, an exception is raised in that case;
        properties of Item entry are checked before saving

        return non-empty string if some properties are invalid, `None` otherwise
        """
        if user:
            item.user = user
        else:
            raise NotAuthenticated

        count = cls.count(category, item.label)
        if count:
            return 'An article with similar title already exists'

        if item.label == 'add':
            return 'Title can\'t be "add" or alike'

        item.category = category
        session.add(item)
        session.commit()

        return None

    @classmethod
    def query(cls, category, label=None):
        """ Construct `query` object filtered by given Category entry,
        and optionally by `label` value
        """
        result = session.query(cls).filter(cls.category==category)
        if label:
            result = result.filter(cls.label==label)

        return result

    @classmethod
    def get_all(cls, category):
        """ Get all entries by the given Category entry """
        return cls.query(category).all()

    @classmethod
    def get_one(cls, category, label):
        """ Get one entry filtered by given Category entry and `label`;
        error is raised if nothing is found
        """
        existing = cls.query(category, label).first()
        if not existing:
            raise NotFound

        return existing

    @classmethod
    def count(cls, category, label=None):
        """ Count entries with given Category entry and `label` """
        return cls.query(category, label).count()

    def delete(self, user):
        """ Delete current entry from db.
        `user` parameter defines on whom behalf this operation is attempted.

        `self.user` and `user` parameter must match to finish the operation,
        otherwise exception will be raised
        """
        if not user:
            raise NotAuthenticated

        if self.user != user:
            raise NotAuthorized

        session.delete(self)

    def edit(self, user, obj):
        """ Edit current entry in db.
        `user` parameter defines on whom behalf this operation is attempted;
        `obj` represents required changes.

        `self.user` and `user` parameter must match to finish the operation,
        otherwise exception will be raised;
        `obj` is inspected before applying any changes,
        if one of it's properties is invalid, an error string returned

        return values are `None` or a non-empty error string
        """
        if not user:
            raise NotAuthenticated

        if self.user != user:
            raise NotAuthorized

        future_label = latin_lower(obj['title'])
        if future_label != self.label:

            count = Item.count(self.category, future_label)
            if count:
                session.rollback()
                return 'An article with similar title already exists'

            if future_label == 'add':
                session.rollback()
                return 'Title can\'t be "add" or alike'

        self.title = obj['title']
        self.author = obj['author']
        self.source = obj['source']
        self.image = obj['image']
        self.text = obj['text']

        session.commit()

        return None

engine = create_engine('sqlite://', creator=engine_creator)

Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()
