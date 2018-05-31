#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#   José Manrique López <jsmanrique@bitergia.com>
#   Quan Zhou <quan@bitergia.com>
#


import urllib
from bs4 import BeautifulSoup


def __has_class(tag, value='gridList-item'):
    if tag.has_attr('class') and value in tag['class']:
        return tag


def get_groups(topic):
    url = 'https://www.meetup.com/es-ES/topics/{}/all/'.format(topic)
    html_code = urllib.request.urlopen(url)
    doc = html_code.read()
    soup = BeautifulSoup(doc, 'html.parser')
    meetups = []
    for item in soup.find_all(__has_class):
        links = item.find_all('a')
        href = links[0]['href']
        meetups.append(href.split('/')[4])

    return meetups
