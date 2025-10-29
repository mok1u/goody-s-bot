import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from bot.utils.logger import log_info, log_error

class VKAPI:
    def __init__(self, access_token, api_version='5.199'):
        self.vk_session = vk_api.VkApi(token=access_token, api_version=api_version)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)
        
    def send_message(self, peer_id, message, keyboard=None, attachment=None):
        try:
            params = {
                'peer_id': peer_id,
                'message': message,
                'random_id': vk_api.utils.get_random_id()
            }
            
            if keyboard:
                params['keyboard'] = keyboard
                
            if attachment:
                params['attachment'] = attachment
                
            self.vk.messages.send(**params)
            return True
            
        except Exception as e:
            log_error(f"Ошибка отправки сообщения {peer_id}", error=e)
            return False
    
    def edit_message(self, peer_id, message_id, message, keyboard=None, attachment=None):
        try:
            params = {
                'peer_id': peer_id,
                'message_id': message_id,
                'message': message,
                'random_id': vk_api.utils.get_random_id()
            }
            
            if keyboard:
                params['keyboard'] = keyboard
                
            if attachment:
                params['attachment'] = attachment
                
            self.vk.messages.edit(**params)
            return True
            
        except Exception as e:
            log_error(f"Ошибка редактирования сообщения {message_id}", error=e)
            return False

    def delete_message(self, peer_id, message_ids):
        try:
            params = {
                'peer_id': peer_id,
                'message_ids': message_ids,
                'delete_for_all': 1
            }
            self.vk.messages.delete(**params)
            return True
        except Exception as e:
            log_error(f"Ошибка удаления сообщения {message_ids}", error=e)
            return False

    def get_events(self):
        return self.longpoll.listen()
    
    def get_user_info(self, user_ids, fields=''):
        try:
            return self.vk.users.get(user_ids=user_ids, fields=fields)
        except Exception as e:
            log_error("Ошибка получения информации о пользователе", error=e)
            return None