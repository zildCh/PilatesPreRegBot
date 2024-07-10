import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from user_repository import UserRepository
from telegram.constants import ParseMode


with open('config.json', 'r') as file:
    config = json.load(file)
from datetime import datetime
ADMIN_ID = config['ADMIN_ID']

UserRepo = UserRepository()

async def admin_send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id != ADMIN_ID:
        await update.message.reply_text("Вы не являетесь администратором.")
        return

    if not update.message.photo:
        await update.message.reply_text("Пожалуйста, отправьте фотографию.")
        return

    photo_id = update.message.photo[-1].file_id
    context.user_data['photo_id'] = photo_id  # Сохраняем photo_id в user_data
    await update.message.reply_text("Теперь отправьте команду /admin_send с текстом сообщения")


async def admin_send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.message.from_user.id)
        if user_id != ADMIN_ID:
            await update.message.reply_text("Вы не являетесь администратором.")
            return

        if len(context.args) == 0:
            await update.message.reply_text("Пожалуйста, укажите сообщение для рассылки.")
            return

        message = update.message.text[len('/admin_send '):]

        context.user_data['message'] = message
        if 'photo_id' in context.user_data:
            photo_id = context.user_data['photo_id']
            # Определение временных интервалов для выбора пользователей
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Всем", callback_data='send_1')],
                [InlineKeyboardButton("❌ Отменить", callback_data='delete')]
            ])
            await update.message.reply_photo(photo=photo_id, caption=message, parse_mode=ParseMode.HTML)
            await update.message.reply_text("Выберите период, для которого будет осуществлена рассылка:",
                                            reply_markup=reply_markup)
        else:
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Всем", callback_data='send_1')],
                [InlineKeyboardButton("❌ Отменить", callback_data='delete')]
            ])
            await update.message.reply_text(text=message, parse_mode=ParseMode.HTML, reply_markup=reply_markup)


async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith('send_'):
        days_ago = int(query.data.split('_')[1])
        message = context.user_data['message']
        users = []
        users = UserRepo.get_all_users2()

        if 'photo_id' in context.user_data:
            photo_id = context.user_data['photo_id']
            for user in users:
                user_id = user
                try:
                    await context.bot.send_photo(chat_id=user_id, photo=photo_id, parse_mode=ParseMode.HTML, caption=message)
                except Exception as e:
                    print(f"Не удалось отправить фото пользователю {user_id}: {e}")
        else:
            for user in users:
                user_id = user
                try:
                    await context.bot.send_message(chat_id=user_id,parse_mode=ParseMode.HTML, text=message)
                except Exception as e:
                    print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

        await context.bot.send_message(chat_id=query.message.chat_id, text="Сообщение успешно отправлено.")

    elif query.data == 'delete':
        await context.bot.send_message(chat_id=query.message.chat_id, text="Отправка отменена, фото удалено.")
        context.user_data.clear()