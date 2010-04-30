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
This module contains the Relation class and associated functions and data.
"""
class Relation:
    """
This class represents a relation object in the openstreetmap.org data.
A Relation represents a relation between some group of nodes, ways, and other
relations.
    """
    class Member:
        """
Represents a member of the Relation.
        """
        def __init__(self, *args):
            """
If called with one argument, calls __from_element.
If called with three arguments, calls __from_data.
            """
            if len(args) == 1:
                self.__from_element(*args)
            elif len(args) == 3:
                self.__from_data(*args)

        def __from_element(self, element):
            """
Constructs a Relation.Member from a xml.minidom element object.
            """
            attr = element.attributes
            self.type = attr["type"].nodeValue
            self.ref = int(attr["ref"].nodeValue)
            self.role = attr["role"].nodeValue

        def __from_data(self, role, type, ref):
            """
Constructs a Relation.Member from data.
role -- the role of this particular member.
type -- the type of object this Member is.
ref -- the id # of the object this Member refers to.
            """
            self.role = role
            self.type = type
            self.ref = ref

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
Constructs a Relation from a xml.minidom element object.
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
        self.members = [Relation.Member(e) for e in element.getElementsByTagName("member")]

    def __from_data(self, id, fields, tags, members):
        """
Constructs a Relation with the specified id. Fields should be a tuple of (version,
timestamp, changeset, uid, user). tags should have {k1:v1, k2:v2, ...}. members
should be a list of tuples for each member of the form (role, type, ref).
        """
        self.id = id
        self.version, self.timestamp, self.changeset, self.uid, self.user = fields
        self.tags = tags
        self.members = [Relation.Member(m[0], m[1], m[2]) for m in members]

    def insert_tuple(self):
        """
Return the database insert tuple for this relation.
(id, version, timestamp, changeset, uid, user)
        """
        return (self.id, self.version, self.timestamp, self.changeset, self.uid, self.user)

    def __repr__(self):
        """
Return a readable representation of this Relation.
        """
        return "<Relation id:%(id)s>" % {'id':self.id}

relation_fields = ('id', 'version', 'timestamp', 'changeset', 'uid', 'user')

