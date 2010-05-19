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

import math
import os
import os.path
from urllib2 import urlopen

TILEDIR = "tiles"
TILEURL = "http://tah.openstreetmap.org/Tiles/tile/%(zoom)d/%(xtile)d/%(ytile)d.png"
DEBUG = False

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return(lat_deg, lon_deg)

def get_tile_png(xtile, ytile, zoom, url = TILEURL):
    if DEBUG:
        print url % locals()
    return urlopen(url % locals())

def get_png_filename(xtile, ytile, zoom):
    path = os.path.join(TILEDIR, str(zoom), str(xtile), "%s.png" %(ytile,))
    if os.path.exists(path):
        return path
    else:
        try:
            os.makedirs(os.path.join(TILEDIR, str(zoom), str(xtile)))
        except OSError as err:
            if err.errno == 17:
                pass
            else:
                raise
        pngfile = get_tile_png(xtile, ytile, zoom)
        targetfile = open(path, "wb")
        targetfile.writelines(pngfile)
        return path
        
