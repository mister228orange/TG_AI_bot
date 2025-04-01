from ollama import AsyncClient
import sqlite3


class AIManager:

    def __init__(self, model_name, model_developer="unknow"):
        self.model_name = model_name
        self.model_developers = model_developer
        self.chats = {}
        self.conn = sqlite3.connect('msgs.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS messages(
            msg_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            msg_txt TEXT,
            role TEXT
        )""")

        # Load existing messages, but don't assume msg_id is used
        self.cursor.execute("""SELECT user_id, msg_txt, role FROM messages""")
        msgs = self.cursor.fetchall()
        for user_id, msg_txt, role in msgs:
            message = {'role': role, 'content': msg_txt}
            if user_id in self.chats:
                self.chats[user_id].append(message)
            else:
                self.chats[user_id] = [message]
        self.print_stat()


    async def get_AI_response(self, sender, msg):
        print(f"User {sender} send '{msg[:50]}' and wait answer")
        message = {'role': 'user', 'content': msg}

        """Add message to history or create new user history"""
        if sender in self.chats:
            self.chats[sender].append(message)
        else:
            self.chats[sender] = [message]

        resp_txt = []
        try:
            async for part in await AsyncClient().chat(model=self.model_name, messages=self.chats[sender], stream=True):
                resp_txt.append(part['message']['content'])
            resp_txt = ''.join(resp_txt)
            resp_message = {'role': 'assistant', 'content': resp_txt}
            self.chats[sender].append(resp_message)
            self.save_msgs()
            self.print_stat()
            print(f"AI completed answered '{resp_txt[:50]}'... to {sender}")

        except Exception as e:
            resp_txt = f"AI failed with error {e}"
            print(resp_txt)
        finally:
            return resp_txt


    def save_msgs(self):
        for sender, messages in self.chats.items():
            for msg in messages:
                self.cursor.execute("SELECT COUNT(*) FROM messages WHERE user_id = ? AND msg_txt = ? AND role = ?",
                                    (sender, msg['content'], msg['role']))
                count = self.cursor.fetchone()[0]
                if count == 0:
                    self.cursor.execute("INSERT INTO messages (user_id, msg_txt, role) VALUES (?, ?, ?)",
                                        (sender, msg['content'], msg['role']))

        self.conn.commit()


    def print_stat(self):
        print(f"Chats: {len(self.chats.keys())}")
        total_msgs = 0
        for chat, msgs in self.chats.items():
            total_msgs += len(msgs)
            print(chat, len(msgs))
        print(f"Total messages: {total_msgs}")
