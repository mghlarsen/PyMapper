# -*- coding: utf-8 -*-

## Copyright 2010 Michael Larsen <mike.gh.larsen@gmail.com>
##
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

from __future__ import with_statement
from contextlib import contextmanager
import atexit
import sqlite3
import osm
import osm.node
import osm.way
import osm.relation

DATABASE_FILE_NAME = "osm.db"
DATABASE_USE_MEMORY = True

_connection = None
if DATABASE_USE_MEMORY:
    _connection = sqlite3.connect(":memory:")
else:
    _connection = sqlite3.connect(DATABASE_FILE_NAME)

atexit.register(_connection.close)

@contextmanager
def _trans(conn):
    cursor = conn.cursor()
    try:
        yield cursor
    except:
        conn.rollback()
        raise
    else:
        conn.commit()

_create_sql = 'CREATE TABLE IF NOT EXISTS %s (%s);'

_create_osm_tag_sql = _create_sql % ('osm_tag',
 'id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT, value TEXT, \
  UNIQUE(key,value)')

_create_osm_node_sql = _create_sql % ('osm_node',
  'id INTEGER PRIMARY KEY, lat REAL, lon REAL, version INTEGER, \
   timestamp TEXT, changeset INTEGER, uid INTEGER, user TEXT')

_create_osm_node_tag_sql = _create_sql % ('osm_node_tag',
  'nid INTEGER NOT NULL,\
   tid INTEGER NOT NULL,\
   FOREIGN KEY (nid) REFERENCES osm_node (id),\
   FOREIGN KEY (tid) REFERENCES osm_tag (id)')

_create_osm_way_sql = _create_sql % ('osm_way',
  'id INTEGER PRIMARY KEY, version INTEGER, timestamp TEXT,\
   changeset INTEGER, uid INTEGER, user TEXT')

_create_osm_way_tag_sql = _create_sql % ('osm_way_tag',
  'wid INTEGER NOT NULL, tid INTEGER NOT NULL,\
   FOREIGN KEY (wid) REFERENCES osm_way (id),\
   FOREIGN KEY (tid) REFERENCES osm_tag (id)')

_create_osm_way_node_sql = _create_sql % ('osm_way_node',
  'wid INTEGER NOT NULL, seq INTEGER NOT NULL,\
   nid INTEGER NOT NULL, UNIQUE(wid, seq),\
   FOREIGN KEY (wid) REFERENCES osm_way (id),\
   FOREIGN KEY (nid) REFERENCES osm_node (id)')

_create_osm_relation_sql = _create_sql % ('osm_relation',
 'id INTEGER PRIMARY KEY, version INTEGER, timestamp TEXT, \
  changeset INTEGER, uid INTEGER, user TEXT')

_create_osm_relation_tag_sql = _create_sql % ('osm_relation_tag',
 'rid INTEGER NOT NULL, tid INTEGER NOT NULL, \
  FOREIGN KEY (rid) REFERENCES osm_relation (id), \
  FOREIGN KEY (tid) REFERENCES osm_tag (id)')

_create_osm_relation_member_sql = _create_sql % ('osm_relation_member',
 'rid INTEGER NOT NULL, seq INTEGER NOT NULL, role TEXT,\
  type TEXT NOT NULL, ref INTEGER NOT NULL, UNIQUE(rid, seq),\
  FOREIGN KEY (rid) REFERENCES osm_relation (id)')

_create_osm_map_sql = _create_sql % ('osm_map',
 'id INTEGER PRIMARY KEY, minlat REAL, maxlat REAL, minlon REAL, maxlon REAL\
  CHECK (minlat <= maxlat), CHECK (minlon <= maxlon);')

with _trans(_connection) as cursor:
    cursor.execute(_create_osm_tag_sql)
    cursor.execute(_create_osm_node_sql)
    cursor.execute(_create_osm_node_tag_sql)
    cursor.execute(_create_osm_way_sql)
    cursor.execute(_create_osm_way_tag_sql)
    cursor.execute(_create_osm_way_node_sql)
    cursor.execute(_create_osm_relation_sql)
    cursor.execute(_create_osm_relation_tag_sql)
    cursor.execute(_create_osm_relation_member_sql)
    cursor.execute(_create_osm_map_sql)

def _insert_sql(table, fields):
    sql = 'INSERT OR REPLACE INTO %s (%s) VALUES (%s)'
    blanks = ['?',] * len(fields)
    return sql % (table, ','.join(fields), ','.join(blanks))

