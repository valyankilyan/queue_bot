import answers
import config
import telebot
import pickle
from loggerconfig import getLogger
import logging
logger = getLogger(__name__)
logger.info("Starting bot ")

queue_file = 'queue.bak'

bot = telebot.TeleBot(config.token)
queue = []

try:
    queue = pickle.load(open(queue_file, 'rb')) or []    
except:
    logger.error("there isn't queue or cur bak files")


def save_data():
    pickle.dump(queue, open(queue_file, "wb"))    

def get_user_pair(message):
    return (message.chat.id, message.from_user.username)

def swap(l, i, j):
    save = l[i]
    l[i] = l[j]
    l[j] = save

@bot.message_handler(commands=['start'])
def send_welcome(message):
    logger.info(f'{message.from_user.username} sent {message.text}')
    bot.send_message(message.chat.id, answers.start)


@bot.message_handler(commands=['help'])
def send_help(message):
    logger.info(f'{message.from_user.username} sent {message.text}')
    bot.send_message(message.chat.id, answers._help)


def say_them_to_go():
    if len(queue) > 0:
        bot.send_message(queue[0][0], answers.it_s_your_turn)
        logger.info(f'{queue[0][1]} is next')
        for i in range(1, min(len(queue), 4)):
            bot.send_message(queue[i][0], answers.you_are_next)
            bot.send_message(queue[i][0], f'Твоё место в очереди {i + 1}')
            logger.info(f'{queue[i][1]} is next')


@bot.message_handler(commands=['book'])
def book_place_in_queue(message):    
    if get_user_pair(message) in queue:
        bot.send_message(message.chat.id, answers.already_in_queue)
        show_queue(message)
        logger.info(
            f'{message.from_user.username} trying to book a place twice')
        return
    queue.append(get_user_pair(message))
    save_data()
    if len(queue) == 1:
        say_them_to_go()
    else:
        bot.send_message(message.chat.id, answers.book_success)
        # bot.send_message(message.chat.id, f"Ты на {queue.index(get_user_pair(message)) + 1} месте.")
        show_queue(message)
    logger.info(f'{message.from_user.username} booked a place in queue')


@bot.message_handler(commands=['endsession'])
def end_lab_session(message):    
    if len(queue) == 0:
        bot.send_message(message.chat.id, "Ты пытаешься меня сломать?? Очередь пустая..")
        show_queue(message)
        return
    if queue[0][0] != message.chat.id:
        bot.send_message(message.chat.id, answers.it_s_not_your_turn)
        logger.info(
            f'{message.from_user.username} trying to end someones turn')
        return
    queue.remove(get_user_pair(message))
    bot.send_message(message.chat.id, answers.end_success)    
    save_data()
    say_them_to_go()


@bot.message_handler(commands=['showqueue'])
def show_queue(message):
    logger.info("someone asked for queue")
    logger.info(f"Размер очереди: {len(queue)}\n")
    out = f"Размер очереди: {len(queue)}\n"
    for i in range(len(queue)):
        if i >= 0 and i < len(queue):
            if queue[i] == get_user_pair(message):
                out += f'*>{i + 1} - @{queue[i][1]}*\n'
            else:
                out += f'{i + 1} - @{queue[i][1]}\n'
    bot.send_message(message.chat.id, out, parse_mode="Markdown")
    if get_user_pair(message) in queue:
        ind = queue.index(get_user_pair(message))
        bot.send_message(message.chat.id, answers.your_turn.format(ind + 1))        
    else:
        bot.send_message(message.chat.id, answers.you_are_not_in_queue)
        
@bot.message_handler(commands=['getout'])
def get_out(message):
    logger.info(f"{message.from_user.username} decided to get out from this crappy queue.")
    if get_user_pair(message) in queue:
        if queue.index(get_user_pair(message)) == 0:
            end_lab_session(message)
        try:
            queue.remove(get_user_pair(message))
        except Exception as err:
            logger.error(f"Why did that happen...")
            bot.send_message(message.chat.id, f'Не, ну чел, щас ты реально меня сломать попытался.. У меня эксепшен вылетел блин.. Смотри {err=}, {type(err)=}')
        bot.send_message(message.chat.id, answers.successfully_got_out)
    else:
        bot.send_message(message.chat.id, answers.you_are_not_in_queue)
    save_data()
        
@bot.message_handler(commands=['pass'])
def pass_one(message):
    logger.info(f"{message.from_user.username} trying to pass.")
    if get_user_pair(message) in queue:
        try:
            ind = queue.index(get_user_pair(message))
            if ind == len(queue) - 1:
                bot.send_message(message.chat.id, f'Сорян, но ты и так на последнем месте..')
            else:
                bot.send_message(message.chat.id, f'okэy меняю тебя местами с @{queue[ind+1]}')
                bot.send_message(queue[ind+1][0], f'@{queue[ind][1]} пропустил_а тебя вперед, радуйся')
                swap(queue, ind, ind+1)
                save_data()
        except Exception as err:
            bot.send_message(message.chat.id, f'Не, ну чел, щас ты реально меня сломать попытался.. У меня эксепшен вылетел блин.. Смотри {err=}, {type(err)=}')
            
    else:
        bot.send_message(answers.you_are_not_in_queue)

@bot.message_handler(commands=['showentirequeue'])
def show_entire_queue(message):
    logger.info(f"{message.from_user.username} asked for entire queue")
    bot.send_message(message.chat.id, str(queue))

# @bot.message_handler(commands=['increase_cur'])
# def increase_cur(message):
#     global cur
#     if len(queue) > cur + 1:
#         cur+= 1
#         save_data()
#         logger.info(f'cur increased to {cur}')
#         bot.send_message(message.chat.id, f'cur increased to {cur}')
#     else:
#         logger.info(f'cur cannot be increased cur = {cur}, len(queue) = {len(queue)}')
#         bot.send_message(message.chat.id, f'cur cannot be increased cur = {cur}, len(queue) = {len(queue)}')
#     show_queue(message)
    
@bot.message_handler(commands=['clearqueue'])
def clear_queue(message):
    logger.info(f"Data was cleared by {message.from_user.username}")
    global queue    
    queue = []    
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
