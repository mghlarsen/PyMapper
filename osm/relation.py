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

class Relation:
    class Member:
        def __init__(self, *args):
            if len(args) == 1:
                self.__from_element(*args)
            elif len(args) == 3:
                self.__from_data(*args)
        
        def __from_element(self, element):
            attr = element.attributes
            self.type = attr["type"].nodeValue
            self.ref = int(attr["ref"].nodeValue)
            self.role = attr["role"].nodeValue
        
        def __from_data(self, role, type, ref):
            self.role = role
            self.type = type
            self.ref = ref
        
    def __init__(self, *args):
        if len(args) == 1:
            self.__from_element(*args)
        elif len(args) == 4:
            self.__from_data(*args)
    
    def __from_element(self, element):
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
        self.id = id
        self.version, self.timestamp, self.changeset, self.uid, self.user = fields
        self.tags = tags
        self.members = [Relation.Member(m[0], m[1], m[2]) for m in members]
    
    def __repr__(self):
        return "<Relation id:%(id)s>" % {'id':self.id}
