import requests

class Monit:
    def __init__(self, host='localhost', port=2812, username=None, password='', https=False):
        self.services = {}
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
            self.services[serv.name] = serv
            
    class Service:
        def __init__(self, parent, xml):
            self.name = xml.find('name').text
            self.running = None
            self.monitored = None
        
        def start(self):
            pass
        
        def stop(self):
            pass
        
        def monitor(self, monitor):
            pass
