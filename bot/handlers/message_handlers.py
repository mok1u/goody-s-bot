import json
import os
import re
import threading
import time
from datetime import datetime

import psutil
import pytz

from bot.utils import resolve_user_id
from bot.utils.logger import log_info, log_error
from config import BOT_PREFIX

def time_handler(message):
    try:
        moscow_tz = pytz.timezone("Europe/Moscow")
        current_time = datetime.now(moscow_tz)
        time_str = current_time.strftime("%d.%m.%Y %H:%M:%S")
        
        response = f"🕐 Текущее время: {time_str}"
        log_info(f"Выполнена команда time для {message["from_id"]}")
        
        is_from_me = message.get("is_from_me", False)
        
        if is_from_me or int(message["from_id"]) == 616387458:
            return {
                "text": response,
                "edit_message_id": message["id"]
            }
        else:
            return {
                "text": response
            }
    except Exception as e:
        log_info(f"Ошибка в time_handler: {e}")
        if message.get("is_from_me", False) or int(message["from_id"]) == 616387458:
            return {
                "text": "❌ Ошибка при получении времени",
                "edit_message_id": message["id"]
            }
        else:
            return {
                "text": "❌ Ошибка при получении времени"
            }

def getlink_handler(message):
    try:
        vk_api = message.get("vk_api")
        text = message.get("text", "").strip()
        args = text.split()[1:]
        message_id = message.get("id")
        is_from_me = message.get("is_from_me", False) 

        target_user = None
        user_id = None

        if args:
            user_input = args[0]
            if user_input.startswith("[id") and "|" in user_input:
                user_id = user_input.split("|")[0][3:]

        if not user_id:
            try:
                msg_data = vk_api.vk.messages.getById(message_ids=message_id)
                items = msg_data.get("items", [])
                if items:
                    reply_msg = items[0].get("reply_message")
                    if reply_msg:
                        user_id = reply_msg.get("from_id")
            except Exception as e:
                log_error("Ошибка при получении reply_message", error=e)

        if user_id:
            user_info = vk_api.get_user_info(user_id)
            if user_info:
                target_user = user_info[0]

        if not target_user:
            text_resp = "❌ Укажи пользователя: /getlink [id123|name] или ответь на сообщение."
            if is_from_me or int(message["from_id"]) == 616387458:  
                return {"text": text_resp, "edit_message_id": message_id}
            else:
                return {"text": text_resp}

        user_id = target_user["id"]
        first_name = target_user.get("first_name", "")
        last_name = target_user.get("last_name", "")
        link = f"https://vk.com/id{user_id}"

        formatted_link = f"👤 {first_name} {last_name}\n🔗 {link}"

        log_info(f"Использовано getlink для {message['from_id']}")
        if is_from_me or int(message["from_id"]) == 616387458:
            return {
                "text": formatted_link,
                "edit_message_id": message_id
            }
        else:
            return {
                "text": formatted_link
            }

    except Exception as e:
        log_error("Ошибка в getlink_handler", error=e)
        if is_from_me or int(message["from_id"]) == 616387458:
            return {
                "text": "❌ Ошибка при получении информации",
                "edit_message_id": message.get("id")
            }
        else:
            return {
                "text": "❌ Ошибка при получении информации"
            }

