import  config
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
import mysql.connector
from helper_funcs import pintopinterst, get_download_url
from time import sleep
bot = TeleBot(config.BOT_TOKEN)


def check_join(user, channels):
    for channel in channels:
        is_member = bot.get_chat_member(chat_id=channel, user_id=user)
        if is_member.status in ['kicked', 'left']:
            return False

    return True


def check_admin(userid):
    admins = []
    with mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD,
                                 host=config.DATABASE_HOST, database=config.DATABASE_NAME) as connection:
        with connection.cursor() as cursor:
            sql = f"SELECT * FROM admin"
            cursor.execute(sql)
            for i in cursor:
                admins.append(i[0])

    return str(userid) in admins

keybord_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
keybord_markup.add("📈 آمار و گزارش کاربران", "🆔 اضافه کردن ادمین", "📍فوروارد همگانی", "💠 بخش تبلیغات","🔐افزودن کانال قفل", "give photo")

button1 = InlineKeyboardButton("اضافه کردن تبلیغات", callback_data="addads")
button2 = InlineKeyboardButton("حدف کردن تبلیغات", callback_data="delads")
markup = InlineKeyboardMarkup()
markup.add(button1, button2)
button3 = InlineKeyboardButton("عضو شدم", callback_data="commit")
markup1 = InlineKeyboardMarkup(row_width=1)
markup1.add(button3)

@bot.callback_query_handler(func=lambda call:True)
def callback_query(call):
    if call.data == "addads":
        msg = bot.send_message(call.message.chat.id, "تبلیغ خود را ارسال نمایید")
        bot.register_next_step_handler(msg, addadsfunc)
    elif call.data == "delads":
        with mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD,
                                     host=config.DATABASE_HOST, database=config.DATABASE_NAME) as connection:
            with connection.cursor() as cursor:
                sql = f"SELECT * FROM ads "
                cursor.execute(sql)
                for i in cursor:
                    bot.send_message(call.message.chat.id, f"{i[0]}.\n{i[1]}")
        msg = bot.send_message(call.message.chat.id, "ای دی تبلیغات مورد نظر برای حدف را از لیست زیر انتخاب کرده و آن را برای حدف ارسال نمایید")
        bot.register_next_step_handler(msg, deladdfunc)
    elif call.data == "commit":
        channels = []
        with mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD,
                                     host=config.DATABASE_HOST, database=config.DATABASE_NAME) as connection:
            with connection.cursor() as cursor:
                sql = f"SELECT * FROM channel"
                cursor.execute(sql)
                for i in cursor:
                    channels.append(i[0])

        if check_join(call.message.chat.id, channels):
            bot.send_message(call.message.chat.id, "🔗 برای دانلود عکس یا فیلم از پینترست لطفا لینک خود را ارسال کنید")
        else:
            x = ""
            for i in channels:
                x += i
                x += "\n"
            else:
                bot.send_message(call.message.chat.id, f"🔒 برای استفاده از ربات باید در کانال های زیر عضو شوید:\n{x}",
                                 reply_markup=markup1)







@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        with mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD, host=config.DATABASE_HOST, database=config.DATABASE_NAME) as connection:
            with connection.cursor() as cursor:
                sql = f"INSERT INTO users (id) VALUES ('{message.from_user.id}')"
                cursor.execute(sql)
                connection.commit()
    except:
        pass

    if check_admin(message.from_user.id):
        bot.send_message(message.from_user.id, "🗝 سلام ادمین عزیز امیدوارم روز خوبی داشته باشی چه کاری از من برات بر میاد", reply_markup=keybord_markup)
    else:
        channels = []
        with mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD,
                                     host=config.DATABASE_HOST, database=config.DATABASE_NAME) as connection:
            with connection.cursor() as cursor:
                sql = f"SELECT * FROM channel"
                cursor.execute(sql)
                for i in cursor:
                    channels.append(i[0])

        if check_join(message.from_user.id, channels):
            bot.send_message(message.from_user.id, "🔗 برای دانلود عکس یا فیلم از پینترست لطفا لینک خود را ارسال کنید")
        else:
            x = ""
            for i in channels:
                x += i
                x += "\n"
            else:
                bot.send_message(message.from_user.id, f"🔒 برای استفاده از ربات باید در کانال های زیر عضو شوید:\n{x}", reply_markup=markup1)