def _select_sql(tables, results, conditions = None):
    sql = 'SELECT %(resultsTxt)s FROM %(tablesTxt)s WHERE %(conditionsTxt)s;'
    sql_nowhere = 'SELECT %(resultsTxt)s FROM %(tablesTxt)s;'
    tablesTxt = None
    if isinstance(tables, str):
        tablesTxt = tables
    else:
        tablesTxt = ', '.join(tables)
    resultsTxt = None
    if isinstance(results, str):
        resultsTxt = results
    else:
        resultsTxt = ', '.join(results)
    conditionsTxt = None
    if isinstance(conditions, str):
        conditionsTxt = conditions
    elif not conditions:
        return sql_nowhere % locals()
    else:
        conditionsTxt = ' AND '.join(conditions)
    return sql % locals()

def _getTagID(cursor, key, value):
    select_sql = _select_sql('osm_tag', 'id', ('key = ?', 'value = ?'))
    insert_sql = _insert_sql('osm_tag', ('key', 'value'))
    cursor.execute(select_sql, (key, value))
    idTuple = cursor.fetchone()
    if idTuple == None:
        cursor.execute(insert_sql, (key, value))
        cursor.execute(select_sql, (key, value))
        idTuple = cursor.fetchone()
    return idTuple[0]

def node_store(node):
    insert_sql = _insert_sql('osm_node', node_fields)
    tag_insert_sql = _insert_sql('osm_node_tag', ('nid', 'tid'))
    with _trans(_connection) as c:
        c.execute(insert_sql, node.insert_tuple())
        for i in node.tags.items():
            c.execute(tag_insert_sql, (node.id, _getTagID(c, *i)))

def node_marshall(id, fields):
    select_tag_sql = _select_sql('osm_node_tag INNER JOIN osm_tag ON tid = id', ('key', 'value'), 'nid = ?')
    with _trans(_connection) as c:
        tagDict = dict()
        c.execute(select_tag_sql, (id,))
        for key, value in c:
            tagDict[key] = value
        return osm.Node(id, fields, tagDict)

def node_retrieve(id):
    select_sql = _select_sql('osm_node', node_fields[1:], 'id = ?')
    with _trans(_connection) as c:
        c.execute(select_sql, (id,))
        fields = c.fetchone()
        return node_marshall(id, fields)

def node_count():
    cursor = _connection.execute(select_sql('osm_node', 'COUNT(id)'))
    res = cursor.fetchone()
    return res[0]

def node_exists(id):
    cursor = _connection.execute(_select_sql('osm_node', 'COUNT(id)', 'id = ?'), (id,))
    res = cursor.fetchone()
    return res[0] > 0

def node_iter():
    cursor = _connection.execute(_select_sql('osm_node', node_fields))
    return (node_marshall(fields[0], fields[1:]) for fields in cursor)

def way_store(way):
    insert_sql = _insert_sql('osm_way', way_fields)
    tag_insert_sql = _insert_sql('osm_way_tag', ('wid', 'tid'))
    node_insert_sql = _insert_sql('osm_way_node', ('wid', 'seq', 'nid'))
    with _trans(_connection) as c:
        c.execute(insert_sql, way.insert_tuple())
        for i in way.tags.items():
            c.execute(tag_insert_sql, (way.id, _getTagID(c, *i)))
        for i in xrange(len(way.nodes)):
            c.execute(node_insert_sql, (way.id, i, way.nodes[i]))

def way_marshall(id, fields):
    select_tag_sql = _select_sql('osm_way_tag INNER JOIN osm_tag ON tid = id', ('key', 'value'), 'wid = ?')
    select_node_sql = _select_sql('osm_way_node', 'nid', 'wid = ? ORDER BY seq ASC')
    with _trans(_connection) as c:
        tagDict = dict()
        c.execute(select_tag_sql, (id,))
        for key, value in c:
            tagDict[key] = value
        c.execute(select_node_sql, (id,))
        nodeList = (row[0] for row in c)
        return osm.Way(id, fields, tagDict, nodeList)

def way_retrieve(id):
    select_sql = _select_sql('osm_way', way_fields[1:], 'id = ?')
    with _trans(_connection) as c:
        c.execute(select_sql, (id,))
        fields = c.fetchone()
        return way_marshall(id, fields)

