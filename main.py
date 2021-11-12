import answers
import config
import telebot
import pickle
from loggerconfig import getLogger
import logging
logger = getLogger(__name__)
logger.info("Starting bot ")

queue_file = 'queue.bak'
cur_file = 'cur.bak'

bot = telebot.TeleBot(config.token)
queue = []
cur = -1

try:
    queue = pickle.load(open(queue_file, 'rb')) or []
    cur = pickle.load(open(cur_file, 'rb')) or -1
except:
    logger.error("there isn't queue or cur bak files")


def save_data():
    pickle.dump(queue, open(queue_file, "wb"))
    pickle.dump(cur, open(cur_file, 'wb'))


@bot.message_handler(commands=['start'])
def send_welcome(message):
    logger.info(f'{message.from_user.username} sent {message.text}')
    bot.send_message(message.chat.id, answers.start)


@bot.message_handler(commands=['help'])
def send_help(message):
    logger.info(f'{message.from_user.username} sent {message.text}')
    bot.send_message(message.chat.id, answers._help)


def say_them_to_go():
    if cur < len(queue):
        bot.send_message(queue[cur][0], answers.it_s_your_turn)
        logger.info(f'{queue[cur][1]} is now passing the lab')
        if cur + 1 < len(queue):
            bot.send_message(queue[cur+1][0], answers.you_are_next)
            logger.info(f'{queue[cur+1][1]} is next')


@bot.message_handler(commands=['book'])
def book_place_in_queue(message):
    global cur
    if (message.chat.id, message.from_user.username) in queue[cur:]:
        bot.send_message(message.chat.id, answers.already_in_queue)
        show_queue(message)
        logger.info(
            f'{message.from_user.username} trying to book a place twice')
        return
    queue.append((message.chat.id, message.from_user.username))
    save_data()
    if cur == -1: 
        cur+= 1
        save_data()
    if cur == len(queue) - 1:
        say_them_to_go()
    else:
        bot.send_message(message.chat.id, answers.book_success)
        show_queue(message)
    logger.info(f'{message.from_user.username} booked a place in queue')


@bot.message_handler(commands=['endsession'])
def end_lab_session(message):
    global cur
    if len(queue) == 0 or cur == -1:
        bot.send_message(message.chat.id, "Ты пытаешься меня сломать?? Очередь пустая..")
        show_queue(message)
        return
    if queue[cur][0] != message.chat.id:
        bot.send_message(message.chat.id, answers.it_s_not_your_turn)
        logger.info(
            f'{message.from_user.username} trying to end someones turn')
        return
    bot.send_message(message.chat.id, answers.end_success)
    cur+= 1
    save_data()
    say_them_to_go()


@bot.message_handler(commands=['showqueue'])
def show_queue(message):
    logger.info("someone asked for queue")
    logger.info(f"Размер очереди: {len(queue) - (0 if cur == -1 else cur)}\n")
    out = f"Размер очереди: {len(queue) - (0 if cur == -1 else cur)}\n"
    for i in range(cur, cur + 3):
        if i >= 0 and i < len(queue):
            out += f'{i - cur + 1} - {queue[i][1]}\n'
    bot.send_message(message.chat.id, out)
    if (message.chat.id, message.from_user.username) in queue[cur:]:
        ind = queue.index((message.chat.id, message.from_user.username))
        bot.send_message(message.chat.id, answers.your_turn.format(ind - cur + 1))        
    else:
        bot.send_message(message.chat.id, answers.you_are_not_in_queue)

@bot.message_handler(commands=['showentirequeue'])
def show_entire_queue(message):
    logger.info(f"{message.from_user.username} asked for entire queue")
    bot.send_message(message.chat.id, str(queue))

@bot.message_handler(commands=['increase_cur'])
def increase_cur(message):
    global cur
    if len(queue) > cur + 1:
        cur+= 1
        save_data()
        logger.info(f'cur increased to {cur}')
        bot.send_message(message.chat.id, f'cur increased to {cur}')
    else:
        logger.info(f'cur cannot be increased cur = {cur}, len(queue) = {len(queue)}')
        bot.send_message(message.chat.id, f'cur cannot be increased cur = {cur}, len(queue) = {len(queue)}')
    show_queue(message)
    
@bot.message_handler(commands=['clearqueue'])
def clear_queue(message):
    logger.info(f"Data was cleared by {message.from_user.username}")
    global queue
    global cur
    queue = []
    cur = -1
    save_data()
    bot.send_message(message.chat.id, "Очередь очищена")

@bot.message_handler(func=lambda m: True)
def casual_message(message):
    logger.info(f'{message.from_user.username} sent {message.text}')
    error(message)

def error(message):
    bot.reply_to(message, answers.error)


if __name__ == "__main__":    
    bot.polling(none_stop=True)
