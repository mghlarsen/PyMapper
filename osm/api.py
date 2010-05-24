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
"""
import osm.config
from urllib2 import urlopen

DEBUG = osm.config.debug()
DEFAULT_SERVER = osm.config.osm_api_server()
DEFAULT_API = osm.config.osm_api_ver()

def map_get(minLat, maxLat, minLon, maxLon, server = DEFAULT_SERVER, api = DEFAULT_API):
    """
    Gets all map data inside the box defined by the parameters from the
    designated server and api.
    """
    return fetch("map?bbox=%(minLon)s,%(minLat)s,%(maxLon)s,%(maxLat)s" % locals(),
                server, api)

def relation_get(id, server = DEFAULT_SERVER, api = DEFAULT_API):
    """
    Executes a query for the specified relation.
    Returns a list containing all the data returned by the server (presumably
    just the relation).
    """
    return fetch("relation/%(id)s" % locals(), DEFAULT_SERVER, DEFAULT_API)

def way_get(id, server = DEFAULT_SERVER, api = DEFAULT_API):
    """
    Executes a query for the specified way.
    Returns a list containing all the data returned by the server (presumably
    just the way).
    """
    return fetch("way/%(id)s" % locals(), DEFAULT_SERVER, DEFAULT_API)

def node_get(id, server = DEFAULT_SERVER, api = DEFAULT_API):
    """
    Executes a query for the specified node.
    Returns a list containing all the data returned by the server (presumably
    just the node).
    """
    return fetch("node/%(id)s" % locals(), DEFAULT_SERVER, DEFAULT_API)

def node_way_get(id, server = DEFAULT_SERVER, api = DEFAULT_API):
    """
    Executes a query for all ways that include the specified node.
    Returns a list containing all the data returned by the server (presumably
    just the ways).
    """
    return fetch("node/%(id)s/ways"% locals(), DEFAULT_SERVER, DEFAULT_API)

def fetch(methodStr, server = DEFAULT_SERVER, api = DEFAULT_API):
    """
    Execute a query to given server at the specified api version.
    Returns the server response parsed by xml.minidom.
    """
    if DEBUG:
        print "fetching http://%(server)s/api/%(api)s/%(methodStr)s" % locals()
    return urlopen("http://%(server)s/api/%(api)s/%(methodStr)s" % locals())

