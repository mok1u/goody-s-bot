from bot.core.vk_api import VKAPI
from bot.handlers.router import message_router
from bot.utils.logger import log_info, log_error, log_critical
from bot.utils.helpers import remove_pycache
from vk_api.longpoll import VkEventType
from bot.utils.system_info import SystemInfo
from bot.handlers.event_handlers import QuestEventHandler

import threading
import time
import pytz
from datetime import datetime

class VKBot:
    def __init__(self, access_token, allowed_users, api_version='5.199'):
        self.vk_api = VKAPI(access_token, api_version)
        self.allowed_users = allowed_users
        self.running = False
        self.stop_quests = False
        self.auto_quest_thread = None
        self.target_chat_id = 2000000406
        self.system_info = SystemInfo()
        self.quest_event_handler = QuestEventHandler()
        
    def start(self):
        log_info("Запуск страничного VK бота...")
        self.running = True
        
        self.auto_quest_thread = threading.Thread(target=self._auto_quest_scheduler)
        self.auto_quest_thread.daemon = True
        self.auto_quest_thread.start()
        
        try:
            log_info("Бот запущен и ожидает события")
            
            for event in self.vk_api.longpoll.listen():
                if not self.running:
                    break
                self.handle_event(event)
                    
        except Exception as e:
            log_critical("Критическая ошибка при запуске бота", error=e)
    
    def _auto_quest_scheduler(self):
        while self.running:
            try:
                moscow_tz = pytz.timezone('Europe/Moscow')
                now = datetime.now(moscow_tz)
                
                if now.hour == 23 and now.minute == 50:
                    log_info("Автоматический запуск getquest в чат 2000000406")
                    self.vk_api.send_message(peer_id=self.target_chat_id, message="Автоматическая фиксация квестов")
                    self._run_auto_quest()
                    time.sleep(70)
                else:
                    time.sleep(0.1)
                    
            except Exception as e:
                log_error("Ошибка в планировщике авто-квестов", error=e)
                time.sleep(60)
    
    def _run_auto_quest(self):
        peer_id = self.target_chat_id
        self.quest_event_handler.clear_quests()
        try:
            with open('links.txt', 'r', encoding='utf-8') as f:
                links = [link.strip() for link in f.readlines() if link.strip()]
            
            if not links:
                log_info("Нет ссылок для авто-квестов")
                return
            
            for link in links:
                if not self.running:
                    break
                
                self.quest_event_handler.add_pending_quest(peer_id, link)
                message_text = f"/getquests {link}"
                self.vk_api.send_message(peer_id=self.target_chat_id, message=message_text)
                time.sleep(3)
            
            self.vk_api.send_message(peer_id=self.target_chat_id, message="Квесты зафиксированы")
            self.vk_api.send_message(peer_id=self.target_chat_id, message="/botadmins")
            log_info("Авто-квесты завершены")
            
        except Exception as e:
            log_error("Ошибка в авто-квестах", error=e)
    
    def handle_event(self, event):
        try:
            if event.type != VkEventType.MESSAGE_NEW:
                return

            user_id = getattr(event, "user_id", None) or getattr(event, "from_id", None)
            is_from_me = getattr(event, "from_me", False)

            if self.quest_event_handler.handle_event(event, self):
                return

            if not (is_from_me or (user_id in self.allowed_users)):
                return

            message_data = {
                'from_id': user_id,
                'peer_id': event.peer_id,
                'text': event.text,
                'id': event.message_id,
                'vk_api': self.vk_api,
                'bot': self,
                'is_from_me': is_from_me
            }

            self.handle_message(message_data)
                    
        except Exception as e:
            log_error("Ошибка при обработке события", error=e)
        
    def stop(self):
        log_info("Остановка бота...")
        self.running = False

    def handle_message(self, message):
        try:
            peer_id = message['peer_id']
            
            response = message_router.route(message)
            
            if response:
                if 'edit_message_id' in response:
                    self.vk_api.edit_message(
                        peer_id=peer_id,
                        message_id=response['edit_message_id'],
                        message=response['text'],
                        keyboard=response.get('keyboard'),
                        attachment=response.get('attachment')
                    )
                else:
                    self.vk_api.send_message(
                        peer_id=peer_id,
                        message=response['text'],
                        keyboard=response.get('keyboard'),
                        attachment=response.get('attachment')
                    )
                    
        except Exception as e:
            log_error("Ошибка при обработке сообщения", error=e)

def main():
    from config import ACCESS_TOKEN, API_VERSION, ALLOWED_USERS
    
    remove_pycache()
    
    bot = VKBot(
        access_token=ACCESS_TOKEN,
        allowed_users=ALLOWED_USERS,
        api_version=API_VERSION
    )
    
    try:
        bot.start()
    except KeyboardInterrupt:
        log_info("Бот остановлен пользователем")
    except Exception as e:
        log_critical("Неожиданная ошибка", error=e)
    finally:
        bot.stop()

if __name__ == "__main__":
    main()