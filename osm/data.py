from sqlalchemy import Table, Column, Integer, String, Float, DateTime, Binary, MetaData, ForeignKey, create_engine
from sqlalchemy.orm import relation, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import PrimaryKeyConstraint
import osm.api
import osm.parse
import osm.tile

engine = create_engine('sqlite:///osm2.db', echo = False)
Session = sessionmaker(bind = engine)
session = Session()
Base = declarative_base()

node_tags = Table('osm_node_tag', Base.metadata, Column('nid', Integer, ForeignKey('osm_node.id')),
                                                 Column('tid', Integer, ForeignKey('osm_tag.id')))
way_tags = Table('osm_way_tag', Base.metadata, Column('wid', Integer, ForeignKey('osm_way.id')),
                                               Column('tid', Integer, ForeignKey('osm_tag.id')))
relation_tags = Table('osm_relation_tag', Base.metadata, Column('rid', Integer, ForeignKey('osm_relation.id')),
                                                         Column('tid', Integer, ForeignKey('osm_tag.id')))

class WayNode(Base):
    __tablename__ = 'osm_way_node'

    wid = Column(Integer, ForeignKey('osm_way.id'), primary_key = True)
    seq = Column(Integer, primary_key = True)
    nid = Column(Integer, ForeignKey('osm_node.id'))
    

    def __init__(self, wid, seq, nid):
        self.wid = wid
        self.seq = seq
        self.nid = nid

class Member(Base):
    __tablename__ = 'osm_relation_member'
    
    rid = Column(Integer, ForeignKey('osm_relation.id'), primary_key = True)
    seq = Column(Integer, primary_key = True)
    role = Column(String)
    type = Column(String)
    ref = Column(Integer, ForeignKey('osm_node.id'), ForeignKey('osm_way.id'), ForeignKey('osm_relation.id'))

    def __init__(self, rid, seq, role, type, ref):
        self.rid = rid
        self.seq = seq
        self.role = role
        self.type = type
        self.ref = ref

class Tag(Base):
    __tablename__ = 'osm_tag'

    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)

    def __init__(self, key, value):
        self.key = key
        self.value = value

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
    tags = relation('Tag', secondary = relation_tags, backref = 'osm_relation')

    def __init__(self, id, version, changeset, uid, user, tags, members):
        self.id = id
        self.version = version
        self.changeset = changeset
        self.uid = uid
        self.user = user
        self.members = members
        self.tags = tags

class Bounds(Base):
    __tablename__ = 'osm_map_bounds'

    id = Column(Integer, primary_key = True)
    timestamp = Column(DateTime)
    minlat = Column(Float)
    maxlat = Column(Float)
    minlon = Column(Float)
    maxlon = Column(Float)

    def __init__(self, timestamp, minlat, maxlat, minlon, maxlon):
        self.timestamp = timestamp
        self.minlat = minlat
        self.maxlat = maxlat
        self.minlon = minlon
        self.maxlon = maxlon

class Tile(Base):
    __tablename__ = 'osm_map_tile'

    zoom = Column(Integer, primary_key = True)
    x = Column(Integer, primary_key = True)
    y = Column(Integer, primary_key = True)
    pngFilename = Column(String)

    def __init__(self, zoom, x, y, pngFilename = None):
        self.zoom = zoom
        self.x = x
        self.y = y
        if pngFilename:
            self.pngFilename = pngFilename
        else:
            self.pngFilename = osm.tile.get_png_filename(x, y, zoom)

    def bounds(self):
        maxLat, minLon = osm.tile.num2deg(self.x, self.y, self.zoom)
        minLat, maxLon = osm.tile.num2deg(self.x + 1, self.y + 1, self.zoom)
        return (minLat, minLon, maxLat, maxLon)

Base.metadata.create_all(engine)

def data_store(data):
    objs = list()
    for d in data:
        o = None
        if d[0] == 'BOUNDS':
            a = d[1]
            o = Bounds(None, float(a['minlat']), float(a['maxlat']), float(a['minlon']), float(a['maxlon']))
        elif d[0] == 'NODE':
            a = d[1]
            o = Node(int(a['id']), float(a['lat']), float(a['lon']),
                     int(a['version']), int(a['changeset']),
                     int(a['uid']), a['user'],
                     [Tag(*tag) for tag in d[2].items()])
            for t in o.tags:
                session.add(t)
        elif d[0] == 'WAY':
            a = d[1]
            o = Way(int(a['id']), int(a['version']), int(a['changeset']),
                    int(a['uid']), a['user'],
                    [Tag(*tag) for tag in d[2].items()],
                    [WayNode(a['id'], i, int(d[3][i])) for i in range(len(d[3]))])
            for t in o.tags:
                session.add(t)
            for wn in o.nodes:
                session.add(wn)
        elif d[0] == 'RELATION':
            a = d[1]
            o = Relation(int(a['id']), int(a['version']), int(a['changeset']),
                         int(a['uid']), a['user'],
                         [Tag(*tag) for tag in d[2].items()],
                         [Member(int(a['id']), i, d[3][i][0], d[3][i][1], int(d[3][i][2])) for i in range(len(d[3]))])
            for t in o.tags:
                session.add(t)
            for m in o.members:
                session.add(m)
        objs.append(o)
        session.add(o)
    return objs

def node_get(target_id):
    res = session.query(Node).filter_by(id=target_id).first()
    if res:
        return res
    xmldata = osm.api.node_get(target_id)
    data = osm.parse.parse(xmldata)
    objs = data_store(data)
    session.commit()
    for o in objs:
        if isinstance(o, osm.data.Node) and o.id == target_id:
            return o
    raise KeyError
 
def way_get(target_id):
    res = session.query(Way).filter_by(id=target_id).first()
    if res:
        return res
    xmldata = osm.api.way_get(target_id)
    data = osm.parse.parse(xmldata)
    objs = data_store(data)
    session.commit()
    for o in objs:
        if isinstance(o, Way) and o.id == target_id:
            return o
    raise KeyError

def relation_get(target_id):
    res = session.query(Relation).filter_by(id=target_id).first()
    if res:
        return res
    xmldata = osm.api.relation_get(target_id)
    data = osm.parse.parse(xmldata)
    objs = data_store(data)
    session.commit()
    for o in objs:
        if isinstance(o, Relation) and o.id == target_id:
            return o
    raise KeyError

def map_fetch(minLat, maxLat, minLon, maxLon):
    xmldata = osm.api.map_get(minLat, maxLat, minLon, maxLon)
    data = osm.parse.parse(xmldata)
    objs = data_store(data)
    session.commit()


