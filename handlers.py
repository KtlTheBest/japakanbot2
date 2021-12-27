from db import DBInstance
import util

from telegram.ext import ConversationHandler

def start(update, context):
    db = DBInstance()
    username = util.getUsername(update)
    name = util.getName(update)
    chatid = util.getChatID(update)
    db.addNewUser(username, name, chatid)
    util.send_message('Hello, I added your id to database!', update)

def help(update, context):
    message = """Hello, this bot supports the following commands:
    /start - registers the user
    /add - Adds kanji to the dictionary, until the /done is entered
    /fix - Fixes the kanji and stops when /done is entered
    /delete - Deletes the specified kanji
    /done - Stops /add, /fix and /delete
    /list - Shows the list of all kanji
    /quiz - Shows the current kanji that needs to be guessed
    /stats - Shows the stats of successful guesses
    /clearstats - Clears the stats accross kanji

To guess a kanji, just enter a romaji. If you forgot which kanji you need to guess, just enter /quiz
    """
    util.send_message(message, update)

def start_add_kanji(update, context):
    message = "Nice! Please send me kanji and romaji in one message, splitting them by space, one at a time, like this:\n\n作戦 sakusen"
    util.send_message(message, update)
    return 0

def start_fix_kanji(update, context):
    message = "Okay! Please send me kanji and romaji in one message, splitting them by space, one at a time, like this:\n\n作戦 sakusen"
    util.send_message(message, update)
    return 0

def start_delete_kanji(update, context):
    message = "Sure! Please send me kanji ONLY in one message, like this:\n\n作戦"
    util.send_message(message, update)
    return 0

def receive_add_kanji(update, context):
    chatid = util.getChatID(update)
    text = util.getMessage(update).rstrip().lstrip()
    kanji, romaji = filter(None, text.split(' '))
    db = DBInstance()
    db.addKanji(chatid, kanji, romaji)

    message = "I see the following:\n{} - {}".format(kanji, romaji)
    util.send_message(message, update)

    return 0

def receive_delete_kanji(update, context):
    chatid = util.getChatID(update)
    kanji = util.getMessage(update).rstrip().lstrip()
    db = DBInstance()
    db.deleteKanji(chatid, kanji)

    message = "Deleted the following kanji:\n{}".format(kanji)
    util.send_message(message, update)

    return 0

def wrong_receive_kanji(update, context):
    message = "Please send kanji in the correct format. Try again!"
    util.send_message(message, update)
    return 0

def finish_receive_kanji(update, context):
    message = "Thank you! Finished updating your dictionary. You may start seeing new words now."
    util.send_message(message, update)

    chatid = util.getChatID(update)
    util.setRandomKanji(chatid)

    return ConversationHandler.END

def remind_to_study_kanji(context):
    bot = context.bot
    db = DBInstance()

    chatid_list = db.getChats()

    for t in chatid_list:
        chatid = t[0]
        res = db.getQuizKanjiForChatID(chatid)
        if len(res) == 0:
            quiz_kanji = "You have none. Add new kanji via /add command!"
        else:
            quiz_kanji = res[0][0]

        message = "Don't stop on taking quizes!\nYour current quiz kanji is: {}".format(quiz_kanji)
        bot.sendMessage(chatid, message)

def show_cur_quiz_kanji(update, context):
    chatid = util.getChatID(update)
    db = DBInstance()
    res = db.getQuizKanjiForChatID(chatid)
    if len(res) == 0:
        message = "Your quiz is not set, try to add new kanji to the list first, by invoking /add command"
    else:
        kanji = res[0][0]
        message = "Here is the kanji that was set as the quiz:\n{}".format(kanji)
    util.send_message(message, update)

def show_kanji_list(update, context):
    chatid = util.getChatID(update)
    db = DBInstance()
    kanji_list = db.getKanjiListForChatID(chatid)
    message = '\n'.join(['{} - {}'.format(x[0], x[1]) for x in kanji_list])

    if len(message) == 0:
        message = "Your current kanji list is empty. Try adding more with /add command"
    util.send_message(message, update)

def check_guess(update, context):
    guess = util.getMessage(update).rstrip().lstrip().lower()
    chatid = util.getChatID(update)
    db = DBInstance()
    res = db.getQuizKanjiForChatID(chatid)
    if len(res) == 0:
        message = "Your quiz is not set, try to add new kanji to the list first, by invoking /add command"
        util.send_message(message, update)
        return
    
    kanji, correct = res[0][0], res[0][1]

    if correct == guess:
        db.updateCountKanji(chatid, kanji, 1)
        message = "Correct!"
    else:
        message = "Sorry, but correct answer is:\n\n{}".format(correct)

    util.send_message(message, update)
    db.clearKanjiQuizForChatID(chatid)
    util.setRandomKanji(chatid)
    res = db.getQuizKanjiForChatID(chatid)
    kanji = res[0][0]
    message = "Next~ {}".format(kanji)
    util.send_message(message, update)

def show_stats(update, context):
    chatid = util.getChatID(update)
    db = DBInstance()
    stats = db.getQuizStatsForChatID(chatid)

    if len(stats) == 0:
        message = "You don't have any kanji yet, try adding them via /add command!"
        util.send_message(message)
        return
    
    util.send_message('Kanji - Count:\n' + '\n'.join(["{} - {}".format(x[0], x[1]) for x in stats]), update)

def clear_stats(update, context):
    chatid = util.getChatID(update)
    db = DBInstance()
    db.clearQuizStatsForChatID(chatid)
    message = "Stats for all kanji are cleared ~"
    util.send_message(message, update)

def unknown_command(update, context):
    util.send_message('Unknown command!', update)

def dbquery(update, context):
    chatid = util.getChatID(update)
    if chatid != '363854360':
        util.send_message("Unknown command!")
        return
    query = util.getMessage(update).rstip().lstrip()
    db = DBInstance()
    res = db.custom_command(query)
    
    form = "The result is:\n{}"
    if len(res) == 0:
        util.send_message(form.format("<empty>", update))
        return
    text_res = ""
    for row in res:
        text_res += ', '.join(row)
    util.send_message(form.format(text_res))