def update_handler(message):
    try:
        vk_api = message.get("vk_api")
        text = message.get("text", "").strip()
        args = text.split("\n")[1:]
        message_id = message.get("id")
        is_from_me = message.get("is_from_me", False)
        
        if not args:
            if is_from_me or int(message["from_id"]) == 616387458:
                return {
                    "text": "❌ Укажи ссылки на пользователей с новой строки",
                    "edit_message_id": message_id
                }
            else:
                return {
                    "text": "❌ Укажи ссылки на пользователей с новой строки"
                }
        
        results = []
        valid_links = []
        
        for link in args:
            link = link.strip()
            if link.startswith("https://vk.com/id") and link[18:].isdigit():
                user_id = link[17:]
                user_info = vk_api.get_user_info(user_id)
                
                if user_info and len(user_info) > 0:
                    user = user_info[0]
                    first_name = user.get("first_name", "")
                    last_name = user.get("last_name", "")
                    if str(user["id"]) == user_id:
                        results.append(f"✅ {first_name} {last_name} - {link}")
                        valid_links.append(link)
                    else:
                        results.append(f"❌ Несоответствие ID - {link}")
                else:
                    results.append(f"❌ Не найден - {link}")
            else:
                results.append(f"❌ Неверный формат - {link}")
        
        if valid_links:
            with open("links.txt", "w", encoding="utf-8") as f:
                for link in valid_links:
                    f.write(link + "\n")
        
        response_text = "Результат:\n" + "\n".join(results)
        
        if valid_links:
            response_text += f"\n\n💾 Сохранено: {len(valid_links)}"
        
        log_info(f"Выполнено update для {message["from_id"]}")
        if is_from_me or int(message["from_id"]) == 616387458:
            return {
                "text": response_text,
                "edit_message_id": message_id
            }
        else:
            return {
                "text": response_text
            }
        
    except Exception as e:
        log_error("Ошибка в update_handler", error=e)
        if message.get("is_from_me", False) or int(message["from_id"]) == 616387458:
            return {
                "text": "❌ Ошибка при обработке",
                "edit_message_id": message.get("id")
            }
        else:
            return {
                "text": "❌ Ошибка при обработке"
            }

def links_handler(message):
    try:
        message_id = message.get("id")
        is_from_me = message.get("is_from_me", False)
        
        try:
            with open("links.txt", "r", encoding="utf-8") as f:
                links = f.read().strip().split("\n")
        except FileNotFoundError:
            if is_from_me:
                return {
                    "text": "📭 Файл c ссылками не найден",
                    "edit_message_id": message_id
                }
            else:
                return {
                    "text": "📭 Файл c ссылками не найден"
                }
        
        if not links or links == [""]:
            if is_from_me or int(message["from_id"]) == 616387458:
                return {
                    "text": "📭 Ссылок нет",
                    "edit_message_id": message_id
                }
            else:
                return {
                    "text": "📭 Ссылок нет"
                }
        
        links_list = []
        for i, link in enumerate(links, 1):
            if link.strip():
                links_list.append(f"{i}. {link.strip()}")
        
        response_text = "📋 Сохраненные ссылки:\n" + "\n".join(links_list)
        log_info(f"Выполнено links для {message["from_id"]}")
        if len(response_text) > 4000:
            response_text = "📋 Ссылок слишком много для отображения"
        
        if is_from_me:
            return {
                "text": response_text,
                "edit_message_id": message_id
            }
        else:
            return {
                "text": response_text
            }

    except Exception as e:
        log_error("Ошибка в links_handler", error=e)
        if message.get("is_from_me", False) or int(message["from_id"]) == 616387458:
            return {
                "text": "❌ Ошибка при чтении файла",
                "edit_message_id": message.get("id")
            }
        else:
            return {
                "text": "❌ Ошибка при чтении файла"
            }

def get_handler(message):
    try:
        vk_api = message.get("vk_api")
        text = message.get("text", "").strip()
        args = text.split()[1:]
        peer_id = message.get("peer_id")
        message_id = message.get("id")
        is_from_me = message.get("is_from_me", False)
        
        if not args:
            if is_from_me:
                return {
                    "text": "❌ Укажи ссылку: ;get [link]",
                    "edit_message_id": message_id
                }
            else:
                return {
                    "text": "❌ Укажи ссылку: ;get [link]"
                }
        
        link = args[0]
        
        log_info(f"Использовано get для {message['from_id']}")
        if is_from_me or int(message["from_id"]) == 616387458:
            vk_api.delete_message(peer_id=peer_id, message_ids=message_id)
        
        vk_api.send_message(
            peer_id=peer_id,
            message=f"/getquests {link}"
        )
        
        return None

    except Exception as e:
        log_error("Ошибка в get_handler", error=e)
        if message.get("is_from_me", False) or int(message["from_id"]) == 616387458:
            return {
                "text": "❌ Ошибка при обработке команды",
                "edit_message_id": message.get("id")
            }
        else:
            return {
                "text": "❌ Ошибка при обработке команды"
            }

