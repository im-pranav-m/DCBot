import sqlite3
from datetime import datetime,timedelta

connect = sqlite3.connect("data/userinfo.db")
cursor = connect.cursor()

def update_database(userid, username, xp, coins, vcmins, cammins, streammins):
    current_date = datetime.now().strftime("%Y-%m-%d")  # Format: YYYY-MM-DD

    # Check if the user already exists
    cursor.execute("SELECT 1 FROM userinfo WHERE userid = ?", (userid,))
    user_exists = cursor.fetchone()

    if user_exists:
        # Update the existing user record
        cursor.execute("""
            UPDATE userinfo
            SET username = ?,
                xp = xp + ?,
                coins = coins + ?,
                vcmins = vcmins + ?,
                cammins = cammins + ?,
                streammins = streammins + ?,
                datevc = ?
            WHERE userid = ?
        """, (username, xp, coins, vcmins, cammins, streammins, current_date, userid))
    else:
        # Insert a new record for the user
        cursor.execute("""
            INSERT INTO userinfo (userid, username, xp, coins, vcmins, cammins, streammins, datevc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (userid, username, xp, coins, vcmins, cammins, streammins, current_date))

    connect.commit()

def get_user_vc(userid):
    cursor.execute("SELECT vcmins FROM userinfo WHERE userid = ?", (userid,))
    result = cursor.fetchone()  # Returns a tuple like (500,)
    return result[0] if result else 0  # Return XP as int, or 0 if not found

def get_user_cam(userid):
    cursor.execute("SELECT cammins FROM userinfo WHERE userid = ?", (userid,))
    result = cursor.fetchone()  # Returns a tuple like (500,)
    return result[0] if result else 0  # Return XP as int, or 0 if not found

def get_user_stream(userid):
    cursor.execute("SELECT streammins FROM userinfo WHERE userid = ?", (userid,))
    result = cursor.fetchone()  # Returns a tuple like (500,)
    return result[0] if result else 0  # Return XP as int, or 0 if not found

def get_user_coins(userid):
    cursor.execute("SELECT coins FROM userinfo WHERE userid = ?", (userid,))
    result = cursor.fetchone()  # Returns a tuple like (500,)
    return result[0] if result else 0  # Return XP as int, or 0 if not found

def get_user_xp(userid):
    cursor.execute("SELECT xp FROM userinfo WHERE userid = ?", (userid,))
    result = cursor.fetchone()  # Returns a tuple like (500,)
    return result[0] if result else 0  # Return XP as int, or 0 if not found

def isStreak(userid):
    # Get last activity date from userinfo
    cursor.execute("SELECT datevc FROM userinfo WHERE userid = ?", (userid,))
    result = cursor.fetchone()

    if not result or not result[0]:  
        return False  # No record found

    last_date = datetime.strptime(result[0], "%Y-%m-%d").date()
    today = datetime.today().date()

    # Check if the user exists in the streaks table
    cursor.execute("SELECT streakdays FROM streaks WHERE userid = ?", (userid,))
    streak_result = cursor.fetchone()

    if not streak_result:
        # If the user is not in streaks table, create a new record with streakdays = 1
        cursor.execute("INSERT INTO streaks (userid, streakdays) VALUES (?, ?)", (userid, 1))
        connect.commit()
        return True  # Consider the first day as a streak start

    if last_date == today:
        return True  # User has already logged in today

    if last_date == today - timedelta(days=1):  
        # Increase streak count since the user continued the streak
        cursor.execute("UPDATE streaks SET streakdays = streakdays + 1 WHERE userid = ?", (userid,))
        connect.commit()
        return False  # Streak continues

    # If the last login is older than yesterday, reset the streak
    cursor.execute("UPDATE streaks SET streakdays = 0 WHERE userid = ?", (userid,))
    connect.commit()
    return False  # Streak is broken

def streakdays(userid):
    cursor.execute("SELECT streakdays FROM streaks WHERE userid = ?", (userid,))
    result = cursor.fetchone()
    
    return int(result[0]) if result else 0