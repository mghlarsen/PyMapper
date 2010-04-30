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
import osm.fetch

state = dict()

def setup():
    state['data'] = osm.fetch.map_get(40.850, 40.851, -73.937, -73.936)


def testStoreNodeRetrieve():
    for d in state['data']:
        if isinstance(d, osm.node.Node):
            assert osm.store.node_exists(d.id)
            assert d.id == osm.store.node_retrieve(d.id).id

def testStoreWayRetrieve():
    for d in state['data']:
        if isinstance(d, osm.way.Way):
            assert osm.store.way_exists(d.id)
            assert d.id == osm.store.way_retrieve(d.id).id

def testStoreRelationRetrieve():
    for d in state['data']:
        if isinstance(d, osm.relation.Relation):
            assert osm.store.relation_exists(d.id)
            assert d.id == osm.store.relation_retrieve(d.id).id

def testNode():
    assert len(osm.nodes) > 0
    for id, node in osm.nodes:
        assert id == node.id
        assert node != None
