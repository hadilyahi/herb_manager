from auth_utils import hash_password
import json
import os

os.makedirs("database", exist_ok=True)

username = "Lamjed"
password = "lamjed123"

hashed_password = hash_password(password)

admin_data = [{"username": username, "password": hashed_password}]

with open("database/admin.json", "w", encoding="utf-8") as f:
    json.dump(admin_data, f, indent=4, ensure_ascii=False)

print("✅ تم إنشاء المستخدم بنجاح!")
