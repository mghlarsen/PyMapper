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

import osm
import sys

def routeFind(src, dst):
    srcNode = osm.nodeGet(src)
    dstNode = osm.nodeGet(dst)
    return []

usage = """Usage:
route.py <src node #> <dst node #>"""

if __name__ == '__main__':
    if len(sys.argv) < 3:
	print(usage)
    else:
	print(routeFind(int(sys.argv[1]), int(sys.argv[2])))
