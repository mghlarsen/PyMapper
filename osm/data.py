# -*- coding: utf-8 -*-

## Copyright 2010 Michael Larsen <mike.gh.larsen@gmail.com>              ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, either version 3 of the License, or     ##
## (at your option) any later version.                                   ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
"""
This module handles the storing of data in the database, as well as dynamic
fetching of map data through the osm.api module.
"""


from sqlalchemy import Table, Column, Integer, String, Float, DateTime, Binary, MetaData, ForeignKey, create_engine, and_, or_
from sqlalchemy.orm import relation, sessionmaker
import sqlalchemy.orm.exc
from sqlalchemy.ext.declarative import declarative_base
import osm.config
import osm.api
import osm.parse
import osm.tile

MAP_POINT_RANGE = osm.config.map_point_range()

engine = create_engine(osm.config.db_connect_str(), echo = osm.config.db_echo_on())
Session = sessionmaker(bind = engine)
session = Session(autoflush = True)
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

def WayNode_get(wid, seq, nid, s = session):
    try:
        res = s.query(WayNode).filter_by(wid=wid,seq=seq).one()
        res.nid = nid
        return res
    except sqlalchemy.orm.exc.NoResultFound:
        return WayNode(wid, seq, nid)


class Member(Base):
    __tablename__ = 'osm_relation_member'
    
    rid = Column(Integer, ForeignKey('osm_relation.id'), primary_key = True)
    seq = Column(Integer, primary_key = True)
    role = Column(String)
    type = Column(String)
    ref = Column(Integer)

    def get_ref(self):
        if self.type == 'node':
            return node_get(self.ref)
        if self.type == 'way':
            return way_get(self.ref)
        if self.type == 'relation':
            return relation_get(self.ref)
        print "Unknown reference type: %s" % (self.type,)

    def __init__(self, rid, seq, role, type, ref):
        self.rid = rid
        self.seq = seq
        self.role = role
        self.type = type
        self.ref = ref

def Member_get(rid, seq, role, type, ref, s = session):
    try:
        res = s.query(Member).filter_by(rid = rid, seq = seq).one()
        res.role = role
        res.type = type
        res.ref = ref
        return res
    except sqlalchemy.orm.exc.NoResultFound:
        return Member(rid, seq, role, type, ref)

class Tag(Base):
    __tablename__ = 'osm_tag'

    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)

    def __init__(self, key, value):
        self.key = key
        self.value = value

def Tag_get(k, v, s = session):
    res = s.query(Tag).filter_by(key=k, value=v).first()
    if res == None:
        return Tag(k, v)
    else:
        return res

class Node(Base):
    __tablename__ = 'osm_node'

    id = Column(Integer, primary_key=True)
    lat = Column(Float)
    lon = Column(Float)
    version = Column(Integer)
    changeset = Column(Integer)
    uid = Column(Integer)
    user = Column(String)
    tags = relation(Tag, secondary = node_tags, backref = 'osm_node')
    ways = relation('Way', secondary = WayNode.__table__, order_by = WayNode.wid)

    def in_bounds(self, s = session):
        return s.query(Bounds, Node).filter(and_(Node.id == self.id,
                                                 Bounds.minlat <= Node.lat,
                                                 Bounds.maxlat >= Node.lat,
                                                 Bounds.minlon <= Node.lon,
                                                 Bounds.maxlon >= Node.lon)).count()

    def get_adjacent(self, s = session):
        if not self.in_bounds(s):
            self.do_map_data_fetch()

        waySpots = []
        for way in self.ways:
            if len(waySpots) and waySpots[-1][0] == way:
                continue
            nids = [n.id for n in way.nodes]
            if nids.count(self.id) > 1:
                if nids.count(self.id) > 2:
                    print "Way %d has more than 2 occurences of Node %d." % (way.id, self.id)
                idx1 = nids.index(self.id)
                idx2 = nids[idx1 + 1:].index(self.id) + idx1
                waySpots.append((way, idx1))
                waySpots.append((way, idx2))
            else:
                waySpots.append((way, nids.index(self.id)))
        nodes = []
        for way, idx in waySpots:
            wayLen = len(way.nodes)
            if idx > 0:
                nodes.append((way, -1, way.nodes[idx - 1]))
            if idx + 1 < len(way.nodes):
                nodes.append((way, 1, way.nodes[idx + 1]))
        return nodes

    def do_map_data_fetch(self, s = session):
        map_fetch_point(self.lat, self.lon)
        assert self.in_bounds(s)

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
    tags = relation(Tag, secondary = way_tags, backref = 'osm_way')
    nodes = relation(Node, secondary = WayNode.__table__, order_by = WayNode.seq)
    wn = relation(WayNode)

    def __init__(self, id, version, changeset, uid, user, tags, nodes):
        self.id = id
        self.version = version
        self.changeset = changeset
        self.uid = uid
        self.user = user
        self.tags = tags
        self.wn = nodes


