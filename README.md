# Terminal Quiz Multiplayer
#### Author: Bocaletto Luca
#### OS: Linux

A lightweight, multiplayer quiz game running entirely in a Linux terminal. Players connect to a TCP server, register or log in, and answer multiple-choice questions loaded from an external JSON file. Scores persist across sessions and a global leaderboard can be viewed in-game or via a simple HTTP endpoint.

---

## Features

- Real-time multiplayer quiz (minimum 2 players per session)  
- Questions and answers stored in `questions.json`  
- Secure user registration & login with SHA-256 hashed passwords  
- Session scoring: +10 for correct, –5 for wrong or timed-out answers  
- Persistent global leaderboard in `data.json`  
- In-game `leaderboard` command and HTTP view at `http://<host>:8000/leaderboard`  
- Easily extendable question database by editing the JSON file  

---

## Repository Structure

```
terminal-quiz-multiplayer/
├── server.py         # TCP server logic, user & game management
├── client.py         # Terminal client interface
├── questions.json    # External database of quiz questions
└── data.json*        # Auto-generated user data & scores
```

_\* `data.json` is created on first server run._

---

## Prerequisites

- Python 3.6 or higher  
- No third-party dependencies (uses only Python standard library)  
- Linux environment (tested on Debian/Ubuntu)

---

## Installation

1. Clone the repo  
   ```bash
   git clone https://github.com/bocaletto-luca/terminal-quiz-multiplayer.git
   cd terminal-quiz-multiplayer
   ```

2. (Optional) Make scripts executable  
   ```bash
   chmod +x server.py client.py
   ```

---

## Running the Server

Start the quiz server on TCP port 5000 and HTTP port 8000:

```bash
./server.py
```

You should see:

```
Server listening on 0.0.0.0:5000
HTTP leaderboard available at http://0.0.0.0:8000/leaderboard
```

---

## Running a Client

In one or more separate terminals, launch:

```bash
./client.py
```

You’ll see:

```
Connected to terminal-quiz server!
```

Use the prompt to:

- `register` – create a new user  
- `login`    – authenticate an existing user  
- `start`    – queue for the next quiz session  
- `leaderboard` – view top 10 global scores  
- `exit`     – disconnect  

Once at least 2 players issue `start`, a 5-question quiz begins simultaneously for all queued players.

---

## Customizing Questions

Edit `questions.json` to add or modify entries. Each object should follow:

```json
{
  "id":       6,
  "question": "Your question text here?",
  "options":  ["Option A", "Option B", "Option C", "Option D"],
  "answer":   2        // zero-based index of the correct option
}
```

- `id` must be unique  
- `options` array length can vary  
- `answer` references the correct option index  

---

## Contributing

1. Fork the repository  
2. Create a new branch (`git checkout -b feature-name`)  
3. Make your changes and commit (`git commit -m "Add feature"`)  
4. Push to your fork (`git push origin feature-name`)  
5. Open a Pull Request detailing your improvements  

---

## License

This project is released under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html).

```
SPDX-License-Identifier: GPL-3.0-or-later
```
