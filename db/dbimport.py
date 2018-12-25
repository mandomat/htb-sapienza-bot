
import requests
import re
import json
import sqlite3
import sys
import os

USERNAME = os.environ['EMAIL']
PASSWORD = os.environ['PASSWORD']

LOGIN_URL = "https://www.hackthebox.eu/login"
UNIVERSITY_URL = "https://www.hackthebox.eu/home/universities/profile/41"
UNI_RANKS_URL="https://www.hackthebox.eu/home/universities/rankings"
USER_URL = "https://www.hackthebox.eu/home/users/profile/"

def main():
    conn = sqlite3.connect('db/htb.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users(id integer PRIMARY KEY, name text, rank text, respect text, points integer, completion real)')
    c.execute('CREATE TABLE IF NOT EXISTS  users_machines(name text, userid integer, user integer, root integer,FOREIGN KEY(userid) REFERENCES users(id))')
    c.execute('CREATE TABLE IF NOT EXISTS  universities(rank integer, name text PRIMARY KEY, students integer, respect integer, country integer, points integer, ownership real, challenges integer, users integer, systems integer, fortresses integer, endgames integer)')
    c.execute("CREATE VIEW IF NOT EXISTS  machines_view(name,users,roots) AS SELECT users_machines.name, sum(user) as users, sum(root) as roots FROM 'users_machines' join 'users' on userid = id group BY users_machines.name ORDER BY roots")

    print("* Start * ")
    print("- Retrieving universities")

    get_uni_ranks(conn)
    print("- Done")

    print("- Retrieving users")
    get_all_users_stats(conn)
    print("- Done")
    query_result = c.execute("SELECT id FROM users")

    print("- Retrieving machines")
    for userid in query_result.fetchall():
        get_user_machines_stats(userid[0],conn)

    print("* Done * ")
    conn.close()

def get_uni_ranks(conn):
    cookies=get_cookies()
    uni_ranks_page= requests.get(UNI_RANKS_URL,cookies=cookies, headers = dict(referer = UNI_RANKS_URL))

    check_request = check_request_success(uni_ranks_page, UNI_RANKS_URL)
    if check_request:
        uni_ranks_page = check_request

    uni_ranks_re= re.compile("<td [^>]+?>([0-9]+?)</td> <td [^>]+?><a [^>]+?>(.*?)</a></td> <td [^>]+?>([0-9]+?)</td> <td [^>]+?><span [^>]+?>\+([0-9]+?) <i [^>]+?></i></span></td> <td [^>]+?><span data-toggle=\"tooltip\" title=\"(.*?)\"><span [^>]+?></span></span></td> <td [^>]+?>([0-9]+?)</td> <td [^>]+?> <div [^>]+?> <div [^>]+?> <span [^>]+?>([0-9]+?\.?[0-9]+?)%</span> </div> </div> </td> <td [^>]+?>([0-9]+?)</td> <td [^>]+?><span [^>]+?>([0-9]+?)</span>&nbsp;.*?</td> <td [^>]+?><span [^>]+?>([0-9]+?)</span>&nbsp;.*?</td> <td [^>]+><span [^>]+>([0-9]+?)</span></td> <td [^>]+?><span [^>]+?>([0-9]+?)</span></td> ")
    uni_ranks_result = uni_ranks_re.findall(uni_ranks_page.text)

    print("Inserting " + str(uni_ranks_result))
    c = conn.cursor()
    c.executemany("INSERT OR REPLACE INTO universities VALUES(?, ?, ?, ?, ?, ?,?, ?, ?, ?, ?, ?)",uni_ranks_result)

    conn.commit()

# users info in the form {"user1":"hacker","user2":"noob",...}
def get_all_users_stats(conn):
    cookies = get_cookies()
    university_page = requests.get(UNIVERSITY_URL,cookies=cookies, headers = dict(referer = UNIVERSITY_URL))

    check_request = check_request_success(university_page, UNIVERSITY_URL)
    if check_request:
        university_page = check_request

    user_stats_re= re.compile("<a href=\"https://www\.hackthebox\.eu/home/users/profile/([0-9]+)\">(.*?)</a> <span [^>]+>\[(.*?)\]</span> </td> <td [^>]+><span [^>]+>\+([0-9]+) <i [^>]+></i></span></td> <td [^>]+><span [^>]+>([0-9]+)</span></td> <td [^>]+> <div data-toggle=\"tooltip\" title=\"([0-9]+\.?[0-9]*?)%\"")
    user_stats_result = user_stats_re.findall(university_page.text)

    print("Inserting " + str(user_stats_result))
    c = conn.cursor()
    c.executemany("INSERT OR REPLACE INTO users VALUES(?, ?, ?, ?, ?, ?)",user_stats_result)

    conn.commit()



# the specified user's stats in the form {"machine1":[user,root],"machine2":[user],...}
def get_user_machines_stats(userid, conn):
    cookies = get_cookies()
    user_url = USER_URL + str(userid)
    user_page = requests.get(user_url,cookies=cookies, headers = dict(referer = user_url))

    check_request = check_request_success(user_page, user_url)
    if check_request:
        user_page = check_request

    machine_flags_re = re.compile("<img [^>]+> [^>]+ owned (user|root) <img [^>]+> <a [^>]+>(.*?)</a>")
    machine_flags_result = machine_flags_re.findall(user_page.text)

    d = dict()
    [d [tuple[1]].append(tuple[0]) if tuple[1] in list(d.keys())
    else d.update({tuple[1]: [tuple [0]]}) for tuple in machine_flags_result]

    c = conn.cursor()
    print("Inserting " + str(d))
    for key in d:
        user = 1 if "user" in d[key] else  0
        root = 1 if "root" in d[key] else 0
        c.execute("INSERT OR REPLACE INTO users_machines VALUES (?, ?, ?, ?)",(key,userid,user,root))
    conn.commit()

# attempt to login bypassing the XSRF protection
def do_login():
    session = requests.session()
    login_page = session.get(LOGIN_URL)
    cookies = session.cookies#["hackthebox_session"]

    # Retrieve the CSRF token first
    csrf_token_re = re.compile("<meta name=\"csrf-token\" content=\"(.*?)\">")
    csrf_token = csrf_token_re.findall(login_page.text)

    # Create payload
    payload = {
        "email": USERNAME,
        "password": PASSWORD,
        "_token": csrf_token[0]
    }

    # Perform login
    login_result = session.post(LOGIN_URL, data = payload,cookies=cookies, headers = dict(referer = LOGIN_URL))

    if "These credentials do not match our records." not in login_result.text:
        save_cookies(dict(cookies))
        return session

    else:
        print("Ooops. Login Failed.")
        return None

def check_request_success(page, url):
    if "Login to Hack The Box" in page.text:
        print("Need to Login")
        session = do_login()
        if session == None:
            sys.exit()
        cookies = get_cookies()
        page = session.get(url,cookies=cookies, headers = dict(referer = url))
        return page
    else:
        return None

def get_cookies():
    with open("db/cookies","r") as f:
        cookies = json.load(f)
    return cookies

def save_cookies(new_cookies):
    with open("db/cookies","w") as f:
        json.dump(new_cookies,f)
    return

if __name__ == '__main__':
    main()
