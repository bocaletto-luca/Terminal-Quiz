#!/usr/bin/env python3
import socket, threading, json

HOST = '127.0.0.1'
PORT = 5000

def send(sock, msg):
    sock.sendall((json.dumps(msg)+'\n').encode())

def recv(sock):
    buf = b''
    while not buf.endswith(b'\n'):
        part = sock.recv(1024)
        if not part:
            return None
        buf += part
    return json.loads(buf.decode().strip())

def listener(sock):
    while True:
        msg = recv(sock)
        if not msg:
            break
        t = msg.get('type')

        if t == 'question':
            print(f"\nDomanda #{msg['id']}: {msg['question']}")
            for i,o in enumerate(msg['options']):
                print(f"  {i}. {o}")
            ans = input("Risposta (numero): ")
            send(sock, {'type':'answer','id':msg['id'],'choice':int(ans)})

        elif t == 'result':
            status = "CORRETTO" if msg['correct'] else "SBAGLIATO"
            print(f"[{status}] Punteggio: {msg['score']}")

        elif t == 'session_end':
            print("\n-- Fine sessione --")
            for e in msg['ranking']:
                print(f"  {e['user']}: {e['pts']} pt")
            print()

        elif t in ('ok','info','error'):
            print(f"[{t.upper()}] {msg.get('msg')}")

        elif t == 'leaderboard':
            print("\n-- Classifica Globale --")
            for e in msg['entries']:
                print(f"  {e['user']}: {e['score']} pt")
            print()

        else:
            print(msg)

def main():
    sock = socket.socket()
    sock.connect((HOST, PORT))
    threading.Thread(target=listener, args=(sock,), daemon=True).start()
    print("Connesso a LinQuiz!")

    while True:
        cmd = input("Comando (register/login/start/leaderboard/exit): ").strip()
        if cmd == 'register':
            u = input("Username: "); p = input("Password: ")
            send(sock, {'type':'register','user':u,'pass':p})

        elif cmd == 'login':
            u = input("Username: "); p = input("Password: ")
            send(sock, {'type':'login','user':u,'pass':p})

        elif cmd == 'start':
            send(sock, {'type':'start'})

        elif cmd == 'leaderboard':
            send(sock, {'type':'leaderboard'})

        elif cmd == 'exit':
            send(sock, {'type':'exit'})
            break

        else:
            print("Comando non riconosciuto.")

    sock.close()
    print("Disconnesso da LinQuiz.")

if __name__ == '__main__':
    main()
