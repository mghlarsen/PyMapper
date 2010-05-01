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
This module contains the node class an associated functions and data.
"""

class Node:
    """
    This class represents a node object in the openstreetmap.org data.
    A Node represents some point on the map and is used to define ways.
    """
    def __init__(self, *args):
        """
        Create a Node object. If called with one argument, it will call __from_element.
        If called with three arguments, it will call __from_data.
        """
        if len(args) == 1:
            self.__from_element(args[0])
        elif len(args) == 3:
            self.__from_data(args[0], args[1], args[2])

    def __from_element(self, element):
        """
        Constructs a Node from a xml.minidom element object.
        """
        attr = element.attributes
        self.id = int(attr['id'].nodeValue)
        self.lat = float(attr['lat'].nodeValue)
        self.lon = float(attr['lon'].nodeValue)
        self.version = int(attr['version'].nodeValue)
        self.timestamp = attr['timestamp'].nodeValue
        self.changeset = int(attr['changeset'].nodeValue)
        self.uid = int(attr['uid'].nodeValue)
        self.user = attr['user'].nodeValue
        tagElements = element.getElementsByTagName("tag")
        self.tags = dict()
        for e in tagElements:
            self.tags[e.attributes['k'].nodeValue] = e.attributes['v'].nodeValue

    def __from_data(self, id, fields, tags):
        """
        Constructs a Node with the specified id. fields should be a tuple of 
        (lat, lon, version, timestamp, changeset, uid, user). Tags should have 
        {k1:v1, k2:v2, ...}.
        """
        self.id = id
        self.lat, self.lon, self.version, self.timestamp, self.changeset, self.uid, self.user = fields
        self.tags = tags
   
    def __repr__(self):
        """
        Return readable representation of this node.
        """
        return "<Node id:%(id)s lat:%(lat)s lon:%(lon)s>" %  {
            'id':self.id, 'lat':self.lat, 'lon':self.lon, 'tags':self.tags}

    def __cmp__(self, other):
        """
        Comparison operator.
        """
        if isinstance(other, Node):
            if self.id == other.id:
                if ((self.lat == other.lat) and
                    (self.lon == other.lon) and
                    (self.version == other.version) and
                    (self.timestamp == other.timestamp) and
                    (self.changeset == other.changeset) and
                    (self.uid == other.uid) and
                    (self.user == other.user) and
                    (self.tags == other.tags)):
                        return 0
                return self.version - other.version
            return self.id - other.id
        return NotImplemented

    def insert_tuple(self):
        """
        Returns a tuple of information for insertion into the database.
        (id, lat, lon, version, timestamp, changeset, uid, user)
        """
        return (self.id, self.lat, self.lon, self.version, self.timestamp, self.changeset, self.uid, self.user)

node_fields = ('id', 'lat', 'lon', 'version', 'timestamp', 'changeset', 'uid', 'user')