class Relation(Base):
    __tablename__ = 'osm_relation'

    id = Column(Integer, primary_key = True)
    version = Column(Integer)
    changeset = Column(Integer)
    uid = Column(Integer)
    user = Column(String)
    tags = relation(Tag, secondary = relation_tags, backref = 'osm_relation')
    members = relation(Member, order_by = 'osm_relation_member.c.seq')

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

def data_store(data, s = session):
    objs = list()
    for d in data:
        o = None
        if d[0] == 'BOUNDS':
            a = d[1]
            bList = s.query(Bounds).filter_by(minlat = float(a['minlat']),
                                              maxlat = float(a['maxlat']),
                                              minlon = float(a['minlon']),
                                              maxlon = float(a['maxlon'])).all()
            if len(bList):
                o = bList[0]
            else:
                o = Bounds(None, float(a['minlat']), float(a['maxlat']), float(a['minlon']), float(a['maxlon']))
        elif d[0] == 'NODE':
            a = d[1]
            if s.query(Node).filter_by(id = int(a['id'])).count() > 0:
                o = s.query(Node).filter_by(id = int(a['id'])).one()
                o.lat = float(a['lat'])
                o.lon = float(a['lon'])
                o.version = int(a['version'])
                o.changeset = int(a['changeset'])
                o.uid = int(a['uid'])
                o.user = a['user']
                o.tags = [Tag_get(tag[0], tag[1], s) for tag in d[2].items()]
            else:
                o = Node(int(a['id']), float(a['lat']), float(a['lon']),
                         int(a['version']), int(a['changeset']),
                         int(a['uid']), a['user'],
                         [Tag_get(tag[0], tag[1], s) for tag in d[2].items()])
            for t in o.tags:
                s.add(t)
        elif d[0] == 'WAY':
            a = d[1]
            if s.query(Way).filter_by(id = int(a['id'])).count() > 0:
                o = s.query(Way).filter_by(id = int(a['id'])).one()
                o.version = int(a['version'])
                o.changeset = int(a['changeset'])
                o.uid = int(a['uid'])
                o.user = a['user']
                o.tags = [Tag_get(tag[0], tag[1], s) for tag in d[2].items()]
                o.wn = [WayNode_get(a['id'], i, int(d[3][i]), s) for i in range(len(d[3]))]
            else:
                o = Way(int(a['id']), int(a['version']), int(a['changeset']),
                        int(a['uid']), a['user'],
                        [Tag_get(tag[0], tag[1], s) for tag in d[2].items()],
                        [WayNode(a['id'], i, int(d[3][i])) for i in range(len(d[3]))])
            for t in o.tags:
                s.add(t)
            for wn in o.nodes:
                s.add(wn)
        elif d[0] == 'RELATION':
            a = d[1]
            if s.query(Relation).filter_by(id = int(a['id'])).count() > 0:
                o = s.query(Relation).filter_by(id = int(a['id'])).one()
                o.version = int(a['version'])
                o.changeset = int(a['changeset'])
                o.uid = int(a['uid'])
                o.user = a['user']
                o.tags = [Tag_get(tag[0], tag[1], s) for tag in d[2].items()]
                o.members = [Member_get(int(a['id']), i, d[3][i][0], d[3][i][1], int(d[3][i][2]),s) for i in range(len(d[3]))]
            else:
                o = Relation(int(a['id']), int(a['version']), int(a['changeset']),
                            int(a['uid']), a['user'],
                            [Tag_get(tag[0], tag[1], s) for tag in d[2].items()],
                            [Member(int(a['id']), i, d[3][i][0], d[3][i][1], int(d[3][i][2])) for i in range(len(d[3]))])
            for t in o.tags:
                s.add(t)
            for m in o.members:
                s.add(m)
        objs.append(o)
        s.add(o)
    s.commit()
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

