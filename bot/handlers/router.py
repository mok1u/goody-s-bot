from bot.handlers.message_handlers import (
    time_handler, 
    getlink_handler,
    help_handler,
    sysinfo_handler,
    invite_handler,
    uninvite_handler,
    black_handler,
    unblack_handler
)
from bot.handlers.quests_module import (
    update_handler,
    links_handler,
    get_handler,
    getquest_handler,
    stopget_handler,
    quests_handler,
    infoquest_handler
)
from config import BOT_PREFIX

class MessageRouter:
    def __init__(self):
        self.handlers = {}
        
    def register_handler(self, command, handler):
        self.handlers[command] = handler
        
    def route(self, message):
        text = message.get('text', '').strip()
        
        if BOT_PREFIX and text.startswith(BOT_PREFIX):
            full_command = text[len(BOT_PREFIX):].strip()
            command_parts = full_command.split()

            if not command_parts:
                return None
                
            command = command_parts[0].lower()
            
            handler = self.handlers.get(command)
            if handler:
                bot = message.get('bot')
                if bot and hasattr(bot, 'system_info'):
                    bot.system_info.add_request()
                return handler(message)
        
        return None

message_router = MessageRouter()

message_router.register_handler("time", time_handler)
message_router.register_handler("getlink", getlink_handler)
message_router.register_handler("update", update_handler)
message_router.register_handler("links", links_handler)
message_router.register_handler("get", get_handler)
message_router.register_handler("getquest", getquest_handler)
message_router.register_handler("stopget", stopget_handler)
message_router.register_handler("help", help_handler)
message_router.register_handler("sysinfo", sysinfo_handler)
message_router.register_handler("quests", quests_handler)
message_router.register_handler('invite', invite_handler)
message_router.register_handler('uninvite', uninvite_handler)
message_router.register_handler('black', black_handler)
message_router.register_handler('unblack', unblack_handler)
message_router.register_handler('checkquests', infoquest_handler)