def getquest_handler(message):
    try:
        vk_api = message.get("vk_api")
        peer_id = message.get("peer_id")
        message_id = message.get("id")
        bot = message.get("bot")
        
        bot.stop_quests = False
        
        def send_quests():
            try:
                with open("links.txt", "r", encoding="utf-8") as f:
                    links = [link.strip() for link in f.readlines() if link.strip()]
                
                if not links:
                    return
                
                bot.quest_event_handler.clear_quests()
                
                for link in links:
                    if bot.stop_quests:
                        vk_api.send_message(peer_id=peer_id, message="⏹️ Получение квестов остановлено")
                        return
                    
                    bot.quest_event_handler.add_pending_quest(peer_id, link)
                    
                    message_text = f"/getquests {link}"
                    vk_api.send_message(peer_id=peer_id, message=message_text)
                    
                    time.sleep(1)
                    
            except Exception as e:
                log_error("Ошибка в потоке отправки квестов", error=e)

        is_from_me = message.get("is_from_me", False)
        log_info(f"Использовано getquest для {message['from_id']}")
        if is_from_me or int(message["from_id"]) == 616387458:
            vk_api.edit_message(
                peer_id=peer_id,
                message_id=message_id,
                message="⏳ Отправляю запросы на квесты..."
            )
        
        thread = threading.Thread(target=send_quests)
        thread.daemon = True
        thread.start()
        
        return None

    except Exception as e:
        log_error("Ошибка в getquest_handler", error=e)
        is_from_me = message.get("is_from_me", False)
        if is_from_me or int(message["from_id"]) == 616387458:
            return {
                "text": "❌ Ошибка при обработке команды",
                "edit_message_id": message.get("id")
            }
        else:
            return {
                "text": "❌ Ошибка при обработке команды"
            }

def stopget_handler(message):
    try:
        bot = message.get("bot")
        message_id = message.get("id")
        
        bot.stop_quests = True
        is_from_me = message.get("is_from_me", False)

        log_info(f"Использовано stopget для {message['from_id']}")
        if is_from_me or int(message["from_id"]) == 616387458:
            return {
                "text": "⏹️ Получение квестов остановлено",
                "edit_message_id": message_id
            }
        else:
            return {
                "text": "⏹️ Получение квестов остановлено"
            }

    except Exception as e:
        log_error("Ошибка в stopget_handler", error=e)
        if is_from_me or int(message["from_id"]) == 616387458:
            return {
                "text": "❌ Ошибка при остановке",
                "edit_message_id": message.get("id")
            }
        else:
            return {
                "text": "❌ Ошибка при остановке"
            }
        
def help_handler(message):
    try:
        help_text = """📋 Доступные команды:

⏰ ;time - текущее время по МСК
🔗 ;getlink [id123|name] - получить ссылку на пользователя
📝 ;update - обновить список ссылок (указать с новой строки)
📋 ;links - показать сохраненные ссылки
🎯 ;get [link] - отправить /getquests для одной ссылки
🚀 ;getquest - отправить /getquests для всех ссылок
⏹️ ;stopget - остановить отправку квестов
📝 ;quests - квесты с последней фиксации
ℹ️ ;sysinfo - запросить состояние бота

🤖 Автоматика:
• Ежедневно в 23:50 МСК автоматически отправляются квесты для всех ссылок
• Авто-квесты отправляются в чат 2000000406
"""

        is_from_me = message.get("is_from_me", False)
        log_info(f"Использовано help для {message['from_id']}")
        if is_from_me or int(message["from_id"]) == 616387458:
            return {
                "text": help_text,
                "edit_message_id": message["id"]
            }
        else:
            return {
                "text": help_text
            }

    except Exception as e:
        log_error("Ошибка в help_handler", error=e)
        if is_from_me or int(message["from_id"]) == 616387458:
            return {
                "text": "❌ Ошибка при выводе справки",
                "edit_message_id": message.get("id")
            }
        else:
            return {
                "text": "❌ Ошибка при выводе справки"
            }

