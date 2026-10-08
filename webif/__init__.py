#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
#  Copyright 2026-      MIWE77
#########################################################################
#  This file is part of SmartHomeNG.
#  https://www.smarthomeNG.de
#  https://knx-user-forum.de/forum/supportforen/smarthome-py
#
#  This file implements the web interface for the Open-Meteo plugin.
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import json
import time

import cherrypy
from jinja2 import Environment, FileSystemLoader

from lib.item import Items
from lib.model.smartplugin import SmartPluginWebIf


class WebInterface(SmartPluginWebIf):
    """
    Webinterface for the Open-Meteo plugin
    """

    def __init__(self, webif_dir, plugin):
        """
        Initialization of the web interface

        :param webif_dir: directory where the webinterface of the plugin resides
        :param plugin: instance of the plugin
        :type webif_dir: str
        :type plugin: object
        """
        self.logger = plugin.logger
        self.webif_dir = webif_dir
        self.plugin = plugin
        self.items = Items.get_instance()

        self.tplenv = self.init_template_environment()

    @cherrypy.expose
    def index(self, reload=None):
        """
        Build index.html for cherrypy

        :return: contents of the template after being rendered
        """
        tmpl = self.tplenv.get_template('index.html')

        item_list = []
        for item in self.plugin.get_item_list():
            if item is self.plugin._pause_item:
                continue
            item_list.append(item)

        return tmpl.render(
            p=self.plugin,
            items=sorted(item_list, key=lambda k: str.lower(k['_path'])),
            item_count=len(item_list),
        )

    @cherrypy.expose
    def get_data_html(self, dataSet=None):
        """
        Return data to update the webpage via SHNG auto-refresh.

        :param dataSet: Dataset for which the data should be returned
        :return: JSON string with the data needed to update the web page.
        """
        if dataSet is None:
            now = int(time.time())
            fetch_ago = now - getattr(self.plugin, 'last_fetch_ts', now)

            data = {
                '_status': 'alive' if self.plugin.alive else 'stopped',
                '_fetch_ago': fetch_ago,
            }

            for item in self.plugin.get_item_list():
                if item is self.plugin._pause_item:
                    continue
                data[item._path] = item()

            return json.dumps(data)

        return '{}'

    @cherrypy.expose
    def force_update(self):
        """
        Trigger an immediate data refresh from the web UI.
        """
        if self.plugin.alive:
            self.plugin.force_update()
        return '{}'
