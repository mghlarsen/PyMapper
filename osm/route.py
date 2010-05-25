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

from __future__ import with_statement
import osm.data
import sys
import math
import Queue
import threading


DEBUG = True
MAX_ITER = 10000

class RouteFinder:
    def __init__(self, origin, destination, filters = [], max_iter = MAX_ITER):
        self.origin = origin
        self.destination = destination
        self._filters = filters
        self._max_iter = MAX_ITER
        self._toCheck = Queue.PriorityQueue(0)
        self._checked = dict()
        self._stateLock = threading.Lock()
        self._iterations_done = 0
        self._results = []
        self._add_new(distance(origin, destination), origin, 0, [origin])
    
    def _next_iter(self, node, pathDist):
        with self._stateLock:
            if node in self._checked:
                print "checked: %f, pathDist: %f" % (self._checked[node], pathDist)
            assert (not node in self._checked) or (self._checked[node] >= pathDist)
            self._checked[node] = pathDist
            self._iterations_done += 1
            print self._iterations_done
            if self._iterations_done == self._max_iter:
                print "Hit max iterations, flushing queue."
                while not self._toCheck.empty():
                    self._toCheck.get()
                    self._toCheck.task_done()
                return None
        self._toCheck.task_done()
        return self._toCheck.get()

    def _next_iter_short(self):
        with self._stateLock:
            self._iterations_done += 1
            print self._iterations_done
            if self._iterations_done == self._max_iter:
                print "Hit max iterations, flushing queue."
                while not self._toCheck.empty():
                    self._toCheck.get()
                    self._toCheck.task_done()
                return None
        self._toCheck.task_done()
        return self._toCheck.get()
        

    def _add_new(self, estDist, node, pathDist, path):
        self._toCheck.put((estDist, node, pathDist, path))

    def _add_result(self, distance, path):
        with self._stateLock:
            print "Result: %f %s" % (distance, path)
            self._results.append((distance, path))
            self._results.sort()

    def _get_checked(self, node):
        with self._stateLock:
            if node in self._checked:
                return self._checked[node]
            else:
                return None
            

    def best_result(self):
        with self._stateLock:
            if len(self._results):
                return self._results[0]
            return None

    def join(self):
        self._toCheck().join()

    def search(self):
        frame = self._toCheck.get()
        while frame:
            estDist, curr, currPathDist, path = frame

            if curr == self.destination:
                self._add_result(currPathDist, path)

            checkedDist = self._get_checked(curr)
            bestDist = self.best_result()
            if checkedDist != None and checkedDist < currPathDist:
                frame = self._next_iter_short()
            elif bestDist != None and bestDist[0] <= currPathDist:
                frame = self._next_iter_short()
            else:
                for nTuple in curr.get_adjacent():
                    n = nTuple[2]
                    nextDist = distance(curr, n)
                    nextPathDist = currPathDist + nextDist
                    nextEstDist = nextPathDist + (1.1 * distance(n, self.destination))
                    nextPath = path + [n]

                    if bestDist != None and bestDist[0] < nextPathDist + distance(n, self.destination):
                        continue

                    nextCheckedDist = self._get_checked(n)
                    if nextCheckedDist != None and nextCheckedDist < nextPathDist:
                        continue
                    
                    self._add_new(nextEstDist, n, nextPathDist, nextPath)
                
                frame = self._next_iter(curr, currPathDist)

def routeFind(src, dest, queue_max_size = 0):
    finder = RouteFinder(src, dest)
    
    finder.search() 
    
    return finder.best_result()


def distance(src, dst):
    from math import acos, cos, sin
    term1 = sin(src.lat) * sin(dst.lat)
    term2 = cos(src.lat) * cos(dst.lat) * cos(dst.lon - src.lon)
    return 6371.0 * acos(term1 + term2)


usage = """Usage:
route.py <src node #> <dst node #>"""

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print usage
    else:
        res = routeFind(osm.data.node_get(int(sys.argv[1])), osm.data.node_get(int(sys.argv[2])))
        print "Route distance: %f" % (res[0],)
        print [n.id for n in res[1]]
