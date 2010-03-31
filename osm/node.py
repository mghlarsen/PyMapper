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

class Node:
    def __init__(self, *args):
        if len(args) == 1:
            self.__from_element(args[0])
        elif len(args) == 3:
            self.__from_data(args[0], args[1], args[2])

    def __from_element(self, element):
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
        self.id = id
        self.lat, self.lon, self.version, self.timestamp, self.changeset, self.uid, self.user = fields
        self.tags = tags
    
    def __repr__(self):
        return "<Node id:%(id)s lat:%(lat)s lon:%(lon)s>" %  {
            'id':self.id, 'lat':self.lat, 'lon':self.lon, 'tags':self.tags}

