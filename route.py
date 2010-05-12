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

import osm
import sys
import math
import Queue

DEBUG = True
MAX_ITER = 1000

def routeFind(src, dst, queue_max_size = 0):
    srcNode = osm.nodes[src]
    dstNode = osm.nodes[dst]

    toAnalyze = Queue.PriorityQueue(queue_max_size)
    analyzed = dict()

    toAnalyze.put((0 + distance(src, dst), src, 0, []))
    queueSize = 1

    i = 0

    while (not toAnalyze.empty()) and (i < MAX_ITER):
        i += 1
        estDist, curr, currPathDist, path = toAnalyze.get()
        queueSize -= 1
        if DEBUG:
            print "left:%s est:%s curr:%s distance:%s path:%s" % (queueSize, estDist, curr, currPathDist, path)
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
            queueSize += 1
        analyzed[curr] = currPathDist
    return ([], -1)

def getAdjacent(nodeID):
    wayIDs = osm.nodeWays[nodeID]
    adjacent = []
    for wayID in wayIDs:
        way = osm.ways[wayID]
        curr = -1
        for i in xrange(len(way.nodes)):
            if way.nodes[i] == nodeID:
                curr = i
                break
        if curr == -1: continue
        
        if DEBUG:
            print "node:%s way:%s i:%s way.nodes:%s%s" % (nodeID, wayID, i, len(way.nodes), way.nodes),
            if i != 0: print " %s" % (way.nodes[i - 1], ),
            if i < len(way.nodes) - 1: print " %s" % (way.nodes[i + 1]),
            print
        if i > 0: adjacent.append(way.nodes[i - 1])
        if i < len(way.nodes) - 1: adjacent.append(way.nodes[i + 1])
    return adjacent

def distance(srcID, dstID):
    srcNode = osm.nodes[srcID]
    dstNode = osm.nodes[dstID]
    srcLat = srcNode.lat
    srcLon = srcNode.lon
    dstLat = dstNode.lat
    dstLon = dstNode.lon
    return math.sqrt(((srcLat - dstLat)**2) + ((srcLon - dstLon)**2))

usage = """Usage:
route.py <src node #> <dst node #>"""

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print usage
    else:
        print routeFind(int(sys.argv[1]), int(sys.argv[2]))

