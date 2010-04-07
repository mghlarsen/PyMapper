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

import sys
from osm.node import Node
from osm.way import Way
from osm.relation import Relation
from osm.fetch import map_get
from osm.store import data_store

nodes = dict()
ways = dict()
relations = dict()
nodeWays = dict()

def mapGet(lat, lon, dist = 0.0125):
    if DEBUG:
        print "lat: %s lon: %s dist: %s" % (lat, lon, dist)
    m = map_get(lat - dist, lat + dist, lon - dist, lon + dist)
    data_store(m)
    for i in m:
        if isinstance(i, Node):
            nodes[i.id] = i
        elif isinstance(i, Way):
            ways[i.id] = i
            for n in i.nodes:
                if n.in_bbox(lat - dist, lat + dist, lon - dist, lon + dist):
                    nodeWays[n.id] = nodeWays[n.id] + [i.id]
        elif isinstance(i, Relation):
            relations[i.id] = i
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
        print usage

def mapcmd(argv):
    if len(argv) == 4:
        m = mapGet(float(argv[2]), float(argv[3]))
    else:
        m = mapGet(float(argv[2]), float(argv[3]), float(argv[4]))

    wayMap = dict()
    for i in m:
        if isinstance(i, Way):
            for j in i.nodes:
               if j in nodeMap:
                   if not j in wayMap:
                       wayMap[j] = list()
                   if 'name' in i.tags:
                       wayMap[j].append(i)
                   elif 'highway' in i.tags:
                       i.tags['name'] = i.tags['highway'] + ' road #' + str(i.id)
    for i in wayMap.keys():
        print "%d (%s, %s): " %  (i, nodes[i].tags['lat'], nodeMap[i].tags['lon']),
        for w in wayMap[i]:
           print w.tags['name'],
        print


if __name__ == "__main__":
    print sys.argv
    main()
