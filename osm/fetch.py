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
This module is responsible for fetching data from the server.

By default fetching is done from www.openstreetmap.org with api version 0.6.
Currently, Debug is enabled by default (and configuration isn't really
implemented very flexibly, so you'll have to edit it here or override on each
call.
"""

from urllib2 import urlopen
from xml.dom.minidom import parse
import osm.node
import osm.way
import osm.relation
import osm.store

DEBUG = True
DEFAULT_SERVER = "www.openstreetmap.org"
DEFAULT_API = "0.6"

def extract_data(document):
    """
    This function extracts the appropriate node, way, and relation objects from
    the supplied xml.minidom document element. It returns a list consisting of
    these objects.
    """
    osm_node = document.documentElement
    assert osm_node.tagName == u'osm'

    nodes = [osm.node.Node(e) for e in osm_node.getElementsByTagName("node")]
    ways = [osm.way.Way(e) for e in osm_node.getElementsByTagName("way")]
    relations = [osm.relation.Relation(e) for e in 
                   osm_node.getElementsByTagName("relation")]
    return nodes + ways + relations

def map_get(minLat, maxLat, minLon, maxLon, server = DEFAULT_SERVER, api = DEFAULT_API):
    """
    Gets all map data inside the box defined by the parameters from the
    designated server and api.
    """
    doc = fetch("map?bbox=%(minLon)s,%(minLat)s,%(maxLon)s,%(maxLat)s" % locals(),
                server, api)
    osm.store.map_store(minLat, maxLat, minLon, maxLon)
    data = extract_data(doc)
    osm.store.data_store(data)
    return data

def relation_get(id, server = DEFAULT_SERVER, api = DEFAULT_API):
    """
    Executes a query for the specified relation.
    Returns a list containing all the data returned by the server (presumably
    just the relation).
    """
    doc = fetch("relation/%(id)s" % locals(), DEFAULT_SERVER, DEFAULT_API)
    return extract_data(doc)

def relation_fetch(id, server = DEFAULT_SERVER, api = DEFAULT_API):
    """
    Executes a query for the specified relation, and caches all data from the
    response.
    Returns the requested relation object.
    """
    data = relation_get(id, server, api)
    osm.store.data_store(data)
    for d in data:
        if isinstance(d, osm.relation.Relation) and d.id == id:
            return d

def way_get(id, server = DEFAULT_SERVER, api = DEFAULT_API):
    """
    Executes a query for the specified way.
    Returns a list containing all the data returned by the server (presumably
    just the way).
    """
    doc = fetch("way/%(id)s" % locals(), DEFAULT_SERVER, DEFAULT_API)
    return extract_data(doc)

def way_fetch(id, server = DEFAULT_SERVER, api = DEFAULT_API):
    """
    Executes a query for the specified way, and caches all data from the
    response.
    Returns the requested way object.
    """
    data = way_get(id, server, api)
    osm.store.data_store(data)
    for d in data:
        if isinstance(d, osm.way.Way) and d.id == id:
            return d

def node_get(id, server = DEFAULT_SERVER, api = DEFAULT_API):
    """
    Executes a query for the specified node.
    Returns a list containing all the data returned by the server (presumably
    just the node).
    """
    doc = fetch("node/%(id)s" % locals(), DEFAULT_SERVER, DEFAULT_API)
    return extract_data(doc)

def node_fetch(id, server = DEFAULT_SERVER, api = DEFAULT_API):
    """
    Executes a query for the specified node, and caches all data from the
    response.
    Returns the requested node object.
    """
    data = node_get(id, server, api)
    osm.store.data_store(data)
    for d in data:
        if isinstance(d, osm.node.Node) and d.id == id:
            return d

def node_way_get(id, server = DEFAULT_SERVER, api = DEFAULT_API):
    """
    Executes a query for all ways that include the specified node.
    Returns a list containing all the data returned by the server (presumably
    just the ways).
    """
    doc = fetch("node/%(id)s/ways"% locals(), DEFAULT_SERVER, DEFAULT_API)
    return extract_data(doc)

def node_way_fetch(id, server = DEFAULT_SERVER, api = DEFAULT_API):
    """
    Executes a query for all ways that include the specified node, and caches
    the response.
    Returns the requested way objects.
    """
    data = node_way_get(id, server, api)
    osm.store.data_store(data)
    return (d.id for d in data if isinstance(d, osm.way.Way))

def fetch(methodStr, server = DEFAULT_SERVER, api = DEFAULT_API):
    """
    Execute a query to given server at the specified api version.
    Returns the server response parsed by xml.minidom.
    """
    if DEBUG:
        print "fetching http://%(server)s/api/%(api)s/%(methodStr)s" % locals()
    results = urlopen("http://%(server)s/api/%(api)s/%(methodStr)s" % locals())

    return parse(results)

