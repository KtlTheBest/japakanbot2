import config
import handlers

import datetime

from util import *

from telegram.ext import (
    Updater,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters
)

ENTER_KANJI = 0

def main():
    updater = Updater(config.TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher



    add_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('add', handlers.start_add_kanji)],
        states={
            ENTER_KANJI: [
                MessageHandler(Filters.regex('^.+? .+$'), handlers.receive_add_kanji),
                CommandHandler('done', handlers.finish_receive_kanji),
                MessageHandler(Filters.text, handlers.wrong_receive_kanji)
            ],
        },
        fallbacks=[CommandHandler('done', handlers.finish_receive_kanji)],
        name='add_kanji'
    )

    fix_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('fix', handlers.start_fix_kanji)],
        states={
            ENTER_KANJI: [
                MessageHandler(Filters.regex('^.+? .+$'), handlers.receive_add_kanji),
                CommandHandler('done', handlers.finish_receive_kanji),
                MessageHandler(Filters.text, handlers.wrong_receive_kanji)
            ],
        },
        fallbacks=[CommandHandler('done', handlers.finish_receive_kanji)],
        name='fix_kanji'
    )

    del_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('delete', handlers.start_delete_kanji)],
        states={
            ENTER_KANJI: [
                CommandHandler('done', handlers.finish_receive_kanji),
                MessageHandler(Filters.regex('^.+'), handlers.receive_delete_kanji),
            ],
        },
        fallbacks=[CommandHandler('done', handlers.finish_receive_kanji)],
        name='del_kanji'
    )
    
    dispatcher.add_handler(add_conv_handler)
    dispatcher.add_handler(fix_conv_handler)
    dispatcher.add_handler(del_conv_handler)

    dispatcher.add_handler(CommandHandler('start', handlers.start))
    dispatcher.add_handler(CommandHandler('quiz', handlers.show_cur_quiz_kanji))
    dispatcher.add_handler(CommandHandler('list', handlers.show_kanji_list))
    dispatcher.add_handler(CommandHandler('stats', handlers.show_stats))
    dispatcher.add_handler(CommandHandler('clearstats', handlers.clear_stats))
    dispatcher.add_handler(CommandHandler('help', handlers.help))
    dispatcher.add_handler(CommandHandler('dbquery', handlers.dbquery))
    dispatcher.add_handler(MessageHandler(Filters.regex('^/.+'), handlers.unknown_command))

    guess_handler = MessageHandler(Filters.text, handlers.check_guess)
    dispatcher.add_handler(guess_handler)

    job_queue = updater.job_queue
    send_kanji_10am = job_queue.run_daily(handlers.remind_to_study_kanji, days=(0, 1, 2, 3, 4, 5, 6), time=datetime.time(hour=10, minute=0, second=0))
    send_kanji_3pm  = job_queue.run_daily(handlers.remind_to_study_kanji, days=(0, 1, 2, 3, 4, 5, 6), time=datetime.time(hour=15, minute=0, second=0))
    send_kanji_9pm  = job_queue.run_daily(handlers.remind_to_study_kanji, days=(0, 1, 2, 3, 4, 5, 6), time=datetime.time(hour=21, minute=0, second=0))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
