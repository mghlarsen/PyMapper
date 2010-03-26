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
from OsmApi import OsmApi

DEBUG = True

api = OsmApi(debug = DEBUG)

def mapGet(lat, lon, dist = 0.0125):
    if DEBUG:
        print("lat: %s lon: %s dist: %s" % (lat, lon, dist))
    return api.Map(lon - dist, lat - dist, lon + dist, lat + dist)

def nodeGet(id):
    return api.NodeGet(id)

def wayGet(id):
    return api.WayGet(id)

def nodeWayGet(id):
    return api.NodeWays(id)

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
                   if not wayMap.has_key(j):
                       wayMap[j] = list()
                   if not data['tag'].has_key('name'):
                       print(data)
                       data['tag']['name'] = data['tag']['highway'] + ' road #' + str(data['id'])
                   else:
                       wayMap[j].append(i)
    
   for i in wayMap.keys():
       print("%d (%s, %s): " % 
             (i, nodeMap[i]['data']['lat'], nodeMap[i]['data']['lon']), 
             end = '') 
       print([w['data']['tag']['name'] for w in wayMap[i]], sep='')


if __name__ == "__main__":
    print(sys.argv)
    main()

