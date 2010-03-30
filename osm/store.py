#!/usr/bin/python
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

from __future__ import print_function
import sqlite3
import osm

DATABASE_FILE_NAME = "osm.db"
DATABASE_USE_MEMORY = True

_connection = None
if DATABASE_USE_MEMORY:
    _connection = sqlite3.connect(":memory:")
else:
    _connection = sqlite3.connect(DATABASE_FILE_NAME)

_cursor = _connection.cursor()

_cursor.execute("""CREATE TABLE IF NOT EXISTS osm_tag
(id INTEGER PRIMARY KEY AUTOINCREMENT,
 key TEXT,
 value TEXT,
 UNIQUE(key, value));""")

_cursor.execute("""CREATE TABLE IF NOT EXISTS osm_node
(id INTEGER PRIMARY KEY,
 lat REAL,
 lon REAL,
 version INTEGER,
 timestamp TEXT,
 changeset INTEGER,
 uid INTEGER,
 user TEXT);""")

_cursor.execute("""CREATE TABLE IF NOT EXISTS osm_node_tag 
 (nid INTEGER NOT NULL,
  tid INTEGER NOT NULL,
  FOREIGN KEY (nid) REFERENCES osm_node (id),
  FOREIGN KEY (tid) REFERENCES osm_tag (id));""")

_cursor.execute("""CREATE TABLE IF NOT EXISTS osm_way
 (id INTEGER PRIMARY KEY,
 version INTEGER,
 timestamp TEXT,
 changeset INTEGER,
 uid INTEGER,
 user TEXT);""")

_cursor.execute("""CREATE TABLE IF NOT EXISTS osm_way_tag 
 (wid INTEGER NOT NULL,
  tid INTEGER NOT NULL,
  FOREIGN KEY (wid) REFERENCES osm_way (id),
  FOREIGN KEY (tid) REFERENCES osm_tag (id));""")

_cursor.execute("""CREATE TABLE IF NOT EXISTS osm_way_node
 (wid INTEGER NOT NULL,
  seq INTEGER NOT NULL,
  nid INTEGER NOT NULL,
  FOREIGN KEY (wid) REFERENCES osm_way (id),
  FOREIGN KEY (nid) REFERENCES osm_node (id),
  UNIQUE(wid, seq));""")

_cursor.execute("""CREATE TABLE IF NOT EXISTS osm_relation
 (id INTEGER PRIMARY KEY,
  version INTEGER,
  timestamp TEXT,
  changeset INTEGER,
  uid INTEGER,
  user TEXT);""")

_cursor.execute("""CREATE TABLE IF NOT EXISTS osm_relation_tag 
 (rid INTEGER NOT NULL,
  tid INTEGER NOT NULL,
  FOREIGN KEY (rid) REFERENCES osm_relation (id),
  FOREIGN KEY (tid) REFERENCES osm_tag (id));""")

_cursor.execute("""CREATE TABLE IF NOT EXISTS osm_relation_member
 (rid INTEGER NOT NULL,
  seq INTEGER NOT NULL,
  role TEXT,
  type TEXT NOT NULL,
  ref_node INTEGER,
  ref_way INTEGER,
  ref_relation INTEGER,
  FOREIGN KEY (rid) REFERENCES osm_relation (id),
  UNIQUE(rid, seq)
  FOREIGN KEY (ref_node) REFERENCES osm_node (id),
  FOREIGN KEY (ref_way) REFERENCES osm_way (id),
  FOREIGN KEY (ref_relation) REFERENCES osm_relation (id));""")

def node_store(node):
    _cursor.execute("""INSERT OR REPLACE INTO osm_node 
                       (id, lat, lon, version, timestamp, changeset, uid, user)
                       VALUES (?,?,?,?,?,?,?,?);""",
                    (node.id, node.lat, node.lon, node.version, node.timestamp, node.changeset, node.uid, node.user))
    for i in node.tags.items():
        _cursor.execute("SELECT id from osm_tag WHERE key = ? AND value = ?;", i)
        tagID = _cursor.fetchone()
        if tagID == None:
            _cursor.execute("INSERT INTO osm_tag (key, value) VALUES (?, ?);", i)
            _cursor.execute("SELECT id from osm_tag WHERE key = ? AND value = ?;", i)
            tagID = _cursor.fetchone()
        _cursor.execute("INSERT INTO osm_node_tag (nid, tid) VALUES (?,?);", (node.id, tagID[0]))

