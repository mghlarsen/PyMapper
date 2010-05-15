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
MAX_ITER = 10000

def routeFind(src, dst, queue_max_size = 0):
    toAnalyze = Queue.PriorityQueue(queue_max_size)
    analyzed = dict()

    toAnalyze.put((0 + distance(src, dst), src, 0, []))

    i = 0
    while (not toAnalyze.empty()) and (i < MAX_ITER):
        i += 1
        estDist, curr, currPathDist, path = toAnalyze.get()
        if DEBUG:
            print "i:%d  qsize:%d  est:%f  curr:%d  distance:%f" % (i, toAnalyze.qsize(), estDist, curr.id, currPathDist),
        if curr == dst: return (path, currPathDist)
        if curr in analyzed and currPathDist >= analyzed[curr]:
            print "analyzed[curr]:%f currPathDist:%f DROPPING" % (analyzed[curr], currPathDist)
            continue
        currBearing = bearing(curr, dst)
        print [n.id for n in curr.adjacent()]
        for n in curr.adjacent():
            nextDist = distance(curr, n)
            nextPathDist = currPathDist + nextDist
            deltaBearing = diff_bearing(bearing(curr, n), currBearing)
            nextEstDist = nextPathDist + (distance(n, dst) * (1 + (deltaBearing / (math.pi * 2))))
            nextPath = path + [n]
            if DEBUG:
                print "id:%d  est:%f  path:%f" % (n.id, nextEstDist, nextPathDist) 
            toAnalyze.put((nextEstDist, n, nextPathDist, nextPath))
        analyzed[curr] = currPathDist
    return ([], -1)

def distance(src, dst):
    from math import acos, cos, sin
    term1 = sin(src.lat) * sin(dst.lat)
    term2 = cos(src.lat) * cos(dst.lat) * cos(dst.lon - src.lon)
    return 6371.0 * acos(term1 + term2)

def bearing(src, dst):
    from math import atan2, cos, sin
    y = sin(dst.lon - src.lon) * cos(dst.lat)
    x = cos(src.lat) * sin (dst.lat) - sin(src.lat) * cos(dst.lat) * cos(dst.lon - src.lon)
    return atan2(y, x)

def diff_bearing(t1, t2):
    if t1 < t2:
        return diff_bearing(t2, t1)
    if t1 < 0 or t2 >= 0 or t2 + math.pi > t1:
        return t1 - t2
    return t2 + (2 * math.pi) - t1

usage = """Usage:
route.py <src node #> <dst node #>"""

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print usage
    else:
        print routeFind(osm.nodes[int(sys.argv[1])], osm.nodes[int(sys.argv[2])])

