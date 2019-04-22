import sqlite3

from datetime import datetime, timedelta

from data import code


def set_carepackage(keyword, expiration, hint):
    try:
        with sqlite3.connect(code.DATABASE) as conn:

            conn.execute(
                'UPDATE CarePackage SET Key = ?, Expiration = ?, Hint = ?', (keyword, expiration, hint,))
            conn.commit()

        return True

    except Exception as e:
        print(e)
        return False


def get_carepackage_hint():
    try:
        with sqlite3.connect(code.DATABASE) as conn:

            row = conn.execute(
                'SELECT Hint FROM CarePackage').fetchone()

        return row[0]

    except Exception as e:
        print(e)
        return False


def getKeyword():
    try:
        with sqlite3.connect(code.DATABASE) as conn:

            row = conn.execute(
                'SELECT Key FROM CarePackage').fetchone()

            return row[0]

    except Exception as e:
        print(e)
        return False


def remove_expired_carepackage():
    try:
        with sqlite3.connect(code.DATABASE) as conn:

            now = datetime.now().timestamp()

            row = conn.execute(
                'SELECT COUNT() FROM CarePackage WHERE Expiration < ?', (now,)).fetchone()

            if row is not None and row[0] == 1:
                conn.execute(
                    'UPDATE CarePackage SET Key = ?, Expiration = ?, Hint = ?', (None, None, None,))

                conn.commit()

                return True

            return False

    except Exception as e:
        print(e)
        return False


def get_random_reward():
    try:
        with sqlite3.connect(code.DATABASE) as conn:

            row = conn.execute(
                'SELECT id, Name FROM CarePackageRwds ORDER BY RANDOM() LIMIT 1').fetchone()

            return row

    except Exception as e:
        print(e)
        return False


def reset_carepackage():
    try:
        with sqlite3.connect(code.DATABASE) as conn:

            conn.execute(
                'UPDATE CarePackage SET Key = ?, Expiration = ?, Hint = ?', (None, None, None,))

            conn.commit()

        return True

    except Exception as e:
        print(e)
        return False


def set_user_multiplier(userId, multiplier):
    try:
        with sqlite3.connect(code.DATABASE) as conn:

            expiration = datetime.now() + timedelta(hours=24)

            conn.execute(
                'INSERT or IGNORE INTO SnipingMods (UserID) VALUES (?)', (userId,))

            conn.execute(
                'UPDATE SnipingMods SET Multiplier = ?, MultiExpiration = ? WHERE UserID = ?', (multiplier, expiration.timestamp(), userId,))

            conn.commit()

        return True

    except Exception as e:
        print(e)
        return False


def set_user_immunity(userId, expiration):
    try:
        with sqlite3.connect(code.DATABASE) as conn:
            conn.execute(
                'INSERT or IGNORE INTO SnipingMods (UserID) VALUES (?)', (userId,))

            conn.execute(
                'UPDATE SnipingMods SET ImmunExpiration = ? WHERE UserID = ?', (expiration.timestamp(), userId,))

            conn.commit()

        return True

    except Exception as e:
        print(e)
        return False


def set_user_smokebomb(userId):
    try:
        with sqlite3.connect(code.DATABASE) as conn:
            conn.execute(
                'INSERT or IGNORE INTO SnipingMods (UserID) VALUES (?)', (userId,))

            conn.execute(
                'UPDATE SnipingMods SET SmokeBomb = ? WHERE UserID = ?', (1, userId,))

            conn.commit()

        return True

    except Exception as e:
        print(e)
        return False


def set_user_potato(userId, expiration):
    try:
        with sqlite3.connect(code.DATABASE) as conn:
            conn.execute(
                'INSERT INTO HotPotato (Owner, Explosion) VALUES (?, ?)', (userId, expiration,))

            conn.commit()

        return True

    except Exception as e:
        print(e)
        return False


def has_potato(userId):
    try:
        with sqlite3.connect(code.DATABASE) as conn:
            hasPotato = conn.execute(
                'SELECT * FROM HotPotato WHERE Owner = ?', (userId,)).fetchone()

            if hasPotato is None:
                return False         

        return True

    except Exception as e:
        print(e)
        return False


def pass_potato(sender, receiver):
    try:
        with sqlite3.connect(code.DATABASE) as conn:
            conn.execute(
                'UPDATE HotPotato SET Owner = ? WHERE Owner = ?', (receiver, sender,))

            conn.commit()

        return True

    except Exception as e:
        print(e)
        return False
