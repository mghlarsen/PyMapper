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
This module contains the Way class and associated functions and data.
"""

class Way:
    """
    This class represents a way object in openstreetmap.org data.
    A Way represents either a path or an area.
    """
    def __init__(self, *args):
        """
        If called with one argument, calls __from_element.
        If called with three arguments, calls __from_data.
        """
        if len(args) == 1:
            self.__from_element(*args)
        elif len(args) == 4:
            self.__from_data(*args)

    def __from_element(self, element):
        """
        Constructs a Way from a xml.minidom element object.
        """
        attr = element.attributes
        self.id = int(attr['id'].nodeValue)
        self.version = int(attr['version'].nodeValue)
        self.timestamp = attr['timestamp'].nodeValue
        self.changeset = int(attr['changeset'].nodeValue)
        self.uid = int(attr['uid'].nodeValue)
        self.user = attr['user'].nodeValue
        tagElements = element.getElementsByTagName("tag")
        self.tags = dict()
        for e in tagElements:
            self.tags[e.attributes['k'].nodeValue] = e.attributes['v'].nodeValue
        self.nodes = [int(nd.attributes['ref'].nodeValue) for nd in 
                       element.getElementsByTagName("nd")]

    def __from_data(self, id, fields, tags, nodes):
        """
        Constructs a Way with the specified id. Fields should be a tuple of
        (version, timestamp, changeset, uid, user). tags should have {k1:v1,
        k2:v2, ...}. nodes should be a list of node ids.
        """
        self.id = id
        self.version, self.timestamp, self.changeset, self.uid, self.user = fields
        self.tags = tags
        self.nodes = nodes

    def insert_tuple(self):
        """
        Return the database insert tuple for this relation.
        (id, version, timestamp, changeset, uid, user)
        """
        return (self.id, self.version, self.timestamp, self.changeset, self.uid, self.user)

    def __repr__(self):
        """
        Return a readable representation of this Way.
        """
        return "<Way id:%(id)s>" % {'id':self.id, 'tags':self.tags}

    def __cmp__(self, other):
        """
        Comparison operator.
        """
        if isinstance(other, Way):
            if self.id == other.id:
                if ((self.version == other.version) and
                    (self.timestamp == other.timestamp) and
                    (self.changeset == other.changeset) and
                    (self.uid == other.uid) and
                    (self.user == other.user) and
                    (self.tags == other.tags) and
                    (self.nodes == other.nodes)):
                        return 0
                return self.version - other.version
            return self.id - other.id
        return NotImplemented

way_fields = ('id', 'version', 'timestamp', 'changeset', 'uid', 'user')