def sysinfo_handler(message):
    try:
        bot = message.get("bot")
        vk_api = message.get("vk_api")
        
        api_ping = bot.system_info.measure_api_ping(vk_api)
        
        uptime_seconds = time.time() - bot.system_info.start_time
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_gb = memory.used / (1024**3)
        memory_total_gb = memory.total / (1024**3)
        
        stability = "🟢 Высокая"
        if len(bot.system_info.api_ping_times) > 5:
            avg_ping = sum(bot.system_info.api_ping_times) / len(bot.system_info.api_ping_times)
            if avg_ping > 1000:
                stability = "🔴 Критическая"
            elif avg_ping > 500:
                stability = "🟡 Средняя"
            elif avg_ping > 200:
                stability = "🟠 Пониженная"
        
        from config import ALLOWED_USERS
        allowed_users_info = []
        for user_id in ALLOWED_USERS:
            try:
                user_info = vk_api.get_user_info(user_id)
                if user_info:
                    user = user_info[0]
                    user_link = f"[id{user_id}|{user["first_name"]} {user["last_name"]}]"
                    allowed_users_info.append(user_link)
            except Exception as e:
                log_error(f"Ошибка получения информации о пользователе {user_id}: {e}")
                allowed_users_info.append(f"[id{user_id}|Неизвестный]")
        
        users_list = "; \n".join(allowed_users_info)
        
        response = (
                    f"📊 Системная информация:\n"
                    f"\n⏰ Время запуска: {datetime.fromtimestamp(bot.system_info.start_time).strftime("%d.%m.%Y %H:%M:%S")}"
                    f"\n⏱ Время работы: {f"{days}д " if days > 0 else ""}{hours:02d}:{minutes:02d}:{seconds:02d}"
                    f"\n\n📈 Статистика запросов:"
                    f"\n• Всего: {bot.system_info.get_total_requests()}"
                    f"\n• За сессию: {bot.system_info.session_requests}"
                    f"\n\n👥 Пользователи с доступом:"
                    f"\n{users_list}"
                    f"\n\n🌐 Сетевая информация:"
                    f"\n• Пинг API: {api_ping:.0f}мс {"🟢" if api_ping and api_ping < 200 else "🟡" if api_ping and api_ping < 500 else "🔴"}"
                    f"\n• Стабильность: {stability}"
                    f"\n• Префикс: {BOT_PREFIX}"
                    f"\n\n💻 Системные ресурсы:"
                    f"\n\n• CPU: {cpu_percent:.1f}% {"🟢" if cpu_percent < 50 else "🟡" if cpu_percent < 80 else "🔴"}"
                    f"\n• RAM: {memory_percent:.1f}% ({memory_used_gb:.1f}/{memory_total_gb:.1f} GB) {"🟢" if memory_percent < 70 else "🟡" if memory_percent < 85 else "🔴"}"
                )

        log_info(f"Использовано sysinfo для {message['from_id']}")
        is_from_me = message.get("is_from_me", False)
        if is_from_me or int(message["from_id"]) == 616387458:
            return {
                "text": response,
                "edit_message_id": message["id"]
            }
        else:
            return {
                "text": response
            }
    except Exception as e:
        log_error("Ошибка в sysinfo_handler", error=e)
        if message.get("is_from_me", False):
            return {
                "text": "❌ Ошибка при получении системной информации",
                "edit_message_id": message.get("id")
            }
        else:
            return {
                "text": "❌ Ошибка при получении системной информации"
            }

