import json
import os
import threading
import time

from bot.utils.logger import log_error, log_info

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
                    
                    time.sleep(3)
                    
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


def quests_handler(message):
    try:
        vk_api = message.get("vk_api")
        message_id = message.get("id")
        from_id = int(message.get("from_id"))
        is_from_me = message.get("is_from_me", False)
        peer_id = message.get("peer_id")
        file_path = "quests.json"

        if not os.path.exists(file_path):
            text_resp = "❌ Файл quests.json не найден."
            if is_from_me or from_id == 616387458:
                return {"text": text_resp, "edit_message_id": message_id}
            return {"text": text_resp}

        with open(file_path, "r", encoding="utf-8") as f:
            quests_data = json.load(f)

        if not quests_data:
            text_resp = "⚠️ Квестов пока нет."
            if is_from_me or from_id == 616387458:
                return {"text": text_resp, "edit_message_id": message_id}
            return {"text": text_resp}

        total_quests = sum(len(v) for v in quests_data.values())
        max_length = 3800
        parts = []
        current_part = f"📋 Всего квестов: {total_quests}\n\n"
        current_len = len(current_part)

        for user_id, quests in quests_data.items():
            user_lines = []
            count = len(quests)
            try:
                user_info = vk_api.get_user_info(user_id)
                if user_info and len(user_info) > 0:
                    user = user_info[0]
                    first_name = user.get("first_name", "")
                    last_name = user.get("last_name", "")
                    name_link = f"[id{user_id}|{first_name} {last_name}]"
                    user_lines.append(f"{name_link} — {count} квест(ов):")
                else:
                    user_lines.append(f"[id{user_id}|Пользователь] — {count} квест(ов):")
            except Exception as e:
                log_error(f"Ошибка получения информации о пользователе {user_id}", error=e)
                user_lines.append(f"👤 [id{user_id}|Неизвестный пользователь] — {count} квест(ов):")

            for q in quests:
                qid = q.get("id", "—")
                status = q.get("status", "—")
                comment = q.get("comment", "")
                user_lines.append(f"    {qid} | Статус: {status} - {comment}")

            user_block = "\n".join(user_lines)

            if current_len + len(user_block) > max_length:
                parts.append(current_part.strip())
                current_part = user_block
                current_len = len(current_part)
            else:
                current_part += "\n" + user_block
                current_len += len(user_block)

        if current_part.strip():
            parts.append(current_part.strip())

        log_info(f"Команда quests выполнена пользователем {from_id} (частей: {len(parts)})")

        first_part = parts[0] if parts else "⚠️ Нет данных для отображения"

        if len(parts) > 1:
            for idx, part in enumerate(parts[1:], start=2):
                try:
                    time.sleep(1)
                    ok = vk_api.send_message(peer_id=peer_id, message=part)
                    if not ok:
                        log_error(f"Не удалось отправить часть #{idx}")
                except Exception as e:
                    log_error(f"Ошибка при отправке части #{idx}", error=e)

        if is_from_me or from_id == 616387458:
            return {"text": first_part, "edit_message_id": message_id}
        return {"text": first_part}

    except Exception as e:
        log_error("Ошибка в quests_handler", error=e)
        if message.get("is_from_me", False) or int(message.get("from_id")) == 616387458:
            return {"text": "❌ Ошибка при обработке квестов", "edit_message_id": message.get("id")}
        return {"text": "❌ Ошибка при обработке квестов"}

