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
"""
This module is responsible for caching the OpenStreetMap.org data in a sqlite
database.

This registers an atexit hook to close the sqlite database connection.
Setting osm.DATABASE_FILE_NAME will change the database filename used.
Setting osm.DATABASE_USE_MEMORY will make the database be in-memory.

This requires with_statement to be available (at least in __future__ i.e.
Python 2.5 or later), as well as contextlib and sqlite3.
"""

from __future__ import with_statement
from contextlib import contextmanager
import atexit
import sqlite3
import osm
import osm.node
import osm.way
import osm.relation


_connection = None
if osm.config.get('osm','db-use-memory'):
    _connection = sqlite3.connect(":memory:")
else:
    _connection = sqlite3.connect(osm.config.get('osm', 'db-filename'))

atexit.register(_connection.close)

@contextmanager
def _trans(conn):
    """
    This is a context manager that makes sqlite3 operations in a transaction.
    Only included because sqlite3 doesn't have its own until Python 2.6.
    """
    cursor = conn.cursor()
    try:
        yield cursor
    except:
        conn.rollback()
        raise
    else:
        conn.commit()

# Basic SQL CREATE TABLE syntax template
_create_sql = 'CREATE TABLE IF NOT EXISTS %s (%s);'

# SQL to create osm_tag
# This table holds all the tag key:value pairs
_create_osm_tag_sql = _create_sql % ('osm_tag',
 'id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT, value TEXT, \
  UNIQUE(key,value)')

# SQL to create osm_node
# This holds the basic Node data
_create_osm_node_sql = _create_sql % ('osm_node',
  'id INTEGER PRIMARY KEY, lat REAL, lon REAL, version INTEGER, \
   timestamp TEXT, changeset INTEGER, uid INTEGER, user TEXT')

# SQL to create osm_node_tag
# This holds the mapping between Nodes and what Tag key:value pairs they have.
_create_osm_node_tag_sql = _create_sql % ('osm_node_tag',
  'nid INTEGER NOT NULL,\
   tid INTEGER NOT NULL,\
   FOREIGN KEY (nid) REFERENCES osm_node (id),\
   FOREIGN KEY (tid) REFERENCES osm_tag (id)')

# SQL to create osm_way
# This holds the basic Way data.
_create_osm_way_sql = _create_sql % ('osm_way',
  'id INTEGER PRIMARY KEY, version INTEGER, timestamp TEXT,\
   changeset INTEGER, uid INTEGER, user TEXT')

# SQL to create osm_way_tag
# This holds the mapping between Ways and what Tag key:value pairs they have.
_create_osm_way_tag_sql = _create_sql % ('osm_way_tag',
  'wid INTEGER NOT NULL, tid INTEGER NOT NULL,\
   FOREIGN KEY (wid) REFERENCES osm_way (id),\
   FOREIGN KEY (tid) REFERENCES osm_tag (id)')

# SQL to create osm_way_node
# This holds the mappings between Ways and what Nodes they contain (and their
# order).
_create_osm_way_node_sql = _create_sql % ('osm_way_node',
  'wid INTEGER NOT NULL, seq INTEGER NOT NULL,\
   nid INTEGER NOT NULL, UNIQUE(wid, seq),\
   FOREIGN KEY (wid) REFERENCES osm_way (id),\
   FOREIGN KEY (nid) REFERENCES osm_node (id)')

# SQL to create osm_relation
# This holds the basic Relation data.
_create_osm_relation_sql = _create_sql % ('osm_relation',
 'id INTEGER PRIMARY KEY, version INTEGER, timestamp TEXT, \
  changeset INTEGER, uid INTEGER, user TEXT')

# SQL to create osm_relation_tag
# This holds the mapping between Relations and what Tag key:value pairs they have.
_create_osm_relation_tag_sql = _create_sql % ('osm_relation_tag',
 'rid INTEGER NOT NULL, tid INTEGER NOT NULL, \
  FOREIGN KEY (rid) REFERENCES osm_relation (id), \
  FOREIGN KEY (tid) REFERENCES osm_tag (id)')

# SQL to create osm_relation_member
# This holds the mappings between Relations and what members they have (and their
# order).
_create_osm_relation_member_sql = _create_sql % ('osm_relation_member',
 'rid INTEGER NOT NULL, seq INTEGER NOT NULL, role TEXT,\
  type TEXT NOT NULL, ref INTEGER NOT NULL, UNIQUE(rid, seq),\
  FOREIGN KEY (rid) REFERENCES osm_relation (id)')

# SQL to create osm_map
# This holds the table of bounding boxes that have already been fetched.
_create_osm_map_sql = _create_sql % ('osm_map',
 'id INTEGER PRIMARY KEY, minlat REAL, maxlat REAL, minlon REAL, maxlon REAL\
  CHECK (minlat <= maxlat), CHECK (minlon <= maxlon)')

# Initialize all tables
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
    """
    Generate the insert SQL to put data into a row in table in fields.
    Returns the SQL with ?-style blanks.
    """
    sql = 'INSERT OR REPLACE INTO %s (%s) VALUES (%s)'
    blanks = ['?',] * len(fields)
    return sql % (table, ','.join(fields), ','.join(blanks))