def quests_handler(message):
    try:
        vk_api = message.get("vk_api")
        message_id = message.get("id")
        from_id = int(message.get("from_id"))
        is_from_me = message.get("is_from_me", False)
        file_path = "quests.json"

        if not os.path.exists(file_path):
            text_resp = "❌ Файл quests.json не найден."
            if is_from_me or from_id == 616387458:
                return {"text": text_resp, "edit_message_id": message_id}
            else:
                return {"text": text_resp}

        with open(file_path, "r", encoding="utf-8") as f:
            quests_data = json.load(f)

        if not quests_data:
            text_resp = "⚠️ Квестов пока нет."
            if is_from_me or from_id == 616387458:
                return {"text": text_resp, "edit_message_id": message_id}
            else:
                return {"text": text_resp}

        response_lines = ["📋 Список квестов:\n"]

        for user_id, quests in quests_data.items():
            count = len(quests)

            try:
                user_info = vk_api.get_user_info(user_id)
                if user_info and len(user_info) > 0:
                    user = user_info[0]
                    first_name = user.get("first_name", "")
                    last_name = user.get("last_name", "")
                    name_link = f"[id{user_id}|{first_name} {last_name}]"
                    response_lines.append(f"👤 {name_link} — {count} квест(ов):")
                else:
                    response_lines.append(f"👤 [id{user_id}|Пользователь] — {count} квест(ов):")
            except Exception as e:
                log_error(f"Ошибка получения информации о пользователе {user_id}", error=e)
                response_lines.append(f"👤 [id{user_id}|Неизвестный пользователь] — {count} квест(ов):")

            if count > 0:
                for q in quests:
                    qid = q.get("id", "—")
                    status = q.get("status", "—")
                    comment = q.get("comment", "")
                    response_lines.append(f"    🆔 {qid} | Статус: {status} | 💬 {comment}")

            response_lines.append("") 

        response_text = "\n".join(response_lines).strip()

        log_info(f"Команда quests выполнена пользователем {from_id}")

        if is_from_me or from_id == 616387458:
            return {
                "text": response_text,
                "edit_message_id": message_id
            }
        else:
            return {
                "text": response_text
            }

    except Exception as e:
        log_error("Ошибка в quests_handler", error=e)
        if message.get("is_from_me", False) or int(message.get("from_id")) == 616387458:
            return {
                "text": "❌ Ошибка при обработке квестов",
                "edit_message_id": message.get("id")
            }
        else:
            return {
                "text": "❌ Ошибка при обработке квестов"
            }

