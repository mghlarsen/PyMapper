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

from setuptools import setup, find_packages

setup(
    name = "PyMapper",
    version = "0.1a2",
    packages = find_packages(),

    author = "Michael G. H. Larsen",
    author_email = "mike.gh.larsen@gmail.com",
    description = "An OpenStreetMap.org based mapping application",
    license = "GPLv3",

    setup_requires = ['nose>=0.11'],
    test_suite = 'nose.collector'
)

