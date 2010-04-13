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
import os

DEBUG = True
DATABASE_FILENAME = getattr(os.environ, 'OSM_DB_FNAME', "osm.db")
DATABASE_USE_MEMORY = getattr(os.environ, 'OSM_DB_MEM', False)

import osm.node
import osm.way
import osm.relation
import osm.fetch
import osm.store
import osm.dict

nodes = osm.dict.NodeDict()
ways = osm.dict.WayDict()
relations = osm.dict.RelationDict()
nodeWays = osm.dict.NodeWayDict()

