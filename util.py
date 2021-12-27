import random
from db import DBInstance

def send_message(msg, update):
    update.message.reply_text(msg)

def getUsername(update):
    return update.effective_user.username

def getName(update):
    return update.effective_user.full_name

def getChatID(update):
    return update.effective_chat.id

def getMessage(update):
    return update['message']['text']

def getRandomKanji(kanji_list):
    lptr = 0
    rptr = len(kanji_list) - 1

    kanji_list = sorted(kanji_list, key=lambda x: x[0])
    counts = {}
    minval = kanji_list[0][0]

    for row in kanji_list:
        new_count = row[0] - minval + 1
        if new_count in counts.keys():
            counts[new_count].append([row[1], row[2]])
        else:
            counts[new_count] = [[row[1], row[2]]]
    
    count_values = list(counts.keys())
    total_sum = sum(count_values)

    kanji, romaji = None, None

    i = 0
    while kanji is None and romaji is None:
        threshold = total_sum - (count_values[i])
        randval = random.randrange(0, total_sum)
        if randval > threshold:
            i += 1
            if i == len(count_values): i = 0
            continue
        else:
            index = random.randrange(0, len(counts[count_values[i]]))
            kanji, romaji = counts[count_values[i]][index]

    return kanji, romaji

def setRandomKanji(chatid):
    db = DBInstance()
    res = db.getQuizKanjiForChatID(chatid)
    if len(res) != 0: db.clearKanjiQuizForChatID(chatid)
    kanji_list = db.getUserKanjiList(chatid)
    if len(kanji_list) == 0: return
    kanji, romaji = getRandomKanji(kanji_list)
    db.setKanjiQuizForChatID(chatid, kanji, romaji)