def map_fetch_point(lat, lon):
    minlat = lat - MAP_POINT_RANGE
    maxlat = lat + MAP_POINT_RANGE
    minlon = lon - MAP_POINT_RANGE
    maxlon = lon + MAP_POINT_RANGE
    map_fetch(minlat, maxlat, minlon, maxlon)
    
    
def map_fetch(minLat, maxLat, minLon, maxLon):
    s = Session(autoflush = False)
    minLatBounds = and_(Bounds.minlat < minLat, Bounds.maxlat > minLat)
    maxLatBounds = and_(Bounds.minlat < maxLat, Bounds.maxlat > maxLat)
    minLonBounds = and_(Bounds.minlon < minLon, Bounds.maxlon > minLon)
    maxLonBounds = and_(Bounds.minlon < maxLon, Bounds.maxlon > maxLon)

    overlaps = session.query(Bounds).filter(or_(and_(minLatBounds, minLonBounds),
                                                and_(minLatBounds, maxLonBounds),
                                                and_(maxLatBounds, minLonBounds),
                                                and_(maxLatBounds, maxLonBounds))).all()
    newMinLat = minLat
    newMaxLat = maxLat
    newMinLon = minLon
    newMaxLon = maxLon
    for b in overlaps:
        if b.minlat < newMinLat and b.maxlat > newMinLat:
            if b.minlon < newMinLon and b.maxlon > newMinLon:
                if (((b.maxlat - newMinLat) * (newMaxLon - newMinLon)) <=
                    ((b.maxlon - newMinLon) * (newMaxLat - newMinLat))):
                    newMinLat = b.maxlat
                else:
                    newMinLon = b.maxlon
            elif b.minlon < newMaxLon and b.maxlon > newMaxLon:
                if (((b.maxlat - newMinLat) * (newMaxLon - newMinLon)) <=
                    ((newMaxLon - b.minlon) * (newMaxLat - newMinLat))):
                    newMinLat = b.maxlat
                else:
                    newMaxLon = b.minlon
        elif b.minlat < newMaxLat and b.maxlat > newMaxLat:
            if b.minlon < newMinLon and b.maxlon > newMinLon:
                if (((newMaxLat - b.minlat) * (newMaxLon - newMinLon)) <=
                    ((b.maxlon - newMinLon) * (newMaxLat - newMinLat))):
                    newMaxLat = b.minlat
                else:
                    newMinLon = b.maxlon
            elif b.minlon < newMaxLon and b.maxlon > newMaxLon:
                if (((newMaxLat - b.minlat) * (newMaxLon - newMinLon)) <=
                    ((newMaxLon - b.minlon) * (newMaxLat - newMinLat))):
                    newMaxLat = b.minlat
                else:
                    newMaxLon = b.minlon
    minlat = newMinLat
    maxlat = newMaxLat
    minlon = newMinLon
    maxlon = newMaxLon
    xmldata = osm.api.map_get(minLat, maxLat, minLon, maxLon)
    data = osm.parse.parse(xmldata)
    objs = data_store(data, s)
    s.commit()

