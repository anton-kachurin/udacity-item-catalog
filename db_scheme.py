from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine


Base = declarative_base()

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()

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
    brief = Column(String(250), nullable=False)
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
            'brief': self.brief,
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
