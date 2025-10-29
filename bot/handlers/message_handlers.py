import re
import time
from datetime import datetime

import psutil
import pytz

from bot.utils import resolve_user_id
from bot.utils.logger import log_error, log_info
from config import BOT_PREFIX


def getlink_handler(message):
    try:
        is_from_me = message.get("is_from_me", False)
        if not is_from_me or int(message["from_id"]) != 616387458:
            return
        vk_api = message.get("vk_api")
        text = message.get("text", "").strip()
        args = text.split()[1:]
        message_id = message.get("id")

        target_user = None
        user_id = None

        if args:
            user_input = args[0]
            user_id = resolve_user_id(mention=user_input)

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
            response = "❌ | Укажи пользователя: /getlink [Упоминание / ответ на сообщение] "
            return {
                "text": response,
                "edit_message_id": message["id"]
            }

        user_id = target_user["id"]
        first_name = target_user.get("first_name", "")
        last_name = target_user.get("last_name", "")
        link = f"https://vk.com/id{user_id}"

        formatted_link = f"👤 {first_name} {last_name}\n🔗 {link}\n ID: {user_id}"

        log_info(f"Использовано getlink для {message['from_id']}")
        return {
            "text": formatted_link,
            "edit_message_id": message_id
        }

    except Exception as e:
        log_error("Ошибка в getlink_handler", error=e)
        return {
            "text": "❌ Ошибка при получении информации",
            "edit_message_id": message.get("id")
        }


def time_handler(message):
    try:
        is_from_me = message.get("is_from_me", False)
        if not is_from_me or int(message["from_id"]) != 616387458:
            return
        
        moscow_tz = pytz.timezone("Europe/Moscow")
        current_time = datetime.now(moscow_tz)
        time_str = current_time.strftime("%d.%m.%Y %H:%M:%S")
        
        response = f"🕐 Текущее время: {time_str}"
        log_info(f"Выполнена команда time для {message["from_id"]}")
        
        is_from_me = message.get("is_from_me", False)
    
        return {
            "text": response,
            "edit_message_id": message["id"]
        }
    except Exception as e:
        log_info(f"Ошибка в time_handler: {e}")
        return {
            "text": "❌ Ошибка при получении времени",
            "edit_message_id": message["id"]
        }


