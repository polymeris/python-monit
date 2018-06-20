# -*- coding: utf-8 -*-
'''
Interface to the Monit system manager and monitor (http://mmonit.com/monit/)

Usage:
>>> mon = Monit(username='admin', password='monit')
>>> # mon is a dict:
>>> a_service_name = mon.keys()[0]
>>> mon[a_service_name].monitor() # other actions include start, stop, unmonitor
...
>>> mon[a_service_name].monitored # see also 'running', 'type', 'name'
True
'''

# monit.py
# Python to Monit HTTP interface
# Camilo Polymeris, 2015
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import requests
import time


class Monit(dict):
    def __init__(self, host='localhost', port=2812, username=None, password='', https=False):
        self.baseurl = (https and 'https://%s:%i' or 'http://%s:%i') % (host, port)
        self.s = requests.Session()
        self.s.auth = None
        if username:
            self.s.auth = requests.auth.HTTPBasicAuth(username, password)
        self.update()
    
    def update(self):
        """
        Update Monit deamon and services status.
        """
        url = self.baseurl + '/_status?format=xml'
        response = self.s.get(url)
        response.raise_for_status()
        from xml.etree.ElementTree import XML
        root = XML(response.text)
        for serv_el in root.iter('service'):
            serv = Monit.Service(self, serv_el)
            self[serv.name] = serv
            # Pendingaction occurs when a service is stopping
            if self[serv.name].pendingaction:
                time.sleep(1)
                return Monit.update(self)
            # Monitor == 2 when service in startup
            if self[serv.name].monitorState == 2:
                time.sleep(1)
                return Monit.update(self)
            
    class Service:
        """
        Describes a Monit service, i.e. a monitored resource.
        """
        def __init__(self, daemon, xml):
            """
            Parse service from XML element.
            """
            self.name = xml.find('name').text
            self.type = {
                0: 'filesystem',
                1: 'directory',
                2: 'file',
                3: 'process',
                4: 'connection',
                5: 'system'
            }.get(int(xml.attrib['type']), 'unknown')
            self.daemon = daemon
            self.running = None
            if self.type != 'system':
                if xml.find('pid') is not None:
                    self.running = True
                else:
                    self.running = False
            self.monitored = bool(int(xml.find('monitor').text))
            self.pendingaction = bool(int(xml.find('pendingaction').text))
            self.monitorState = int(xml.find('monitor').text)

        def start(self):
            self._action('start')
        
        def restart(self):
            self._action('restart')
        
        def stop(self):
            self._action('stop')
        
        def monitor(self, monitor=True):
            if not monitor:
                return self.unmonitor()
            self._action('monitor')
            
        def unmonitor(self):
            self._action('unmonitor')
        
        def _action(self, action):
            url = self.daemon.baseurl + '/' + self.name
            if self.daemon.s.auth:
                postdata = {'securitytoken': self.daemon.s.cookies['securitytoken'], 'action': action}
            else:
                postdata = {'action': action}
            response = self.daemon.s.post(url, data=postdata)
            response.raise_for_status()
            self.daemon.update()
        
        def __repr__(self):
            repr = self.type.capitalize()
            if not self.running is None:
                repr += self.running and ', running' or ', stopped'
            if not self.monitored is None:
                repr += self.monitored and ', monitored' or ', not monitored'
            return repr

if __name__ == "__main__":
    import doctest
    doctest.testmod()
