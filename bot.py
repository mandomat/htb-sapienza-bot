from telegram.ext import Updater, CommandHandler
from telegram.error import TelegramError, Unauthorized, BadRequest,TimedOut, ChatMigrated, NetworkError
import telegram
import logging
import sqlite3
import signal
import sys
import os

machine_emoji= u'\U0001F4BB'
person_emoji=u'\U0001F464'
user_emoji = u'\U0001F413'
root_emoji = u'\U0001F409'
rank_emoji= u'\U0001F451'
respect_emoji= u'\U0001F44D'
points_emoji=u'\U0001F3AF'
completion_emoji=u'\U0001F4C8'
student_emoji=u'\U0001F468'
world_emoji= u'\U0001F30D'
gear_emoji=u'\U00002699'
fortress_emoji=u'\U0001F3F0'
punch_emoji=u'\U0001F44A'

updater = Updater(token=os.environ['TOKEN'])

dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")


def get_users_stats(bot,update,args):
    if len(args)>1:
        output="Too many arguments. Please, specify only one username."
        bot.send_message(chat_id=update.message.chat_id, text=output)
        return
    conn = sqlite3.connect("db/htb.db")
    c = conn.cursor()
    if len(args)==0:
        result = c.execute("SELECT * FROM 'users' ORDER BY points").fetchall()
    elif len(args)==1:
        result = c.execute("SELECT * FROM 'users' WHERE name LIKE ? ORDER BY POINTS",('%'+str(args[0])+'%',)).fetchall()
    conn.close()
    if len(result) == 0:
        output="Username not found!"
        bot.send_message(chat_id=update.message.chat_id, text=output)
        return
    output="\n "
    for user in result:
        output += (person_emoji+"<b>"+str(user[1])+"</b>\n"
        +"Rank "+rank_emoji+": "+ str(user[2])+"\n"
        +"Respect "+respect_emoji+":	"+str(user[3])+"\n"
        +"Points "+points_emoji+": "+ str(user[4])+"\n"
        +"Completion "+completion_emoji+": "+ str(user[5])+"%\n\n"
        )


    bot.send_message(chat_id=update.message.chat_id, text=output,parse_mode=telegram.ParseMode.HTML)


def get_machines_stats(bot,update,args):
    if len(args)>1:
        output="Too many arguments. Please, specify only one machine name."
        bot.send_message(chat_id=update.message.chat_id, text=output)
        return
    conn = sqlite3.connect("db/htb.db")
    c = conn.cursor()
    if len(args)==0:
        result = c.execute("SELECT * FROM 'machines_view' ORDER BY roots").fetchall()
    elif len(args)==1:
        result = c.execute("SELECT * FROM 'machines_view' WHERE name LIKE ? ORDER BY roots",('%'+str(args[0])+'%',)).fetchall()
    conn.close()
    if len(result) == 0:
        output="Machine name not found!"
        bot.send_message(chat_id=update.message.chat_id, text=output)
        return
    output="\n "
    for machine in result:
        output += (machine_emoji+"<b> "+str(machine[0])+"</b>\n"
        + "Users "+user_emoji+": " +str(machine[1])+"\n"
        + "Roots "+root_emoji+": "+str(machine[2])+"\n\n")

    bot.send_message(chat_id=update.message.chat_id, text=output,parse_mode=telegram.ParseMode.HTML)

def get_uni_ranks(bot,update,args):
    if len(args)==0:
        output="Please, provide the university name."
        bot.send_message(chat_id=update.message.chat_id, text=output)
        return
    if len(args)>1:
        output="Too many arguments. Please, specify only one university name."
        bot.send_message(chat_id=update.message.chat_id, text=output)
        return
    conn = sqlite3.connect("db/htb.db")
    c = conn.cursor()
    result = c.execute("SELECT * FROM 'universities' WHERE name LIKE ?",('%'+str(args[0])+'%',)).fetchall()

    conn.close()

    if len(result) == 0:
        output="University name not found!"
        bot.send_message(chat_id=update.message.chat_id, text=output)
        return

    output="\n "
    for uni in result:
        output += (u"<b> "+(uni[1])+"</b>\n"
        +"Rank "+rank_emoji+": "+ str(uni[0])+"\n"
        +"Students "+student_emoji+": "+str(uni[2])+"\n"
        +"Respect "+respect_emoji+": "+str(uni[3])+"\n"
        +"Country "+world_emoji+": "+ str(uni[4])+"\n"
        +"Points "+points_emoji+": "+ str(uni[5])+"\n"
        +"Ownership "+completion_emoji+": "+ str(uni[6])+"%\n"
        +"Challenges "+gear_emoji+": "+ str(uni[7])+"\n"
        +"Users "+user_emoji+": "+ str(uni[8])+"\n"
        +"Systems "+root_emoji+": "+ str(uni[9])+"\n"
        +"Fortress "+fortress_emoji+": "+ str(uni[10])+"\n"
        +"Endgames "+punch_emoji+": "+ str(uni[11])+"\n\n"
        )

    bot.send_message(chat_id=update.message.chat_id, text=output,parse_mode=telegram.ParseMode.HTML)


def error_callback(bot, update, error):
    try:
        raise error
    except BadRequest:
        bot.send_message(chat_id=update.message.chat_id, text=(
        "Your query raised an exception, maybe the response message is too long. Try to restrict your research."))

    except TimedOut:
        bot.send_message(chat_id=update.message.chat_id, text=(
        "Slow connection problems. Please, try later."))
        pass
    except NetworkError:
        bot.send_message(chat_id=update.message.chat_id, text=(
        "NetworkError. Please, try later."))
        pass
    except TelegramError:
        bot.send_message(chat_id=update.message.chat_id, text=(
        "Unknown error. Please, try later."))
        pass

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

get_users_stats_handler = CommandHandler('users', get_users_stats,pass_args=True)
dispatcher.add_handler(get_users_stats_handler)

get_machines_stats_handler = CommandHandler('machines', get_machines_stats,pass_args=True)
dispatcher.add_handler(get_machines_stats_handler)

get_uni_ranks_handler = CommandHandler('uni', get_uni_ranks,pass_args=True)
dispatcher.add_handler(get_uni_ranks_handler)

dispatcher.add_error_handler(error_callback)


updater.start_polling()
