#!/usr/bin/env python3
import socket, threading, json, hashlib, os, random

HOST = '0.0.0.0'
PORT = 5000
USERS_FILE = 'data.json'
QUESTIONS_FILE = 'questions.json'
MIN_PLAYERS = 2
QUESTIONS_PER_GAME = 5
ANSWER_TIMEOUT = 15  # secondi

lock = threading.Lock()
waiting = []  # [(conn, user), ...]

def init_data():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE,'w') as f:
            json.dump({'users': {}}, f, indent=2)

def load_users():
    with lock:
        return json.load(open(USERS_FILE))

def save_users(d):
    with lock:
        json.dump(d, open(USERS_FILE,'w'), indent=2)

def load_questions():
    return json.load(open(QUESTIONS_FILE))

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def send(conn, msg):
    conn.sendall((json.dumps(msg) + '\n').encode())

def recv(conn):
    buf = b''
    while not buf.endswith(b'\n'):
        part = conn.recv(1024)
        if not part:
            return None
        buf += part
    try:
        return json.loads(buf.decode().strip())
    except:
        return None

def broadcast(players, msg):
    for c,_ in players:
        send(c, msg)

def game_session(players):
    users = load_users()
    questions = load_questions()
    qs = random.sample(questions, min(QUESTIONS_PER_GAME, len(questions)))
    scores = {u:0 for _,u in players}

    for q in qs:
        broadcast(players, {
            'type':'question',
            'id': q['id'],
            'question': q['question'],
            'options': q['options']
        })
        answers = {}
        for conn, user in players:
            conn.settimeout(ANSWER_TIMEOUT)
            try:
                r = recv(conn)
                if r and r.get('type')=='answer' and r.get('id')==q['id']:
                    answers[user] = r.get('choice')
                else:
                    answers[user] = None
            except:
                answers[user] = None

        for conn, user in players:
            correct = (answers[user] == q['answer'])
            delta = 10 if correct else -5
            scores[user] += delta
            send(conn, {
                'type':'result',
                'correct': correct,
                'score': scores[user]
            })

    ranking = sorted(scores.items(), key=lambda x: -x[1])
    broadcast(players, {
        'type':'session_end',
        'ranking': [{'user':u,'pts':p} for u,p in ranking]
    })

    users = load_users()
    for u, pts in scores.items():
        users['users'][u]['score'] = users['users'][u].get('score', 0) + pts
    save_users(users)

def handle(conn, _):
    auth = False
    user = None
    init_data()
    while True:
        req = recv(conn)
        if not req:
            break
        t = req.get('type')

        if t == 'register':
            u,p = req['user'], req['pass']
            data = load_users()
            if u in data['users']:
                send(conn, {'type':'error','msg':'Utente esistente'})
            else:
                data['users'][u] = {
                    'password_hash': hash_pw(p),
                    'score': 0
                }
                save_users(data)
                send(conn, {'type':'ok','msg':'Registrazione OK'})

        elif t == 'login':
            u,p = req['user'], req['pass']
            data = load_users()
            if u in data['users'] and data['users'][u]['password_hash']==hash_pw(p):
                auth, user = True, u
                send(conn, {'type':'ok','msg':'Login OK'})
            else:
                send(conn, {'type':'error','msg':'Credenziali errate'})

        elif t == 'start' and auth:
            send(conn, {'type':'info','msg':'In attesa...'})
            with lock:
                waiting.append((conn, user))
                if len(waiting) >= MIN_PLAYERS:
                    players = waiting.copy()
                    waiting.clear()
                    threading.Thread(target=game_session, args=(players,), daemon=True).start()

        elif t == 'leaderboard' and auth:
            data = load_users()
            ranked = sorted(data['users'].items(),
                            key=lambda x: -x[1]['score'])
            top = [{'user':u,'score':info['score']} for u,info in ranked[:10]]
            send(conn, {'type':'leaderboard','entries': top})

        elif t == 'exit':
            break

        else:
            send(conn, {'type':'error','msg':'Comando non valido'})

    conn.close()

def main():
    init_data()
    sock = socket.socket()
    sock.bind((HOST, PORT))
    sock.listen()
    print(f"Server in ascolto su {HOST}:{PORT}")
    while True:
        conn, addr = sock.accept()
        threading.Thread(target=handle, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    main()
