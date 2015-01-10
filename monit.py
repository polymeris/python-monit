# -*- coding: utf-8 -*-
#
# monit.py
# Python to Monit HTTP interface
# Camilo Polymeris, 2015
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import requests

class Monit(dict):
    def __init__(self, host='localhost', port=2812, username=None, password='', https=False):
        self.baseurl = (https and 'https://%s:%i' or 'http://%s:%i') % (host, port)
        self.auth = None
        if username:
            self.auth = requests.auth.HTTPBasicAuth(username, password)
        self.update()
    
    def update(self):
        url = self.baseurl + '/_status?format=xml'
        response = requests.get(url, auth=self.auth)
        from xml.etree.ElementTree import XML
        root = XML(response.text)
        for serv_el in root.iter('service'):
            serv = Monit.Service(self, serv_el)
            self[serv.name] = serv
            
    class Service:     
        def __init__(self, parent, xml):
            self.name = xml.find('name').text
            self.type = {
                None: "unknown",
                0: "filesystem",
                1: "directory",
                2: "file",
                3: "process",
                4: "connection",
                5: "system"
            }.get(int(xml.attrib['type']), None)
            self.parent = parent
            self.running = None
            self.monitored = bool(int(xml.find('monitor').text))
        
        def start(self):
            self._action('start')
        
        def stop(self):
            self._action('stop')
        
        def monitor(self, monitor=True):
            if not monitor:
                return self.unmonitor()
            self._action('monitor')
            
        def unmonitor(self):
            self._action('_unmonitor')
        
        def _action(self, action):
            url = self.parent.baseurl + '/' + self.name
            requests.post(url, auth=self.parent.auth, data={'action': action})
            self.parent.update()
        
        def __repr__(self):
            repr = self.type.capitalize()
            if not self.running is None:
                repr += self.running and ', running' or ', stopped'
            if not self.monitored is None:
                repr += self.running and ', monitored' or ', not monitored'
            return repr
