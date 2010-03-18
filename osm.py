#!/usr/bin/python

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
sys.path.append("osm_lib/OsmApi")
from OsmApi import OsmApi

api = OsmApi(debug = True)

def Map(lat, lon, dist = 0.0125):
    return api.Map(lat - dist, lon - dist, lat + dist, lon + dist)

usage = """Usage:
osm.py map <lat> <lon> [<dist>]
"""

def main():
    if sys.argv[1] == "map" and len(sys.argv) >= 4:
        if len(sys.argv) == 4:
            m = Map(float(sys.argv[2]), float(sys.argv[3]))
        else:
            m = Map(float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]))
        
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
            print(i, ": ", end='')
            print([w['data']['tag']['name'] for w in wayMap[i]], sep='')
    else:
        print (usage)


if __name__ == "__main__":
    print(sys.argv)
    main()

