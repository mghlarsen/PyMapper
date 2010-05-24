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

import unittest
import osm
osm.OSM_CONFIG_FILE_DEFAULT = "osm-test.cfg"
import osm.data

state = dict()

def setup():
    pass

def testNode():
    n = osm.data.node_get(42444081)
    assert n.id == 42444081
    assert len(n.get_adjacent()) == 3
    assert len(n.ways) == 2

def testWay():
    w = osm.data.way_get(5671196)
    assert w.id == 5671196
    assert w.nodes[0].id == 42442734
    assert w.nodes[1].id == 42444060
    assert w.nodes[2].id == 42433066
    assert w.nodes[3].id == 42444069
    assert w.nodes[4].id == 42429029
    assert w.nodes[5].id == 42444081
    assert w.nodes[6].id == 42430951
    assert w.nodes[7].id == 42427190

def testRelation():
    r = osm.data.relation_get(161599)
    assert r.members[0].ref == 9702602
    assert r.members[0].role == "south"
    assert r.members[0].type == "way"

