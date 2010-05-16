
from sqlalchemy import Table, Column, Integer, String, Float, MetaData, ForeignKey, create_engine
from sqlalchemy.orm import relation, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///osm2.db', echo = True)
Session = sessionmaker(bind = engine)
Base = declarative_base()

node_tags = Table('osm_node_tag', Base.metadata, Column('nid', Integer, ForeignKey('osm_node.id')),
                                                 Column('tid', Integer, ForeignKey('osm_tag.id')))
way_tags = Table('osm_way_tag', Base.metadata, Column('wid', Integer, ForeignKey('osm_way.id')),
                                               Column('tid', Integer, ForeignKey('osm_tag.id')))
relation_tags = Table('osm_relation_tag', Base.metadata, Column('rid', Integer, ForeignKey('osm_relation.id')),
                                                         Column('tid', Integer, ForeignKey('osm_tag.id')))
way_nodes = Table('osm_way_node', Base.metadata, Column('wid', Integer, ForeignKey('osm_way.id')),
                                                 Column('nid', Integer, ForeignKey('osm_node.id')),
                                                 Column('seq', Integer))
relation_members = Table('osm_relation_member', Base.metadata, Column('rid', Integer, ForeignKey('osm_relation.id')),
                                                               Column('seq', Integer),
                                                               Column('ref', Integer, ForeignKey('osm_node.id'),
                                                                                      ForeignKey('osm_way.id'),
                                                                                      ForeignKey('osm_relation.id')))

class Node(Base):
    __tablename__ = 'osm_node'

    id = Column(Integer, primary_key=True)
    lat = Column(Float)
    lon = Column(Float)
    version = Column(Integer)
    changeset = Column(Integer)
    uid = Column(Integer)
    user = Column(String)
    tags = relation('Tag', secondary = node_tags, backref = 'osm_node')

    def __init__(self, id, lat, lon, version, changeset, uid, user, tags):
        self.id = id
        self.lat = lat
        self.lon = lon
        self.version = version
        self.changeset = changeset
        self.uid = uid
        self.user = user
        self.tags = tags

class Way(Base):
    __tablename__ = 'osm_way'

    id = Column(Integer, primary_key = True)
    version = Column(Integer)
    changeset = Column(Integer)
    uid = Column(Integer)
    user = Column(String)
    nodes = relation('Node', secondary = way_nodes, backref = 'osm_node')
    tags = relation('Tag', secondary = way_tags, backref = 'osm_way')

    def __init__(self, id, version, changeset, uid, user, tags, nodes):
        self.id = id
        self.version = version
        self.changeset = changeset
        self.uid = uid
        self.user = user
        self.tags = tags
        self.nodes = nodes

class Relation(Base):
    __tablename__ = 'osm_relation'

    id = Column(Integer, primary_key = True)
    version = Column(Integer)
    changeset = Column(Integer)
    uid = Column(Integer)
    user = Column(String)
    members = relation('Member', secondary = relation_members, backref = 'osm_relation')
    tags = relation('Tag', secondary = relation_tags, backref = 'osm_relation')

    def __init__(self, id, version, changeset, uid, user, members, tags):
        self.id = id
        self.version = version
        self.changeset = changeset
        self.uid = uid
        self.user = user
        self.members = members
        self.tags = tags

class Tag(Base):
    __tablename__ = 'osm_tag'

    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)

    def __init__(self, key, value):
        self.key = key
        self.value = value

Base.metadata.create_all(engine)

