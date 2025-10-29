import json
import os
import re
import time
from bot.utils.logger import log_info, log_error

class QuestEventHandler:
    def __init__(self):
        self.quests_file = 'quests.json'
        self.pending_quests = {}
        self.current_link = None
        
    def handle_event(self, event, bot):
        try:
            if not hasattr(event, 'text') or not event.text:
                return False
                
            text = event.text.strip()
            peer_id = getattr(event, 'peer_id', None)
            from_id = getattr(event, 'from_id', None)
            
            if not bot.stop_quests:
                
                if text.startswith('Квесты за день:') or text.startswith('Нет квестов за сегодняшний день'):
                    return self._parse_quests_response(text, peer_id)
                    
        except Exception as e:
            log_error(f"Ошибка в QuestEventHandler: {e}")
            
        return False
    
    def add_pending_quest(self, peer_id, link):
        if peer_id not in self.pending_quests:
            self.pending_quests[peer_id] = {}
        self.pending_quests[peer_id][link] = time.time()
        self.current_link = link
    
    def _parse_quests_response(self, text, peer_id):
        try:
            
            if not self.current_link and peer_id in self.pending_quests:
                current_time = time.time()
                for link, timestamp in self.pending_quests[peer_id].items():
                    if current_time - timestamp < 30:
                        self.current_link = link
                        break
            
            
            if not self.current_link:
                log_info("Нет текущей ссылки для парсинга")
                return False
            
            quests_data = self._load_quests()
            quests_list = []
            
            if text.strip() == "Нет квестов за сегодняшний день.":
                
                user_id = self.current_link.replace('https://vk.com/id', '')
                
                if user_id not in quests_data:
                    quests_data[user_id] = []
                
                self._save_quests(quests_data)
                
                if peer_id in self.pending_quests and self.current_link in self.pending_quests[peer_id]:
                    del self.pending_quests[peer_id][self.current_link]
                
                self.current_link = None
                return True
            
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                if line.startswith("'") and "' - " in line:
                    quest_match = self._parse_quest_line(line)
                    if quest_match:
                        quests_list.append(quest_match)
                    else:
                        log_info("Не удалось распарсить строку квеста")
            
            
            if quests_list:
                user_id = self.current_link.replace('https://vk.com/id', '')
                
                if user_id not in quests_data:
                    quests_data[user_id] = []
                
                quests_data[user_id].extend(quests_list)
                self._save_quests(quests_data)
                log_info(f"Сохранено {len(quests_list)} квестов для пользователя {user_id}")
                
                if peer_id in self.pending_quests and self.current_link in self.pending_quests[peer_id]:
                    del self.pending_quests[peer_id][self.current_link]
                
                self.current_link = None
                return True
                    
        except Exception as e:
            log_error(f"Ошибка парсинга квестов: {e}")
            
        return False
    
    def _parse_quest_line(self, line):
        try:
            clean_line = line.rstrip('-').strip()
            
            parts = clean_line.split("' - ", 1)
            if len(parts) < 2:
                log_info("Не удалось разделить строку на части")
                return None
                
            quest_id = parts[0].strip("'")
            rest = parts[1].strip()
            
            if not quest_id.isdigit():
                log_info(f"ID квеста не цифровой: {quest_id}")
                return None
            
            status = rest
            comment = ""
            
            if '(' in rest and ')' in rest:
                status_parts = rest.split('(', 1)
                status = status_parts[0].strip()
                comment = status_parts[1].rstrip(')').strip()
            
            
            return {
                'id': quest_id,
                'status': status,
                'comment': comment,
                'timestamp': time.time()
            }
            
        except Exception as e:
            log_error(f"Ошибка парсинга строки квеста '{line}': {e}")
        return None
    
    def _load_quests(self):
        try:
            if os.path.exists(self.quests_file):
                with open(self.quests_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            log_error(f"Ошибка загрузки квестов: {e}")
        return {}
    
    def _save_quests(self, quests_data):
        try:
            with open(self.quests_file, 'w', encoding='utf-8') as f:
                json.dump(quests_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log_error(f"Ошибка сохранения квестов: {e}")

    def clear_quests(self):
        try:
            with open(self.quests_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            log_info("Файл quests.json очищен")
        except Exception as e:
            log_error(f"Ошибка очистки quests.json: {e}")

quest_event_handler = QuestEventHandler()