import requests

class Monit:
    def __init__(self, host='localhost', port=2812, username=None, password='', https=False):
        self.services = {}
    
    def update(self):
        pass
            
    class Service:
        def __init__(self, parent, xml):
            self.running = None
            self.monitored = None
        
        def start(self):
            pass
        
        def stop(self):
            pass
        
        def monitor(self, monitor)
        pass
