import os
import time
import random
import requests
import threading
from datetime import datetime
from django.conf import settings

class KeepAlive:
    def __init__(self):
        self.app_url = getattr(settings, 'DJANGO_BASE_URL', 'https://yappuccino.onrender.com')
        self.endpoint = '/health/'
        self.enabled = self._should_beOn()
        self.running = False
        self.thread = None
        
    def _should_beOn(self): return(not settings.DEBUG and ('onrender.com' in self.app_url or os.environ.get('RENDER'))) # prod mode onyl
    
    def start(self):
        if not self.enabled:
            print("kepe alive disabled | not in prod mode")
            return
            
        if self.running:
            print("| OK | keep alive alr RUNNING")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._keep_alive_loop,daemon=True)
        self.thread.start()
        print(f"django blog keep-alive started for {self.app_url}")
    
    def stop(self):
        self.running = False
        if self.thread:
            print("| STOPPED| dj keep alive stoppd")
        
    def _keep_alive_loop(self):
        while self.running:
            try:
                ping = requests.get(
                    f"{self.app_url}{self.endpoint}",
                    timeout=10,
                    headers={ 'uAgent': 'blog-keepalive/1.0','x-KeepAlive': 'true'}
                )
                
                if ping.status_code == 200:
                    print("| OK | blog self ping is ok")
                else:
                    print(f"| WARNING | ping returned {ping.status_code}")
                    
            except Exception as e:
                print(f"| X | blog self ping failed: {e}")
            
            if self.running:
                wtime = random.randint(60,540)
                mins, secs = divmod(wtime,60)
                print(f"dj waiting {mins} mins {secs} secs til next ping")
                
                for _ in range(wtime):
                    if not self.running:
                        break
                    time.sleep(1)


djKeepAlive = KeepAlive()