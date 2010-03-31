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
import sys
from osm.node import Node
from osm.way import Way
from OsmApi import OsmApi

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

DEBUG = True

api = OsmApi(debug = DEBUG)

nodes = dict()
ways = dict()
relations = dict()
nodeWays = dict()

def mapGet(lat, lon, dist = 0.0125):
    if DEBUG:
        print("lat: %s lon: %s dist: %s" % (lat, lon, dist))
    m = api.Map(lon - dist, lat - dist, lon + dist, lat + dist)     
    for i in m:
       data = i['data']
       id = int(data['id'])
       ver = int(data['version'])
       type = i['type']
       if (type == 'node') and ((not id in nodes) or (ver > int(nodes[id]['version']))):
           nodes[id] = data
       elif (type == 'way') and ((not id in ways) or (ver > int(ways[id]['version']))):
           ways[id] = data
           for nid in data['nd']:
               nodeID = int(nid)
               if nodeID in nodeWays:
                   nodeWays[nodeID].append(id)
               else:
                   nodeWays[nodeID] = [id]
       elif type == 'relation': 
           if ((not id in relations) or (ver > int(relations[id]['version']))):
               relations[id] = data
    return m

def nodeGet(id):
    if not id in nodes: nodes[id] = api.NodeGet(id) 
    return nodes[id]

def wayGet(id):
    if not id in ways: ways[id] = api.WayGet(id) 
    return ways[id]

def nodeWayGet(id):
    if not id in nodeWays:
        ways = api.NodeWays(id)
        for i in xrange(len(ways)):
            ways[i] = int(ways[i]['id'])
        nodeWays[id] = ways
    return nodeWays[id]

usage = """Usage:
osm.py map <lat> <lon> [<dist>]
"""

def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "map":
        mapcmd(sys.argv)
    else:
        print (usage)

def mapcmd(argv):
   if len(argv) == 4:
        m = mapGet(float(argv[2]), float(argv[3]))
   else:
        m = mapGet(float(argv[2]), float(argv[3]), float(argv[4]))

   nodeMap = dict()
   for i in m:
       if i['type'] == "node":
           nodeMap[i['data']['id']] = i
    
   wayMap = dict()        
   for i in m:
       type = i['type']
       data = i['data']
       if type == "way":
           nd = data['nd']
           for j in nd:
               if j in nodeMap:
                   if not j in wayMap:
                       wayMap[j] = list()
                   if 'name' in data['tag']:
                       wayMap[j].append(i)
                   elif 'highway' in data['tag']:
                       data['tag']['name'] = data['tag']['highway'] + ' road #' + str(data['id'])      
   for i in wayMap.keys():
       print("%d (%s, %s): " % 
             (i, nodeMap[i]['data']['lat'], nodeMap[i]['data']['lon']), 
             end = '') 
       print([w['data']['tag']['name'] for w in wayMap[i]], sep='')


if __name__ == "__main__":
    print(sys.argv)
    main()