@bot.message_handler()
def handle_message(message):
    if message.text == "📈 آمار و گزارش کاربران":
        x = ""
        with mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD, host=config.DATABASE_HOST, database=config.DATABASE_NAME) as connection:
            with connection.cursor() as cursor:
                sql = f"SELECT COUNT(*) FROM users"
                cursor.execute(sql)
                for i in cursor:
                    x = i[0]
        bot.send_message(message.from_user.id, f"تعداد کاربران ربات در این لحظه {x} نفر می باشد")
    elif message.text == "🆔 اضافه کردن ادمین":
        msg = bot.send_message(message.from_user.id, "آیدی فرد مورد نظر را وارد کنید")
        bot.register_next_step_handler(msg, admin_adder)

    elif message.text == "📍فوروارد همگانی":
        msg = bot.send_message(message.from_user.id, "متن پیام مورد نظر برای اطلاع رسانی به تمام اعضای فعال ربات را وارد نمایید")
        bot.register_next_step_handler(msg, forwardmeassg)
    elif message.text == "🔐افزودن کانال قفل":
        msg = bot.send_message(message.from_user.id, "لطفا بعد از اطمینان حاصل کردن از ادمین بودن ربات در کانال مورد نظر یوزر نیم کانال را بدون @ ارسال نمایید")
        bot.register_next_step_handler(msg, kanalgof)

    elif message.text == "💠 بخش تبلیغات":
        bot.send_message(message.from_user.id, "یکی از گزینه های زیر را انتخاب نمایید", reply_markup=markup)
    else:
        channels = []
        with mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD,
                                     host=config.DATABASE_HOST, database=config.DATABASE_NAME) as connection:
            with connection.cursor() as cursor:
                sql = f"SELECT * FROM channel"
                cursor.execute(sql)
                for i in cursor:
                    channels.append(i[0])

        if check_join(message.from_user.id, channels):
            if message.text.startswith('https://pin.it/'):
                cvb = pintopinterst(message.text)
                if cvb:
                    nbv = get_download_url(cvb)
                    if '.mp4' in str(nbv):
                        bot.send_chat_action(message.from_user.id, action="upload_video")
                    else:
                        bot.send_chat_action(message.from_user.id, action="upload_photo")
                    bot.send_message(message.from_user.id, nbv)
                    with mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD, host=config.DATABASE_HOST, database=config.DATABASE_NAME) as connection:
                        with connection.cursor() as cursor:
                            sql = f"SELECT * FROM ads"
                            cursor.execute(sql)
                            for i in cursor:
                                if i[2] == "1":
                                    with open(i[3], 'rb') as sendfilename:
                                        bot.send_photo(message.from_user.id, sendfilename, caption=i[1])

                                elif i[2] == "2":
                                    with open(i[3], 'rb') as sendfilename:
                                        bot.send_video(message.from_user.id, sendfilename, caption=i[1])

                                else:
                                    bot.send_message(message.from_user.id, i[1])
                else:
                    bot.send_message(message.from_user.id, " ❗️ لینک شما نامعتبر است لطفا دوباره با دقت بیشتر تلاش کنید")

            elif message.text.startswith('https://www.pinterest.com/'):
                njd = get_download_url(message.text)
                if njd:
                    if '.mp4' in str(njd):
                        bot.send_chat_action(message.from_user.id, action="upload_video")
                    else:
                        bot.send_chat_action(message.from_user.id, action="upload_photo")

                    bot.send_message(message.from_user.id, njd)
                    with mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD, host=config.DATABASE_HOST, database=config.DATABASE_NAME) as connection:
                        with connection.cursor() as cursor:
                            sql = f"SELECT * FROM ads"
                            cursor.execute(sql)
                            for i in cursor:
                                if i[2] == "1":
                                    with open(i[3], 'rb') as sendfilename:
                                        bot.send_photo(message.from_user.id, sendfilename, caption=i[1])

                                elif i[2] == "2":
                                    with open(i[3], 'rb') as sendfilename:
                                        bot.send_video(message.from_user.id, sendfilename, caption=i[1])

                                else:
                                    bot.send_message(message.from_user.id, i[1])

                                 
                else:
                    bot.send_message(message.from_user.id, "❗️ لینک شما نامعتبر است لطفا دوباره با دقت بیشتر تلاش کنید")



            else:
                bot.send_message(message.from_user.id, "❗️ لینک شما نامعتبر است لطفا دوباره با دقت بیشتر تلاش کنید")

        else:
            x = ""
            for i in channels:
                x += i
                x += "\n"
            else:
                bot.send_message(message.from_user.id, f"❗️ برای استفاده از ربات باید در کانال های زیر عضو شوید:\n{x}",
                                 reply_markup=markup1)















