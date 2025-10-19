import os
import re
import shutil

def remove_pycache():
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            shutil.rmtree(pycache_path)

def resolve_user_id(vk_api, user_input):
    user_input = user_input.strip()
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

    return user_id