def way_count():
    cursor = _connection.execute(select_sql('osm_way', 'COUNT(id)'))
    res = cursor.fetchone()
    return res[0]

def way_exists(id):
    cursor = _connection.execute(_select_sql('osm_way', 'COUNT(id)', 'id = ?'), (id,))
    res = cursor.fetchone()
    return res[0] > 0

def way_iter():
    cursor = _connection.execute(_select_sql('osm_way', node_fields))
    return (way_marshall(fields[0], fields[1:]) for fields in cursor)

def relation_store(relation):
    insert_sql = _insert_sql('osm_relation', relation_fields)
    tag_insert_sql = _insert_sql('osm_relation_tag', ('rid', 'tid'))
    member_insert_sql = _insert_sql('osm_relation_member', ('rid', 'seq', 'role', type, ref))
    with _trans(_connection) as c:
        c.execute(insert_sql, relation.insert_tuple())
        for i in relation.tags.items():
            c.execute(tag_insert_sql, (relation.id, _getTagID(c, *i)))
        for i in xrange(len(relation.members)):
            mem = relation.members[i]
            c.execute(member_insert_sql, (relation.id, i, mem.role, mem.type, mem.ref))

def relation_marshall(id, fields):
    select_tag_sql = _select_sql('osm_relation_tag INNER JOIN osm_tag ON tid = id', ('key', 'value'), 'rid = ?')
    select_member_sql = _select_sql('osm_relation_member', ('role', 'type', 'ref'), 'rid = ? ORDER BY seq ASC')
    with _trans(_connection) as c:
        tagDict = dict()
        c.execute(select_tag_sql, (id,))
        for key, value in c:
            tagDict[key] = value
        c.execute(select_member_sql, (id,))
        m = (row[0] for row in c)
        return osm.Relation(id, fields, tagDict, m)


def relation_retrieve(id):
    select_sql = _select_sql('osm_relation', relation_fields[1:], 'id = ?')
    with _trans(_connection) as c:
        c.execute(select_sql, (id,))
        fields = c.fetchone()
        return relation_marshall(id, fields)

def relation_count():
    cursor = _connection.execute(select_sql('osm_relation', 'COUNT(id)'))
    res = cursor.fetchone()
    return res[0]

def relation_exists(id):
    cursor = _connection.execute(_select_sql('osm_relation', 'COUNT(id)', 'id = ?'), (id,))
    res = cursor.fetchone()
    return res[0] > 0

def relation_iter():
    cursor = _connection.execute(_select_sql('osm_relation', node_fields))
    return (relation_marshall(fields[0], fields[1:]) for fields in cursor)

def map_store(minlat, maxlat, minlon, maxlon):
    insert_sql = _insert_sql('osm_map', ('minlat', 'maxlat', 'minlon', 'maxlon'))
    _connection.execute(insert_sql, (minlat, maxlat, minlon, maxlon))

def check_in_map(lat, lon):
    select_sql('osm_map', ('id'), ('minlat <= ?', 'minlon <= ?', 'maxlat >= ?', 'maxlon >= ?'))
    cursor = _connection.execute(select_sql)
    res = cursor.fetchone()
    return res != None

def node_way_retrieve(id):
    select_sql = _select_sql('osm_way_node', ('wid'), 'nid = ?')
    with _trans(_connection) as c:
        c.execute(select_sql, (id,))
        return (r[0] for r in c)

def map_node_count():
    cursor = _connection.execute(select_sql(('osm_node', 'osm_map'), 'COUNT(osm_node.id)', 
                                    ('lat >= minlat', 'lat <= maxlat',
                                     'lon >= minlon', 'lon <= maxlon')))
    res = cursor.fetchone()
    return res[0]

def map_node_exists(id):
    cursor = _connection.execute(select_sql(('osm_node', 'osm_map'), 'COUNT(osm_node.id)',
                ('lat >= minlat', 'lat <= maxlat','lon >= minlon', 
                 'lon <= maxlon', 'osm_node.id = ?')), (id,))
    cursor = _connection.execute(_select_sql('osm_node', 'COUNT(id)', 'id = ?'), (id,))
    res = cursor.fetchone()
    return res[0] > 0

def data_store(dataList):
    for item in dataList:
        if isinstance(item, osm.Node):
            node_store(item)
        elif isinstance(item, osm.Way):
            way_store(item)
        elif isinstance(item, osm.Relation):
            relation_store(item)
