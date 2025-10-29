import json
import os
from bot.utils.logger import log_error

class StatsManager:
    def __init__(self, stats_file='stats.json'):
        self.stats_file = stats_file
        self.stats = self._load_stats()
        
    def _load_stats(self):
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {'total_requests': 0}
        except Exception as e:
            log_error(f"Ошибка загрузки статистики: {e}")
            return {'total_requests': 0}
            
    def _save_stats(self):
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log_error(f"Ошибка сохранения статистики: {e}")
            
    def add_request(self):
        self.stats['total_requests'] = self.stats.get('total_requests', 0) + 1
        self._save_stats()
        
    def get_total_requests(self):
        return self.stats.get('total_requests', 0)