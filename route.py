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
import osm
import sys
import math
import Queue

DEBUG = True
MAX_ITER = 100

def routeFind(src, dst, queue_max_size = 0):
    srcNode = osm.nodeGet(src)
    dstNode = osm.nodeGet(dst)
    
    toAnalyze = Queue.PriorityQueue(queue_max_size)
    analyzed = dict()
    
    toAnalyze.put((0 + distance(src, dst), src, 0, []))
    
    i = 0
    
    while (not toAnalyze.empty()) and (i < MAX_ITER):
        i += 1
        estDist, curr, currPathDist, path = toAnalyze.get()
        if DEBUG: print("est:%s curr:%s distance:%s path:%s" 
              % (estDist, curr, currPathDist, path))
        if curr == dst: return (path, currPathDist)
        if curr in analyzed and currPathDist >= analyzed[curr]:
            continue
        next = getAdjacent(curr)
        for n in next:
            nextDist = distance(curr, n)
            nextPathDist = currPathDist + nextDist
            nextEstDist = nextPathDist + distance(n, dst)
            nextPath = path + [n]
            toAnalyze.put((nextEstDist, n, nextPathDist, nextPath))
        analyzed[curr] = currPathDist
    return ([], -1)

def getAdjacent(nodeID):
    wayIDs = osm.nodeWayGet(nodeID)
    adjacent = []
    for wayID in wayIDs:
	way = wayGet(wayID)
        curr = -1
        for i in xrange(len(way['nd'])):
            if way['nd'][i] == nodeID:
                curr = i
                break
        if curr == -1: continue
        
        if i > 0: adjacent.append(way['nd'][i - 1])
        if i < len(way['nd']) - 1: adjacent.append(way['nd'][i + 1])
    return adjacent

def distance(srcID, dstID):
    srcNode = osm.nodeGet(srcID)
    dstNode = osm.nodeGet(dstID)
    srcLat = float(srcNode['lat'])
    srcLon = float(srcNode['lon'])
    dstLat = float(dstNode['lat'])
    dstLon = float(dstNode['lon'])
    return math.sqrt(((srcLat - dstLat)**2) + ((srcLon - dstLon)**2))

usage = """Usage:
route.py <src node #> <dst node #>"""

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(usage)
    else:
        print(routeFind(int(sys.argv[1]), int(sys.argv[2])))
