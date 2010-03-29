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
from urllib2 import urlopen
from xml.dom.minidom import parse
from osm import Node, Way, Relation

DEFAULT_SERVER = "www.openstreetmap.org"
DEFAULT_API = "0.6"

def extract_data(document):
    osm_node = document.documentElement
    assert osm_node.tagName == u'osm'
    
    nodes = [Node(e) for e in osm_node.getElementsByTagName("node")]
    ways = [Way(e) for e in osm_node.getElementsByTagName("way")]
    relations = [Relation(e) for e in osm_node.getElementsByTagName("relation")]
    print("nodes:%(nodes)s\nways:%(ways)s\nrelations:%(relations)s\n" % locals())
    return nodes + ways + relations

def map_get(minLat, maxLat, minLon, maxLon, server = DEFAULT_SERVER, api = DEFAULT_API):
    print("map?bbox=%(minLon)s,%(minLat)s,%(maxLon)s,%(maxLat)s" % locals())
    doc = fetch("map?bbox=%(minLon)s,%(minLat)s,%(maxLon)s,%(maxLat)s" % locals(), server, api)
    return extract_data(doc)

def relation_get(id, server = DEFAULT_SERVER, api = DEFAULT_API):
    doc = fetch("relation/%(id)s" % locals(), DEFAULT_SERVER, DEFAULT_API)
    return extract_data(doc)

def way_get(id, server = DEFAULT_SERVER, api = DEFAULT_API):
    doc = fetch("way/%(id)s" % locals(), DEFAULT_SERVER, DEFAULT_API)
    return extract_data(doc)

def node_get(id, server = DEFAULT_SERVER, api = DEFAULT_API):
    doc = fetch("node/%(id)s" % locals(), DEFAULT_SERVER, DEFAULT_API)
    return extract_data(doc)

def fetch(methodStr, server = DEFAULT_SERVER, api = DEFAULT_API):
    print("fetching http://%(server)s/api/%(api)s/%(methodStr)s" % locals())
    results = urlopen("http://%(server)s/api/%(api)s/%(methodStr)s" % locals())
    print("url: ", results.geturl())
    print("info: ", results.info())
    
    return parse(results)

res = None
if __name__ == "__main__":
    res = map_get(40.85, 40.86, -73.94, -73.93)