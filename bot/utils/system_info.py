import time

from bot.utils.stats_manager import StatsManager

class SystemInfo:
    def __init__(self):
        self.start_time = time.time()
        self.stats_manager = StatsManager()
        self.session_requests = 0
        self.api_ping_times = []
        
    def add_request(self):
        self.stats_manager.add_request()
        self.session_requests += 1
        
    def get_total_requests(self):
        return self.stats_manager.get_total_requests()
        
    def measure_api_ping(self, vk_api):
        try:
            start = time.time()
            vk_api.get_user_info(1)
            ping = (time.time() - start) * 1000
            self.api_ping_times.append(ping)
            if len(self.api_ping_times) > 10:
                self.api_ping_times.pop(0)
            return ping
        except:
            return None