def _select_sql(tables, results, conditions = None):
    """
    Generate the select SQL to get results from table with conditions.
    """
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
    """
    Gets the id of the tag with the given key:value pair.
    If it doesn't exist, this creates it.
    """
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
    """
    Store the given Node in the database.
    """
    insert_sql = _insert_sql('osm_node', osm.node.node_fields)
    tag_insert_sql = _insert_sql('osm_node_tag', ('nid', 'tid'))
    with _trans(_connection) as c:
        c.execute(insert_sql, node.insert_tuple())
        for i in node.tags.items():
            c.execute(tag_insert_sql, (node.id, _getTagID(c, *i)))

def node_marshall(id, fields):
    """
    Generate a Node object with id, and fields (as given in Node.__from_data).
    Fetches the required tag data from the database.
    """
    select_tag_sql = _select_sql('osm_node_tag INNER JOIN osm_tag ON tid = id', ('key', 'value'), 'nid = ?')
    with _trans(_connection) as c:
        tagDict = dict()
        c.execute(select_tag_sql, (id,))
        for key, value in c:
            tagDict[key] = value
        return osm.node.Node(id, fields, tagDict)

def node_retrieve(id):
    """
    Retrieve the Node with id from the database.
    Returns the specified Node.
    """
    select_sql = _select_sql('osm_node', osm.node.node_fields[1:], 'id = ?')
    with _trans(_connection) as c:
        c.execute(select_sql, (id,))
        fields = c.fetchone()
        return node_marshall(id, fields)

def node_count():
    """
    Returns the number of nodes stored in the table.
    """
    cursor = _connection.execute(_select_sql('osm_node', 'COUNT(id)'))
    res = cursor.fetchone()
    return res[0]

def node_exists(id):
    """
    Returns true if a node with the given id exists in the database.
    """
    cursor = _connection.execute(_select_sql('osm_node', 'COUNT(id)', 'id = ?'), (id,))
    res = cursor.fetchone()
    return res[0] > 0

def node_iter():
    """
    Return an iterator over all nodes in the database as Node objects.
    """
    cursor = _connection.execute(_select_sql('osm_node', osm.node.node_fields[0]))
    return (fields[0] for fields in cursor)

def way_store(way):
    """
    Stores the given Way object in the database.
    """
    insert_sql = _insert_sql('osm_way', osm.way.way_fields)
    tag_insert_sql = _insert_sql('osm_way_tag', ('wid', 'tid'))
    node_insert_sql = _insert_sql('osm_way_node', ('wid', 'seq', 'nid'))
    with _trans(_connection) as c:
        c.execute(insert_sql, way.insert_tuple())
        for i in way.tags.items():
            c.execute(tag_insert_sql, (way.id, _getTagID(c, *i)))
        for i in xrange(len(way.nodes)):
            c.execute(node_insert_sql, (way.id, i, way.nodes[i]))

def way_marshall(id, fields):
    """
    Returns a Way object with id and fields (as given in Way.__from_data).
    Generates tags and nodes from the database.
    """
    select_tag_sql = _select_sql('osm_way_tag INNER JOIN osm_tag ON tid = id', ('key', 'value'), 'wid = ?')
    select_node_sql = _select_sql('osm_way_node', 'nid', 'wid = ? ORDER BY seq ASC')
    with _trans(_connection) as c:
        tagDict = dict()
        c.execute(select_tag_sql, (id,))
        for key, value in c:
            tagDict[key] = value
        c.execute(select_node_sql, (id,))
        nodeList = [row[0] for row in c]
        return osm.way.Way(id, fields, tagDict, nodeList)

def way_retrieve(id):
    """
    Retrieve a Way object with the given id from the database.
    """
    select_sql = _select_sql('osm_way', osm.way.way_fields[1:], 'id = ?')
    with _trans(_connection) as c:
        c.execute(select_sql, (id,))
        fields = c.fetchone()
        return way_marshall(id, fields)

def way_count():
    """
    Returns the number of ways stored in the database.
    """
    cursor = _connection.execute(_select_sql('osm_way', 'COUNT(id)'))
    res = cursor.fetchone()
    return res[0]

def way_exists(id):
    """
    Returns true if a way with the given id is in the database.
    """
    cursor = _connection.execute(_select_sql('osm_way', 'COUNT(id)', 'id = ?'), (id,))
    res = cursor.fetchone()
    return res[0] > 0

def way_iter():
    """
    Returns an iterator over all the ways in the database of Way objects.
    """
    cursor = _connection.execute(_select_sql('osm_way', osm.way.way_fields[0]))
    return (fields[0] for fields in cursor)

