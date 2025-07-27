"""Telegram bot functionality for remote monitoring."""

import os
import asyncio
import urllib.request
import cv2
from PyQt6.QtCore import QThread, pyqtSignal
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from ..database.handler import DBHelper


class ConnectionError(Exception):
    """Custom exception raised to halt the TG bot process."""
    pass


class TelegramBot(QThread):
    """Telegram bot for remote monitoring and control."""
    
    send_persons_signal = pyqtSignal()
    send_start_camera = pyqtSignal()
    send_stop_camera = pyqtSignal()
    bot_status = pyqtSignal(str)
    
    def __init__(self, database_obj: DBHelper, camera_status_callback):
        super().__init__()
        self.db = database_obj
        self.camera_status_callback = camera_status_callback
        self.loop = None
        self.noconn = False
        self.bot = None
        self.admin_id = None
    
    def check_bot_status(self):
        """Check bot connection status and initialize if possible."""
        try:
            response = urllib.request.urlopen('https://api.telegram.org', timeout=5)
            if response.status == 200:
                print("Internet connection is OK.")
                self.bot_status.emit("on")
            else:
                print("Internet connection is not OK.")
                raise ConnectionError("Connection failed.")
            
            bot_token = self.db.get_bot_token()
            if bot_token is not None:
                self.bot = AsyncTeleBot(bot_token)
            else:
                raise ConnectionError("Bot token is empty.")

            admins = self.db.get_admins()
            if admins is not None:
                self.admin_id = admins
            else:
                raise ConnectionError("Bot admin is empty.")
  
        except Exception as e:
            print(f"Bot is off ::::Error {e}")
            self.noconn = True
            self.bot_status.emit("off")

    def setup_handlers(self):
        """Setup bot message and callback handlers."""
        @self.bot.message_handler(commands=['help', 'start'])
        async def send_welcome(message):
            text = 'Hello!'
            await self.bot.reply_to(message, text)

        @self.bot.message_handler(func=lambda message: int(message.chat.id) not in self.admin_id)
        async def echo_message(message):
            user_name = message.from_user.first_name
            user_id = message.from_user.id
            if self.db.user_exists(user_id):
                print(f"User {user_name} already exists in the database.")
            else:
                self.db.add_user(user_name, user_id)
                print(f"User {user_name} added to the database.")
                await self.bot.reply_to(message, message.text)

        @self.bot.message_handler(func=lambda message: message.text == 'sendtext' and int(message.chat.id) in self.admin_id)
        async def send_text(message):
            print("Sending message to all users...")
            await self.send_message_to_all_users()

        @self.bot.message_handler(func=lambda message: int(message.from_user.id) in self.admin_id)
        async def handle_admin_command(message):
            if message.text == '/panel':
                await handle_admin(message)

        async def handle_admin(message):
            keyboard = InlineKeyboardMarkup()
            keyboard.row_width = 2
            keyboard.add(
                InlineKeyboardButton("Get photo", callback_data="photo"),
                InlineKeyboardButton("shutdown", callback_data="shutdown"),
                InlineKeyboardButton("start camera", callback_data="start_camera"),
                InlineKeyboardButton("stop camera", callback_data="stop_camera")
            )
            await self.bot.reply_to(message, 'You are my admin. Choose an action:', reply_markup=keyboard)
        
        @self.bot.callback_query_handler(func=lambda call: True)
        async def callback_query(call):
            camera_running = self.camera_status_callback()
            
            if call.data == "photo":
                if camera_running:
                    self.send_persons_signal.emit()
                else:
                    await self.bot.send_message(call.message.chat.id, "Please start the camera first.")
            elif call.data == "shutdown":
                await self.bot.send_message(call.message.chat.id, "Shutting down the application...")
                os._exit(0)
            elif call.data == "start_camera":
                if not camera_running:
                    self.send_start_camera.emit()
                else:
                    await self.bot.send_message(call.message.chat.id, "Camera is already running.")
            elif call.data == "stop_camera":
                if camera_running:
                    self.send_stop_camera.emit()
                else:
                    await self.bot.send_message(call.message.chat.id, "Camera is not running.")

    def run(self):
        """Run the bot in the thread."""
        self.check_bot_status()
        if self.noconn:
            return
        
        self.setup_handlers()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self.bot.polling(none_stop=True))
        except Exception as e:
            print(f"Maybe bot token needs to reset API webhook or token invalid: {e}")
            self.bot_status.emit("off")
    
    def send_photo_to_admin(self, data, text):
        """Send photo to admin users."""
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.send_photoo(data, text), self.loop)
    
    async def send_photoo(self, data, text):
        """Internal method to send photo via bot."""
        print("Sending photo to admin...")
        
        _, buffer = cv2.imencode('.jpg', data[0])
        photo = buffer.tobytes()
        
        if text == "Noperson":
            for admin in self.admin_id:
                await self.bot.send_photo(admin, photo, caption="No person detected!")
            return
            
        for admin in self.admin_id:
            await self.bot.send_photo(admin, photo, caption="Person detected!")
        
        if text == "pandf" and len(data) > 1:
            _, buffer = cv2.imencode('.jpg', data[1])
            face = buffer.tobytes()
            for admin in self.admin_id:
                await self.bot.send_photo(admin, face, caption="Face detected!")
        
        await self.bot.send_message(self.admin_id[0], "Photo sent to admin.")

    async def send_message_to_all_users(self):
        """Send message to all registered users."""
        users = self.db.get_all_users()
        print(f"Users: {users}")
        for user in users:
            user_id = user[0]
            chat = await self.bot.get_chat(user_id)
            await self.bot.send_message(user_id, f"Hello {chat.first_name} @{chat.username}!")
        
        for admin in self.admin_id:
            await self.bot.send_message(admin, "Message sent to all users.")