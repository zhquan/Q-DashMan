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
#   Quan Zhou <quan@bitergia.com>
#


import argparse
import json
import requests


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("-t", "--token",
                        action="store",
                        dest="token",
                        help="slack token")
    parser.add_argument("-j", "--json",
                        action="store",
                        dest="json",
                        help="projects.json path")
    parser.add_argument("-p", "--project",
                        action="store",
                        dest="project",
                        help="project name")
    args = parser.parse_args()

    return args


def read_file(filename):
    try:
        f = open(filename, 'r')
        read = json.loads(f.read())
        f.close()
    except:
        read = {'projects': {}}

    return read


def write_file(filename, data):
    with open(filename, 'w+') as f:
        json.dump(data, f, sort_keys=True, indent=4)


def get_channels(url):
    r = requests.get(url)
    r.raise_for_status()

    group_list = []
    for channels in r.json()['channels']:
        group_list.append(channels['id'])
    return group_list


def main():
    args = parse_args()
    token = args.token
    url = 'https://slack.com/api/channels.list?token='+token+'&pretty=1'
    json_path = args.json
    projects = args.project

    groups = get_channels(url)

    projects_json = read_file(json_path)
    projects_json[projects]['slack'] = groups

    write_file(json_path, projects_json)


if __name__ == '__main__':
    main()