def help_handler(message):
    try:
        help_text = """
Доступные команды:

Общие команды:
;time - текущее время
;getlink [упоминание/ответ] - получение оригинальной ссылки
;sysinfo - состояние бота
;invite - приглашение пользователя в чат
;uninvite - исключение пользователя из чата
;black - добавление пользователя в черный список
;unblack - удаление пользователя из черного списка

Модуль Quests:
;update - обновление списка ссылок
;links - просмотр сохраненных ссылок
;get [link] - отправка /getquests для указанной ссылки
;getquest - отправка /getquests для всех ссылок
;stopget - остановка отправки квестов
;quests - просмотр квестов с последней фиксации

Автоматические операции:
• Ежедневная отправка квестов для всех ссылок в 23:50 МСК
• Авто-квесты направляются в чат 2000000406
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
                    user_link = f"[https://vk.com/id{user_id}|{user["first_name"]} {user["last_name"]}]"
                    allowed_users_info.append(user_link)
            except Exception as e:
                log_error(f"Ошибка получения информации о пользователе {user_id}: {e}")
                allowed_users_info.append(f"[https://vk.com/id{user_id}|Неизвестный]")
        
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
            return False

        if peer_id < 2000000000:
            return {"text": "📛 | Команду можно использовать только в чате", "edit_message_id": message_id}

        if not args:
            return {"text": "📛 | Укажи пользователя: ;invite [упоминание / ответ на сообщение]", "edit_message_id": message_id}

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
            return {"text": "📛 | Не удалось определить пользователя.", "edit_message_id": message_id}

        if user_id == from_id:
            return {"text": "📛 | Нельзя пригласить самого себя.", "edit_message_id": message_id}

        chat_id = peer_id - 2000000000
        try:
            vk_api.vk.messages.addChatUser(chat_id=chat_id, user_id=user_id, visible_messages_count=0)
            text_resp = f"✅ | [https://vk.com/id{user_id}|Пользователь] приглашён в беседу."
        except Exception as e:
            text_resp = (
                                "⚠️ | Ошибка приглашения пользователя\n\n"
                                f"🪦 | Ошибка: {e}"
                                    )

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
            return False

        if peer_id < 2000000000:
            return {"text": "📛 | Команду можно использовать только в беседе.", "edit_message_id": message_id}

        if not args:
            return {"text": "📛 | Укажи пользователя: ;uninvite [упоминание / ответ на сообщение]", "edit_message_id": message_id}

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
            return {"text": "📛 | Не удалось определить пользователя", "edit_message_id": message_id}

        if user_id == from_id:
            return {"text": "📛 | Нельзя исключить самого себя", "edit_message_id": message_id}

        chat_id = peer_id - 2000000000
        try:
            vk_api.vk.messages.removeChatUser(chat_id=chat_id, user_id=user_id)
            text_resp = f"✅ | [https://vk.com/id{user_id}|Пользователь] исключён из чата"
        except Exception as e:
                text_resp = (
                                    "⚠️ | Ошибка исключения пользователя\n\n"
                                    f"🪦 | Ошибка: {e}"
                                     )

        log_info(f"Команда uninvite выполнена пользователем {from_id} → {user_id}")
        return {"text": text_resp, "edit_message_id": message_id}

    except Exception as e:
        log_error("Ошибка в uninvite_handler", error=e)
        return {"text": f"⚠️ | Ошибка исключения пользователя\n\n🪦 | Ошибка: {e}", "edit_message_id": message.get("id")}


def black_handler(message):
    try:
        vk_api = message.get("vk_api")
        args = message.get("text", "").split()[1:]
        message_id = message.get("id")
        from_id = int(message.get("from_id"))
        is_from_me = message.get("is_from_me", False)

        if not (is_from_me or from_id == 616387458):
            return
        
        if not args:
            return {"text": "📛 | Укажи пользователя: ;black [упоминание / ответ на сообщение]", "edit_message_id": message_id}

        user_id = resolve_user_id(args[0])
        if not user_id:
            return {"text": "📛 | Не удалось определить пользователя", "edit_message_id": message_id}
        if user_id == from_id:
            return {"text": "📛 | Нельзя заносить себя в ЧС", "edit_message_id": message_id}

        # Пытаемся выполнить бан
        try:
            vk_api.vk.account.banUser(user_id=user_id)
            text_resp = f"✅ | [https://vk.com/id{user_id}|Пользователь] занесён в ЧС"
            log_info(f"Команда black выполнена пользователем {from_id} → {user_id}")
            
            result = {"text": text_resp, "edit_message_id": message_id}
            return result
            
        except Exception as e:
            text_resp = (
                f"⚠️ | Ошибка при добавлении [https://vk.com/id{user_id}|пользователя] в ЧС\n\n"
                f"🪦 | Ошибка: {e}"
            )
            log_error("Ошибка account.banUser", error=e)
            return {"text": text_resp, "edit_message_id": message_id}

    except Exception as e:
        log_error("Ошибка в black_handler", error=e)
        return {"text": f"⚠️ | Ошибка при добавлении пользователя в ЧС\n\n🪦 | Ошибка: {e}", "edit_message_id": message.get("id")}


def unblack_handler(message):
    try:
        vk_api = message.get("vk_api")
        args = message.get("text", "").split()[1:]
        message_id = message.get("id")
        from_id = int(message.get("from_id"))
        is_from_me = message.get("is_from_me", False)

        if not (is_from_me or from_id == 616387458):
            return
        
        if not args:
            return {"text": "📛 | Укажи пользователя: ;unblack [упоминание / ответ на сообщение]", "edit_message_id": message_id}

        user_id = resolve_user_id(args[0])
        if not user_id:
            return {"text": "📛 | Не удалось определить пользователя.", "edit_message_id": message_id}

        try:
            vk_api.vk.account.unbanUser(user_id=user_id)
            text_resp = f"✅ | [https://vk.com/id{user_id}|Пользователь] удалён из ЧС"
            log_info(f"Команда unblack выполнена пользователем {from_id} → {user_id}")
            
            result = {"text": text_resp, "edit_message_id": message_id}
            return result
            
        except Exception as e:
            text_resp = (
                f"⚠️ | Ошибка при удалении [https://vk.com/id{user_id}|пользователя] из ЧС\n\n"
                f"🪦 | Ошибка: {e}"
            )
            log_error("Ошибка account.unban", error=e)
            return {"text": text_resp, "edit_message_id": message_id}

    except Exception as e:
        log_error("Ошибка в unblack_handler", error=e)
        return {"text": f"⚠️ | Ошибка при удалении пользователя из ЧС\n\n🪦 | Ошибка: {e}", "edit_message_id": message.get("id")}

