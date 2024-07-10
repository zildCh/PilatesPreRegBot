import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters , ConversationHandler
import requests
from admin_commands import admin_send_photo, admin_send_message, handle_confirmation
from user_repository import UserRepository
from user import User
def load_config(filename):
    with open(filename, 'r') as file:
        return json.load(file)

config = load_config('config.json')

TOKEN = config['TOKEN']
CHANNEL_ID = config['CHANNEL_ID']
ADMIN_ID = config['ADMIN_ID']
USERS_FILE = config['USERS_FILE']

repo = UserRepository()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    user = User(user_id, username)
    repo.add_user(user)
    #repo.delete_user(493470036)
    keyboard = [[InlineKeyboardButton("Записаться в лист ожидания ✅", callback_data='button_waiting_list')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Привет! Запишитесь в лист ожидания и получите скидку 10%',
                                    reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'button_waiting_list':
        keyboard = [[InlineKeyboardButton("Готово ✅", callback_data='button_check_subscription')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(chat_id=query.message.chat_id,
                                       text=f"Пожалуйста, подпишитесь на наш канал {CHANNEL_ID}, затем нажмите на кнопку ниже:",
                                       reply_markup=reply_markup)
    elif query.data == 'button_check_subscription':
        await check_subscription(update, context)


async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = CHANNEL_ID
    url = f'https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={chat_id}&user_id={user_id}'

    response = requests.get(url)
    data = response.json()

    if data['ok']:
        status = data['result']['status']
        if status in ['member', 'administrator', 'creator']:
            # Пользователь подписан
            await query.message.reply_text("Спасибо за подписку! Вы записаны в лист ожидания. В день открытия регистрации мы отправим вам ссылку с вашей скидкой 🎁")

        else:
            await query.message.reply_text("Вы еще не подписались на канал. Пожалуйста, подпишитесь и попробуйте снова.")
    else:
        await query.message.reply_text("Произошла ошибка при проверке подписки. Пожалуйста, попробуйте позже.")


def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button, pattern='^button_'))

    application.add_handler(CommandHandler("admin_send", admin_send_message))
    application.add_handler(MessageHandler(filters.PHOTO & filters.User(int(ADMIN_ID)), admin_send_photo))

    application.add_handler(CallbackQueryHandler(handle_confirmation))



    application.run_polling()


if __name__ == '__main__':
    main()
