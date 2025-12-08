import sqlite3

conn = sqlite3.connect("billing_inventory.db")
cur = conn.cursor()

cur.execute("SELECT id, username, password_hash, is_active, created_at FROM users;")
rows = cur.fetchall()

print("Users in database:")
for r in rows:
    print(r)

conn.close()
