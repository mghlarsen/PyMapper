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
"""
This is the "osm" module and package.

The osm package provides a dict-based interface to obtaining map data from
OpenStreetMap.org. It uses sqlite internally forcaching map data to reduce
network usage and for speed.

Members:
config: a ConfigParser.SafeConfigParser object holding config for osm.

nodes: dictionary of osm.node.Node objects. Auto-fetches missing data
when necessary. Use __contains__() or 'in' to check before.

ways: dictionary of osm.way.Way objects. Auto-fetches missing data when
necessary. Use __contains__() or 'in' to check before fetching.

relations: dictionary of osm.relation.Relation objects. Auto-fetches missing
data when necessary. Use __contains__() or 'in' to check before fetching.

nodeWays: dictionary of node ids to the ids of the ways that contain them.

"""

import ConfigParser

config = ConfigParser.SafeConfigParser({'debug':True, 'db-filename':'osm.db', 'db-use-memory':False})
config.add_section('osm')
config.read('osm.cfg')
    
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

