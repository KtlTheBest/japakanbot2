import sqlite3

class DBInstance:

    def __init__(self, database_name='japakana.db', check_same_thread=False):
        self.db_name = database_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=check_same_thread)

        self.setUpDB()

    def setUpUsersTable(self):
        stmt = 'CREATE TABLE IF NOT EXISTS users ( \
            username TEXT,           \
            name TEXT,               \
            chatid TEXT,             \
            PRIMARY KEY( chatid )    \
        );' 

        cursor = self.conn.cursor()
        cursor.execute(stmt)
        self.conn.commit()

    def setUpUserKanjiTable(self):
        stmt = 'CREATE TABLE IF NOT EXISTS user_kanji ( \
            kanji TEXT,                   \
            romaji TEXT,                  \
            chatid TEXT,                  \
            count INT,                    \
            PRIMARY KEY( chatid, kanji )  \
        );' 

        cursor = self.conn.cursor()
        cursor.execute(stmt)
        self.conn.commit()

    def setUpUserKanjiQuiz(self):
        stmt = 'CREATE TABLE IF NOT EXISTS kanji_quiz ( \
            kanji TEXT,                   \
            romaji TEXT,                  \
            chatid TEXT,                  \
            PRIMARY KEY( chatid )         \
        );' 

        cursor = self.conn.cursor()
        cursor.execute(stmt)
        self.conn.commit()

    def setUpDB(self):
        self.setUpUsersTable()
        self.setUpUserKanjiTable()
        self.setUpUserKanjiQuiz()
    
    def chatExists(self, chatid):
        stmt = 'SELECT chatid FROM users WHERE chatid = ?;'
        
        cursor = self.conn.cursor()
        res = cursor.execute(stmt, (chatid,)).fetchall()

        return len(res) > 0

    def getQuizKanjiForChatID(self, chatid):
        stmt = 'SELECT kanji, romaji FROM kanji_quiz WHERE chatid = ?;'
        
        cursor = self.conn.cursor()
        return cursor.execute(stmt, (chatid,)).fetchall()

    def getKanjiListForChatID(self, chatid):
        stmt = 'SELECT kanji, romaji FROM user_kanji WHERE chatid = ?;'
        
        cursor = self.conn.cursor()
        return cursor.execute(stmt, (chatid,)).fetchall()
    
    def getChats(self):
        stmt = 'SELECT chatid FROM users;'
        
        cursor = self.conn.cursor()
        return cursor.execute(stmt).fetchall()

    def addNewUser(self, username, name, chatid):
        if not self.chatExists( chatid ):
            stmt = 'INSERT INTO users VALUES (?, ?, ?)'
            cursor = self.conn.cursor()
            cursor.execute(stmt, (username, name, chatid))
            self.conn.commit()

    def addKanji(self, chatid, kanji, romaji):
        check_stmt = 'SELECT kanji FROM user_kanji WHERE kanji = ?;'
        cursor = self.conn.cursor()
        short_res = cursor.execute(check_stmt, (kanji,)).fetchall()

        if len(short_res) == 0:
            stmt = 'INSERT INTO user_kanji VALUES (?, ?, ?, 0);'
            cursor.execute(stmt, (kanji, romaji, chatid))
            self.conn.commit()
        else:
            print("DEBUG: addKanji: here!")
            stmt = 'UPDATE user_kanji SET romaji = ? WHERE kanji = ? AND chatid = ?;'
            cursor.execute(stmt, (romaji, kanji, chatid))
            self.conn.commit()

    def getUserKanjiList(self, chatid):
        stmt = 'SELECT count, kanji, romaji FROM user_kanji WHERE chatid = ?;'

        cursor = self.conn.cursor()
        res = cursor.execute(stmt, (chatid,)).fetchall()

        return res

    def getQuizStatsForChatID(self, chatid):
        stmt = 'SELECT kanji, count FROM user_kanji WHERE chatid = ?;'

        cursor = self.conn.cursor()
        res = cursor.execute(stmt, (chatid,)).fetchall()

        return res

    def clearQuizStatsForChatID(self, chatid):
        stmt = 'UPDATE user_kanji SET count = 0 WHERE chatid = ?;'

        cursor = self.conn.cursor()
        cursor.execute(stmt, (chatid,))
        self.conn.commit()

    def updateCountKanji(self, chatid, kanji, count):
        stmt = 'UPDATE user_kanji SET count = count + ? WHERE chatid = ? AND kanji = ?;'

        cursor = self.conn.cursor()
        cursor.execute(stmt, (count, chatid, kanji))
        self.conn.commit()

    def updateRomaji(self, chatid, kanji, romaji):
        stmt = 'UPDATE user_kanji SET romaji = ? WHERE chatid = ? AND kanji = ?;'

        cursor = self.conn.cursor()
        cursor.execute(stmt, (romaji, chatid, kanji))
        self.conn.commit()

    def deleteKanji(self, chatid, kanji):
        stmt = 'DELETE FROM user_kanji WHERE chatid = ? AND kanji = ?;'

        cursor = self.conn.cursor()
        cursor.execute(stmt, (chatid, kanji))
        self.conn.commit()

    def setKanjiQuizForChatID(self, chatid, kanji, romaji):
        stmt = 'INSERT INTO kanji_quiz VALUES (?, ?, ?);'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (kanji, romaji, chatid))
        self.conn.commit()

    def clearKanjiQuizForChatID(self, chatid):
        stmt = 'DELETE FROM kanji_quiz WHERE chatid = ?;'
        cursor = self.conn.cursor()
        cursor.execute(stmt, (chatid,))
        self.conn.commit()
