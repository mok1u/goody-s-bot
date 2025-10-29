import os
import shutil
import re
from config import ACCESS_TOKEN
import vk_api

vk_session = vk_api.VkApi(token=ACCESS_TOKEN)
vk = vk_session.get_api()

def remove_pycache():
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            shutil.rmtree(pycache_path)

remove_pycache()

def get_id(mention: str):
        mention = mention.strip()
        
        id_patterns = [
            r'^(?:https?://)?(?:vk\.com|vk\.ru)/id(\d+)$',
            r'^id(\d+)$', 
            r'^\[id(\d+)\|'
        ]
        
        for pattern in id_patterns:
            match = re.match(pattern, mention, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        username_patterns = [
            r'^(?:https?://)?(?:vk\.com|vk\.ru)/([a-zA-Z0-9_.]+)$',
            r'^@?([a-zA-Z0-9_.]+)$',
            r'^\*([a-zA-Z0-9_.]+)$',
            r'^\[id\d+\|[@*]?([a-zA-Z0-9_.]+)\]$'
        ]
        
        for pattern in username_patterns:
            match = re.match(pattern, mention, re.IGNORECASE)
            if match:
                username = match.group(1)
                
                if username.isdigit():
                    return int(username)
                
                if vk:
                    try:
                        users_info = vk.users.get(user_ids=username)
                        return users_info[0]['id'] if users_info else None
                    except:
                        pass
        
        return None