def relation_store(relation):
    """
    Stores the given relation in the database.
    """
    insert_sql = _insert_sql('osm_relation', osm.relation.relation_fields)
    tag_insert_sql = _insert_sql('osm_relation_tag', ('rid', 'tid'))
    member_insert_sql = _insert_sql('osm_relation_member', ('rid', 'seq', 'role', 'type', 'ref'))
    with _trans(_connection) as c:
        c.execute(insert_sql, relation.insert_tuple())
        for i in relation.tags.items():
            c.execute(tag_insert_sql, (relation.id, _getTagID(c, *i)))
        for i in xrange(len(relation.members)):
            mem = relation.members[i]
            c.execute(member_insert_sql, (relation.id, i, mem.role, mem.type, mem.ref))

def relation_marshall(id, fields):
    """
    Creates a Relation with the given id and fields (as given in
    Relation.__from_data). Generates tags and members from the database.
    """
    select_tag_sql = _select_sql('osm_relation_tag INNER JOIN osm_tag ON tid = id', ('key', 'value'), 'rid = ?')
    select_member_sql = _select_sql('osm_relation_member', ('role', 'type', 'ref'), 'rid = ? ORDER BY seq ASC')
    with _trans(_connection) as c:
        tagDict = dict()
        c.execute(select_tag_sql, (id,))
        for key, value in c:
            tagDict[key] = value
        c.execute(select_member_sql, (id,))
        m = [row for row in c]
        return osm.relation.Relation(id, fields, tagDict, m)


def relation_retrieve(id):
    """
    Retrieve the relation with the given id from the database.
    """
    select_sql = _select_sql('osm_relation', osm.relation.relation_fields[1:], 'id = ?')
    with _trans(_connection) as c:
        c.execute(select_sql, (id,))
        fields = c.fetchone()
        return relation_marshall(id, fields)

def relation_count():
    """
    Returns the number of relations stored in the database.
    """
    cursor = _connection.execute(_select_sql('osm_relation', 'COUNT(id)'))
    res = cursor.fetchone()
    return res[0]

def relation_exists(id):
    """
    Returns true if a relation with the given id exists in the database.
    """
    cursor = _connection.execute(_select_sql('osm_relation', 'COUNT(id)', 'id = ?'), (id,))
    res = cursor.fetchone()
    return res[0] > 0

def relation_iter():
    """
    Returns an iterator over all relations in the database as Relations.
    """
    cursor = _connection.execute(_select_sql('osm_relation', osm.relation.relation_fields[0]))
    return (fields[0] for fields in cursor)

def map_store(minlat, maxlat, minlon, maxlon):
    """
    Stores a record that the given bounding box has been fetched.
    """
    insert_sql = _insert_sql('osm_map', ('minlat', 'maxlat', 'minlon', 'maxlon'))
    _connection.execute(insert_sql, (minlat, maxlat, minlon, maxlon))

def check_in_map(lat, lon):
    """
    Returns true if the given (lat, lon) has been fetched.
    """
    select_sql = _select_sql('osm_map', ('id'), ('minlat <= ?', 'minlon <= ?', 'maxlat >= ?', 'maxlon >= ?'))
    cursor = _connection.execute(select_sql, (lat, lon, lat, lon))
    res = cursor.fetchone()
    return res != None

def node_way_retrieve(id):
    """
    Return a list of the id of all ways which include the given node.
    """
    select_sql = _select_sql('osm_way_node', ('wid'), 'nid = ?')
    with _trans(_connection) as c:
        c.execute(select_sql, (id,))
        res = [r[0] for r in c]
        if len(res) == 0 and not map_node_exists(id):
            raise KeyError
        return res

def node_way_iter():
    """
    Return an iterator of (n, [w]) where n is a node, and [w] is a list of the ways
    that include n. 
    """
    select_sql= _select_sql(('osm_node', 'osm_map', 'osm_way_node'), 
                            ('DISTINCT nid',), 
                            ('lat >= minlat', 'lat <= maxlat',
                             'lon >= minlon', 'lon <= maxlon', 
                             'osm_node.id = osm_way_node.nid ORDER BY nid ASC'))
    with _trans(_connection) as c:
        c.execute(select_sql)
        return (r[0] for r in c)

def map_node_count():
    """
    Return the number of nodes that are inside a map bounding box.
    """
    cursor = _connection.execute(_select_sql(('osm_node', 'osm_map'), 'COUNT(osm_node.id)', 
                                    ('lat >= minlat', 'lat <= maxlat',
                                     'lon >= minlon', 'lon <= maxlon')))
    res = cursor.fetchone()
    return res[0]

def map_node_exists(id):
    """
    Return true if the given node is inside of a map bounding box.
    """
    select_sql = """SELECT COUNT(osm_map.id) FROM osm_node, osm_map WHERE 
                    lat >= minlat AND lat <= maxlat AND lon >= minlon AND lon <= maxlon AND osm_node.id = ?;"""
    cursor = _connection.execute(select_sql, (id,))
    res = cursor.fetchone()
    return res[0] > 0

def data_store(dataList):
    """
    Store all Node, Way and Relation objects in dataList in the database.
    """
    for item in dataList:
        if isinstance(item, osm.node.Node):
            node_store(item)
        elif isinstance(item, osm.way.Way):
            way_store(item)
        elif isinstance(item, osm.relation.Relation):
            relation_store(item)