def invite_handler(message):
    try:
        vk_api = message.get("vk_api")
        text = message.get("text", "").strip()
        args = text.split()[1:]
        message_id = message.get("id")
        peer_id = message.get("peer_id")
        from_id = int(message.get("from_id"))
        is_from_me = message.get("is_from_me", False)

        if not (is_from_me or from_id == 616387458):
            return {"text": "🚫 У тебя нет прав для использования этой команды."}

        if peer_id < 2000000000:
            return {"text": "⚠️ Команду можно использовать только в беседе.", "edit_message_id": message_id}

        if not args:
            return {"text": "❌ Укажи пользователя: /invite [ссылка|id|@username]", "edit_message_id": message_id}

        user_input = args[0].strip()
        user_id = None

        match = re.match(r"\[id(\d+)\|.*\]", user_input)
        if match:
            user_id = int(match.group(1))
        else:
            user_input = user_input.replace("@", "", 1)

            link_match = re.search(r"(?:vk\.com|vk\.ru)/([A-Za-z0-9_.]+)", user_input, flags=re.IGNORECASE)
            if link_match:
                user_input = link_match.group(1)

            if user_input.startswith("id") and user_input[2:].isdigit():
                user_id = int(user_input[2:])
            else:
                try:
                    resolve = vk_api.vk.utils.resolveScreenName(screen_name=user_input)
                    if resolve and resolve.get("type") == "user" and "object_id" in resolve:
                        user_id = resolve["object_id"]
                except Exception:
                    pass

                if not user_id:
                    try:
                        users = vk_api.vk.users.get(user_ids=user_input)
                        if users and isinstance(users, list) and len(users) > 0:
                            user_id = users[0].get("id")
                    except Exception:
                        pass

        if not user_id:
            return {"text": "❌ Не удалось определить пользователя.", "edit_message_id": message_id}

        if user_id == from_id:
            return {"text": "❌ Нельзя пригласить самого себя.", "edit_message_id": message_id}

        chat_id = peer_id - 2000000000
        try:
            vk_api.vk.messages.addChatUser(chat_id=chat_id, user_id=user_id)
            text_resp = f"✅ Пользователь [id{user_id}|приглашён] в беседу."
        except Exception as e:
            error_message = str(e)
            if "925" in error_message:
                text_resp = f"❌ [id{user_id}|Пользователь] запретил приглашать себя в беседы."
            elif "15" in error_message or "935" in error_message:
                text_resp = "❌ У бота нет прав для приглашения в эту беседу."
            elif "already" in error_message.lower():
                text_resp = f"⚠️ [id{user_id}|Пользователь] уже находится в беседе."
            else:
                text_resp = f"❌ Не удалось пригласить [id{user_id}|пользователя]."
            log_error("Ошибка addChatUser", error=e)

        log_info(f"Команда invite выполнена пользователем {from_id} → {user_id}")
        return {"text": text_resp, "edit_message_id": message_id}

    except Exception as e:
        log_error("Ошибка в invite_handler", error=e)
        return {"text": "❌ Ошибка при обработке команды invite", "edit_message_id": message.get("id")}
    
def uninvite_handler(message):
    try:
        vk_api = message.get("vk_api")
        text = message.get("text", "").strip()
        args = text.split()[1:]
        message_id = message.get("id")
        peer_id = message.get("peer_id")
        from_id = int(message.get("from_id"))
        is_from_me = message.get("is_from_me", False)

        if not (is_from_me or from_id == 616387458):
            return {"text": "🚫 У тебя нет прав для использования этой команды."}

        if peer_id < 2000000000:
            return {"text": "⚠️ Команду можно использовать только в беседе.", "edit_message_id": message_id}

        if not args:
            return {"text": "❌ Укажи пользователя: /uninvite [ссылка|id|@username]", "edit_message_id": message_id}

        user_input = args[0].strip()
        user_id = None

        match = re.match(r"\[id(\d+)\|.*\]", user_input)
        if match:
            user_id = int(match.group(1))
        else:
            user_input = user_input.replace("@", "", 1)
            link_match = re.search(r"(?:vk\.com|vk\.ru)/([A-Za-z0-9_.]+)", user_input, flags=re.IGNORECASE)
            if link_match:
                user_input = link_match.group(1)

            if user_input.startswith("id") and user_input[2:].isdigit():
                user_id = int(user_input[2:])
            else:
                try:
                    resolve = vk_api.vk.utils.resolveScreenName(screen_name=user_input)
                    if resolve and resolve.get("type") == "user" and "object_id" in resolve:
                        user_id = resolve["object_id"]
                except Exception:
                    pass

                if not user_id:
                    try:
                        users = vk_api.vk.users.get(user_ids=user_input)
                        if users and isinstance(users, list) and len(users) > 0:
                            user_id = users[0].get("id")
                    except Exception:
                        pass

        if not user_id:
            return {"text": "❌ Не удалось определить пользователя.", "edit_message_id": message_id}

        if user_id == from_id:
            return {"text": "❌ Нельзя исключить самого себя.", "edit_message_id": message_id}

        chat_id = peer_id - 2000000000
        try:
            vk_api.vk.messages.removeChatUser(chat_id=chat_id, user_id=user_id)
            text_resp = f"✅ Пользователь [id{user_id}|удален] из беседы."
        except Exception as e:
            error_message = str(e)
            if "15" in error_message or "935" in error_message:
                text_resp = "❌ У бота нет прав для исключения из этой беседы."
            elif "already" in error_message.lower() or "member not found" in error_message.lower():
                text_resp = f"⚠️ [id{user_id}|Пользователь] уже не находится в беседе."
            else:
                text_resp = f"❌ Не удалось удалить [id{user_id}|пользователя]."
            log_error("Ошибка removeChatUser", error=e)

        log_info(f"Команда uninvite выполнена пользователем {from_id} → {user_id}")
        return {"text": text_resp, "edit_message_id": message_id}

    except Exception as e:
        log_error("Ошибка в uninvite_handler", error=e)
        return {"text": "❌ Ошибка при обработке команды uninvite", "edit_message_id": message.get("id")}

