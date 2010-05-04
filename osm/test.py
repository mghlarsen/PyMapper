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

def testNode():
    assert len(osm.nodes) > 0
    for id, node in osm.nodes.items():
        assert id == node.id
        assert node != None
        assert osm.nodes[id] == node
    assert 42427190 in osm.nodes
    assert not 42431626 in osm.nodes
    fetched = osm.nodes[42431626]
    assert fetched.id == 42431626
    assert 42431626 in osm.nodes
    assert isinstance(fetched.__repr__(), str)
    assert osm.nodes[42427190] < osm.nodes[42431626]
    tampered = osm.store.node_retrieve(42431626)
    tampered.version = tampered.version + 1
    assert tampered > fetched

def testNodeWay():
    assert len(osm.nodeWays) > 0
    for id, ways in osm.nodeWays.items():
        for w in ways:
            assert w in osm.ways
            assert id in osm.ways[w].nodes
        assert id in osm.nodes
    assert not 42431626 in osm.nodeWays
    assert 42444081 in osm.nodeWays
    fetched = osm.nodeWays[42431626]
    assert fetched != None
    print fetched
    for w in fetched:
        assert 42431626 in osm.ways[w].nodes

def testWay():
    assert len(osm.ways) > 0
    for id, way in osm.ways.items():
        assert id == way.id
        assert way != None
        assert osm.ways[id] == way
    assert 5671196 in osm.ways
    assert not 46425585 in osm.ways
    fetched = osm.ways[46425585]
    assert fetched.id == 46425585
    assert 46425585 in osm.ways
    assert isinstance(fetched.__repr__(), str)
    assert osm.ways[46425585] > osm.ways[5671196]
    tampered = osm.store.way_retrieve(46425585)
    tampered.version = tampered.version + 1
    assert tampered > fetched    

def testRelation():
    assert len(osm.relations) == 0
    assert not 61320 in osm.relations
    fetched = osm.relations[61320]
    assert fetched.id == 61320
    assert 61320 in osm.relations
    assert osm.store.relation_retrieve(61320) == fetched
    assert not 224951 in osm.relations
    fetched2 = osm.relations[224951]
    assert 224951 in osm.relations
    for id, relation in osm.relations.items():
        assert id == relation.id
        assert relation != None
        assert osm.relations[id] == relation
    assert isinstance(fetched.__repr__(), str)
    assert osm.relations[61320] < osm.relations[224951]
    tampered = osm.store.relation_retrieve(224951)
    tampered.members[0].ref = "relation"
    assert tampered != fetched2
    tampered.version = tampered.version + 1
    assert tampered > fetched2

def testStoreCheckInMap():
    assert osm.store.check_in_map(40.8505, -73.9365)
    assert not osm.store.check_in_map(40.8505, -73.9375)
    assert not osm.store.check_in_map(40.8515, -73.9365)
    assert not osm.store.check_in_map(40.8495, -73.9365)
    assert not osm.store.check_in_map(40.8505, -73.9385)
    assert osm.store.map_node_exists(42444081)
    assert not osm.store.map_node_exists(42431626)

