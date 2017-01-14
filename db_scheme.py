from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine


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
    name = Column(String(50), nullable=False)
    label = Column(String(50), nullable=False)
    description = Column(String(500), nullable=False)

    @property
    def serialize(self):
        obj = {
            'id': self.id,
            'name': self.name,
            'label': self.label,
            'description': self.description
        }
        return obj

    @classmethod
    def get_all(cls):
        return session.query(cls).all()

    @classmethod
    def get_one(cls, label):
        pass

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

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()