def way_store(way):
    _cursor.execute("""INSERT OR REPLACE INTO osm_way 
                       (id, version, timestamp, changeset, uid, user)
                       VALUES (?,?,?,?,?,?)""",
                    (way.id, way.version, way.timestamp, way.changeset, way.uid, way.user))
    for i in way.tags.items():
        _cursor.execute("SELECT id from osm_tag WHERE key = ? AND value = ?;", i)
        tagID = _cursor.fetchone()
        if tagID == None:
            _cursor.execute("INSERT INTO osm_tag (key, value) VALUES (?, ?);", i)
            _cursor.execute("SELECT id from osm_tag WHERE key = ? AND value = ?;", i)
            tagID = _cursor.fetchone()
        _cursor.execute("INSERT INTO osm_way_tag (wid, tid) VALUES (?,?);", (way.id, tagID[0]))
    for i in xrange(len(way.nodes)):
        _cursor.execute("INSERT INTO osm_way_node (wid, seq, nid) VALUES (?,?,?);", (way.id, i, way.nodes[i]))

def relation_store(relation):
    _cursor.execute("""INSERT OR REPLACE INTO osm_relation
                       (id, version, timestamp, changeset, uid, user)
                       VALUES (?,?,?,?,?,?)""",
                    (relation.id, relation.version, relation.timestamp, relation.changeset, relation.uid, relation.user))
    for i in relation.tags.items():
        _cursor.execute("SELECT id from osm_tag WHERE key = ? AND value = ?;", i)
        tagID = _cursor.fetchone()
        if tagID == None:
            _cursor.execute("INSERT INTO osm_tag (key, value) VALUES (?, ?);", i)
            _cursor.execute("SELECT id from osm_tag WHERE key = ? AND value = ?;", i)
            tagID = _cursor.fetchone()
        _cursor.execute("INSERT INTO osm_relation_tag (rid, tid) VALUES (?,?);", (relation.id, tagID[0]))
    for i in xrange(len(relation.members)):
        if relation.members[i].type == "node":
            _cursor.execute("INSERT INTO osm_relation_member (rid, seq, role, type, ref_node) VALUES (?,?,?,'node',?);",
                            (relation.id, i, relation.members[i].role, relation.members[i].ref))
        elif relation.members[i].type == "way":
            _cursor.execute("INSERT INTO osm_relation_member (rid, seq, role, type, ref_way) VALUES (?,?,?,'way',?);",
                            (relation.id, i, relation.members[i].role, relation.members[i].ref))
        elif relation.members[i].type == "relation":
            _cursor.execute("INSERT INTO osm_relation_member (rid, seq, role, type, ref_relation) VALUES (?,?,?,'relation',?);",
                            (relation.id, i, relation.members[i].role, relation.members[i].ref))


def shell():
    buffer = ""
    
    print("Enter your SQL commands to execute in sqlite3.")
    print("Enter a blank line to exit.")
    
    while True:
        line = raw_input()
        if line == "":
            break
        buffer += line
        if sqlite3.complete_statement(buffer):
            try:
                buffer = buffer.strip()
                _cursor.execute(buffer)
                
                if buffer.lstrip().upper().startswith("SELECT"):
                    print(_cursor.fetchall())
            except sqlite3.Error, e:
                print("An error occurred:", e.args[0])
            buffer = ""

    _connection.close()

if __name__ == "__main__":
    from osm.fetch import node_get, way_get, map_get
    node = node_get(42444081)[0]
    print(node)
    node_store(node)
    
    data = map_get(node.lat - 0.001, node.lat + 0.001, node.lon - 0.001, node.lon + 0.001)
    for d in data:
        if isinstance(d, osm.Node):
            node_store(d)
        elif isinstance(d, osm.Way):
            way_store(d)
        elif isinstance(d, osm.Relation):
            relation_store(d)
        else:
            print("Unrecognized")
    
    shell()