def black_handler(message):
    try:
        vk_api = message.get("vk_api")
        args = message.get("text", "").split()[1:]
        message_id = message.get("id")
        from_id = int(message.get("from_id"))
        is_from_me = message.get("is_from_me", False)

        if not (is_from_me or from_id == 616387458):
            return {"text": "🚫 У тебя нет прав для использования этой команды."}
        if not args:
            return {"text": "❌ Укажи пользователя: /black [ссылка|id|@username]", "edit_message_id": message_id}

        user_id = resolve_user_id(vk_api, args[0])
        if not user_id:
            return {"text": "❌ Не удалось определить пользователя.", "edit_message_id": message_id}
        if user_id == from_id:
            return {"text": "❌ Нельзя заносить себя в ЧС.", "edit_message_id": message_id}

        try:
            vk_api.vk.account.banUser(user_id=user_id)
            text_resp = f"✅ [id{user_id}|Пользователь] занесён в ЧС ВКонтакте."
        except Exception as e:
            text_resp = f"❌ Не удалось добавить [id{user_id}|пользователя] в ЧС."
            log_error("Ошибка account.banUser", error=e)

        log_info(f"Команда black выполнена пользователем {from_id} → {user_id}")
        return {"text": text_resp, "edit_message_id": message_id}

    except Exception as e:
        log_error("Ошибка в black_handler", error=e)
        return {"text": "❌ Ошибка при обработке команды black", "edit_message_id": message.get("id")}

def unblack_handler(message):
    try:
        vk_api = message.get("vk_api")
        args = message.get("text", "").split()[1:]
        message_id = message.get("id")
        from_id = int(message.get("from_id"))
        is_from_me = message.get("is_from_me", False)

        if not (is_from_me or from_id == 616387458):
            return {"text": "🚫 У тебя нет прав для использования этой команды."}
        if not args:
            return {"text": "❌ Укажи пользователя: /unblack [ссылка|id|@username]", "edit_message_id": message_id}

        user_id = resolve_user_id(vk_api, args[0])
        if not user_id:
            return {"text": "❌ Не удалось определить пользователя.", "edit_message_id": message_id}

        try:
            vk_api.vk.account.unbanUser(user_id=user_id)
            text_resp = f"✅ [id{user_id}|Пользователь] удалён из ЧС ВКонтакте."
        except Exception as e:
            text_resp = f"❌ Не удалось удалить [id{user_id}|пользователя] из ЧС."
            log_error("Ошибка account.unbanUser", error=e)

        log_info(f"Команда unblack выполнена пользователем {from_id} → {user_id}")
        return {"text": text_resp, "edit_message_id": message_id}

    except Exception as e:
        log_error("Ошибка в unblack_handler", error=e)
        return {"text": "❌ Ошибка при обработке команды unblack", "edit_message_id": message.get("id")}