def admin_adder(message):
    try:
        with mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD, host=config.DATABASE_HOST, database=config.DATABASE_NAME) as connection:
            with connection.cursor() as cursor:
                sql = f"INSERT INTO admin (id) VALUES ('{message.text}')"
                cursor.execute(sql)
                connection.commit()
        bot.send_message(message.from_user.id, "✅ کاربر مورد نظر شما به لیست ادمین ها افزوده شد")
    except:
        bot.send_message(message.from_user.id, "کاربر مورد نظر شما از قبل عضوی از لیست ادمین ها می باشد لطفا دوباره اقدام نفرمایید")

def forwardmeassg(message):
    with mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD, host=config.DATABASE_HOST, database=config.DATABASE_NAME) as connection:
        with connection.cursor() as cursor:
            sql = f"SELECT * FROM users"
            cursor.execute(sql)
            for i in cursor:
                try:
                    bot.send_message(i[0], message.text)
                except:
                    continue

    bot.reply_to(message, "✅ ارسال این پیام به تمامی کاربران با موفقیت انجام شد")


def kanalgof(message):
    try:
        bot.get_chat_member(user_id=message.from_user.id, chat_id=f"@{message.text}")
        try:
            with mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD,
                                         host=config.DATABASE_HOST, database=config.DATABASE_NAME) as connection:
                with connection.cursor() as cursor:
                    sql = f"INSERT INTO channel (id) VALUES ('@{message.text}')"
                    cursor.execute(sql)
                    connection.commit()
            bot.send_message(message.from_user.id, "کانال با موفقیت به لیست کانال های قفل شده افزوده شد ✅")
        except:
            bot.send_message(message.from_user.id, "کانال از قبل جزو لیست کانال های قفل شده می باشد لطفا دوباره اقدام نکنید")
    except:
        bot.send_message(message.from_user.id, "یوزر نیم کانال را اشتباه وارد کرده اید و یا ربات در کانال ادمین نمی باشد لطفا مشکل را برسی کرده و سپس دوباره از پنل ادمین اقدام نمایید")


def addadsfunc(message):
    if message.content_type == "photo":
        photo_file_id = message.photo[-1].file_id
        file_info = bot.get_file(photo_file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(f'{file_info.file_unique_id}.jpg', 'wb') as new_file:
            new_file.write(downloaded_file)
        with mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD, host=config.DATABASE_HOST, database=config.DATABASE_NAME) as connection:
            with connection.cursor() as cursor:
                sql = f"INSERT INTO ads (matn , isphoto, addres) VALUES ('{message.caption}' , '1', '{file_info.file_unique_id}.jpg')"
                cursor.execute(sql)
                connection.commit()

    elif message.content_type == "video":
        video_file_id = message.video.file_id
        # Download the video
        file_info = bot.get_file(video_file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        # Save the video to a file
        with open(f'{file_info.file_unique_id}.mp4', 'wb') as new_file:
            new_file.write(downloaded_file)

        with mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD, host=config.DATABASE_HOST, database=config.DATABASE_NAME) as connection:
            with connection.cursor() as cursor:
                sql = f"INSERT INTO ads (matn , isphoto, addres) VALUES ('{message.caption}' , '2', '{file_info.file_unique_id}.mp4')"
                cursor.execute(sql)
                connection.commit()

    else:
        with mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD, host=config.DATABASE_HOST, database=config.DATABASE_NAME) as connection:
            with connection.cursor() as cursor:
                sql = f"INSERT INTO ads (matn , isphoto, addres) VALUES ('{message.text}' , '0', 'only text')"
                cursor.execute(sql)
                connection.commit()





    bot.send_message(message.from_user.id, "تبلیغات مورد نظر شما با موفقیت اضافه شد ✅")



def deladdfunc(message):
    try:
        adsss = []
        with mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD,
                                     host=config.DATABASE_HOST, database=config.DATABASE_NAME) as connection:
            with connection.cursor() as cursor:
                sql = f"SELECT * FROM ads "
                cursor.execute(sql)
                for i in cursor:
                    adsss.append(str(i[0]))

        if message.text not in adsss:
            raise ValueError("ridi")
        with mysql.connector.connect(user=config.DATABASE_USER, password=config.DATABASE_PASSWORD,
                                         host=config.DATABASE_HOST, database=config.DATABASE_NAME) as connection:
            with connection.cursor() as cursor:
                sql = f"DELETE FROM ads WHERE id = '{message.text}'"
                cursor.execute(sql)
                connection.commit()

        bot.send_message(message.from_user.id, "حذف تبلیغ مورد نظر با موفقیت انجام شد ✅")

    except:
        bot.send_message(message.from_user.id, "ایدی وارد شده صحیح نمی باشد لطفا مجددا اقدام فرمایید! ❌ ")

bot.infinity_polling()