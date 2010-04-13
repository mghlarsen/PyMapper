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
The osm.dict module provides the actual interface that is exposed in the osm module.

"""

import collections
import osm.store
import osm.fetch

class OSMDict(collections.Mapping):
    """
    Generic dictionary based on pluggable functions.

    """
    def __init__(self, retrieve, fetch, count, contains, iter):
        """
        contains: should only return true if the data is locally stored.
        retrieve: should get the data from local sources.
        fetch: should go to the remote sources and cache.
        count: should return the number of local objects.
        iter: should return an iterator over all the
        """
        self.retrieve = retrieve
        self.fetch = fetch
        self.count = count
        self.contains = contains
        self.iter = iter

    def __getitem__(self, item):
        """
        get the value associated with item.
        first tries retrieve, and then fetch.
        """
        try:
            return self.retrieve(item)
        except:
            return self.fetch(item)

    def __len__(self):
        """returns number of locally stored objects. uses count."""
        return self.count()

    def __contains__(self, item):
        """returns true if this item is local. uses contains."""
        return self.contains(item)

    def __iter__(self):
        """"returns an iterator over the locally stored objects."""
        return self.iter()

class NodeDict(OSMDict):
    """
    OSMDict subclass that accesses osm.node.Node objects

    internally uses:
    retrieve: osm.store.node_retrieve
    fetch: osm.fetch.node_fetch
    count: osm.store.node_count
    contain: osm.store.node_exists
    iter: osm.store.node_iter

    """
    def __init__(self):
        retr = osm.store.node_retrieve
        fetch = osm.fetch.node_fetch
        count = osm.store.node_count
        contain = osm.store.node_exists
        iter = osm.store.node_iter
        OSMDict.__init__(self, retr, fetch, count, contain, iter)

class WayDict(OSMDict):
    """
    OSMDict subclass that accesses osm.way.Way objects

    internally uses:
    retrieve: osm.store.way_retrieve
    fetch: osm.fetch.way_fetch
    count: osm.store.way_count
    contain: osm.store.way_exists
    iter: osm.store.way_iter

    """
    def __init__(self):
        retr = osm.store.way_retrieve
        fetch = osm.fetch.way_fetch
        count = osm.store.way_count
        contain = osm.store.way_exists
        iter = osm.store.way_iter
        OSMDict.__init__(self, retr, fetch, count, contain, iter)

class NodeWayDict(OSMDict):
    """
    OSMDict subclass that indexes which ways contain each node.

    internally uses:
    retrieve: osm.store.node_way_retrieve
    fetch: osm.fetch.node_way_fetch
    count: osm.store.map_node_count
    contain: osm.store.map_node_exists
    iter: osm.store.node_way_iter

    """
    def __init__(self):
        retr = osm.store.node_way_retrieve
        fetch = osm.fetch.node_way_fetch
        count = osm.store.map_node_count
        contain = osm.store.map_node_exists
        iter = osm.store.node_way_iter
        OSMDict.__init__(self, retr, fetch, count, contain, iter)

class RelationDict(OSMDict):
    """
    OSMDict subclass that accesses osm.relation.Relation objects

    internally uses:
    retrieve: osm.store.relation_retrieve
    fetch: osm.fetch.relation_fetch
    count: osm.store.relation_count
    contain: osm.store.relation_exists
    iter: osm.store.relation_iter

    """
    def __init__(self):
        retr = osm.store.relation_retrieve
        fetch = osm.fetch.relation_get
        count = osm.store.relation_count
        contain = osm.store.relation_exists
        iter = osm.store.relation_iter
        OSMDict.__init__(self, retr, fetch, count, contain, iter)

