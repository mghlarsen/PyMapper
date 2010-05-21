# -*- coding: utf-8 -*-

## Copyright 2010 Michael Larsen <mike.gh.larsen@gmail.com>             ##
##                                                                      ##
## This program is free software: you can redistribute it and/or modify ##
## it under the terms of the GNU General Public License as published by ##
## the Free Software Foundation, either version 3 of the License, or    ##
## (at your option) any later version.                                  ##
##                                                                      ##
## This program is distributed in the hope that it will be useful,      ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of       ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the         ##
## GNU General Public License for more details.                         ##
##                                                                      ##
## You should have received a copy of the GNU General Public License    ##
## along with this program. If not, see <http://www.gnu.org/licenses/>. ##
"""
This is the 'osm.config' module. It's responsible for handling configuration of all
services in the osm package.

Members:
options: Returned by optparse.OptionParser, holds options passed on the command line.
args: Non-option arguments passed on the command line.
config: Configuration as extracted from defaults, command line, and config file.
"""
import osm
import optparse
import ConfigParser

_parser = optparse.OptionParser()
_parser.add_option('-c', '--config', dest='config', help="Set config file to FILE", metavar="FILE")

options, args = _parser.parse_args()
_config_file = options.config
if _config_file == None:
    _config_file = osm.OSM_CONFIG_FILE_DEFAULT

config = ConfigParser.SafeConfigParser()
config.add_section('osm')
config.set('osm', 'debug', 'False')
config.set('osm', 'db-connect-string', 'sqlite:///osm.db')
config.set('osm', 'db-echo-on', 'False')
config.set('osm', 'map-point-range', '0.01')
config.set('osm', 'api-server', 'www.openstreetmap.org')
config.set('osm', 'api-ver', '0.6')
config.set('osm', 'tile-dir', 'tiles')
config.set('osm', 'tile-url', 'http://tah.openstreetmap.org/Tiles/tile/%(zoom)d/%(xtile)d/%(ytile)d.png')
config.read(_config_file)

def debug():
    return bool(config.get('osm', 'debug'))

def db_connect_str():
    return config.get('osm', 'db-connect-string')

def db_echo_os():
    return bool(config.get('osm', 'db-echo-on'))

def map_point_range():
    return float(config.get('osm', 'map-point-range'))

def osm_api_server():
    return config.get('osm', 'osm-api-server')

def osm_api_ver():
    return config.get('osm', 'osm-api-ver')

def tile_dir():
    return config.get('osm', 'tile-dir')

def tile_url():
    return config.get('osm', 'tile-url', raw=True)

