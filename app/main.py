#!/usr/bin/env python3
import json
import os
import sqlite3
import time
import uuid
import hmac
import hashlib
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "learning_failure_lab.db"
STATIC_DIR = ROOT / "static"
SECRET = os.getenv("APP_SECRET", "dev-secret-change-me")
TOKEN_TTL = 60 * 60 * 8


def now_ts():
    return int(time.time())


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def make_token(user_id: str, role: str) -> str:
    payload = f"{user_id}.{role}.{now_ts()+TOKEN_TTL}"
    sig = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    raw = f"{payload}.{sig}".encode()
    return base64.urlsafe_b64encode(raw).decode()


def verify_token(token: str):
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        user_id, role, exp, sig = raw.split(".")
        payload = f"{user_id}.{role}.{exp}"
        expected = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            return None
        if int(exp) < now_ts():
            return None
        return {"user_id": user_id, "role": role}
    except Exception:
        return None


def db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = db_conn()
    cur = conn.cursor()
    cur.executescript(
        """
        PRAGMA foreign_keys = ON;
        CREATE TABLE IF NOT EXISTS users (
          id TEXT PRIMARY KEY,
          email TEXT UNIQUE NOT NULL,
          password_hash TEXT NOT NULL,
          full_name TEXT NOT NULL,
          role TEXT NOT NULL CHECK (role IN ('STUDENT','TEACHER','ADMIN')),
          created_at INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS topics (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          description TEXT
        );

        CREATE TABLE IF NOT EXISTS questions (
          id TEXT PRIMARY KEY,
          topic_id TEXT NOT NULL REFERENCES topics(id),
          content TEXT NOT NULL,
          difficulty INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS options (
          id TEXT PRIMARY KEY,
          question_id TEXT NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
          content TEXT NOT NULL,
          is_correct INTEGER NOT NULL DEFAULT 0,
          error_type TEXT,
          error_note TEXT
        );

        CREATE TABLE IF NOT EXISTS sessions (
          id TEXT PRIMARY KEY,
          user_id TEXT NOT NULL REFERENCES users(id),
          topic_id TEXT NOT NULL REFERENCES topics(id),
          status TEXT NOT NULL CHECK (status IN ('IN_PROGRESS','SUBMITTED')),
          started_at INTEGER NOT NULL,
          submitted_at INTEGER
        );

        CREATE TABLE IF NOT EXISTS attempts (
          id TEXT PRIMARY KEY,
          session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
          question_id TEXT NOT NULL REFERENCES questions(id),
          selected_option_id TEXT NOT NULL REFERENCES options(id),
          is_correct INTEGER NOT NULL,
          latency_ms INTEGER,
          created_at INTEGER NOT NULL,
          UNIQUE (session_id, question_id)
        );
        """
    )

    cur.execute("SELECT COUNT(*) AS c FROM topics")
    if cur.fetchone()["c"] == 0:
        topics = [
            (str(uuid.uuid4()), "Toán", "Suy luận và giải bài toán"),
            (str(uuid.uuid4()), "Tiếng Anh", "Đọc hiểu ngữ cảnh"),
            (str(uuid.uuid4()), "Khoa học", "Nguyên nhân - kết quả"),
        ]
        cur.executemany("INSERT INTO topics(id,name,description) VALUES(?,?,?)", topics)
        math_topic = topics[0][0]
        english_topic = topics[1][0]
        science_topic = topics[2][0]
        qid = str(uuid.uuid4())
        cur.execute("INSERT INTO questions(id,topic_id,content,difficulty) VALUES(?,?,?,?)", (qid, math_topic, "Nếu 2x + 3 = 11 thì x bằng bao nhiêu?", 1))
        opts = [
            (str(uuid.uuid4()), qid, "4", 1, None, None),
            (str(uuid.uuid4()), qid, "7", 0, "CONFUSION", "Nhầm chuyển vế"),
            (str(uuid.uuid4()), qid, "5", 0, "LOGIC_GAP", "Quên chia 2"),
            (str(uuid.uuid4()), qid, "3", 0, "RANDOM_GUESS", "Đoán nhanh"),
        ]
        cur.executemany("INSERT INTO options(id,question_id,content,is_correct,error_type,error_note) VALUES(?,?,?,?,?,?)", opts)

        qid2 = str(uuid.uuid4())
        cur.execute("INSERT INTO questions(id,topic_id,content,difficulty) VALUES(?,?,?,?)", (qid2, math_topic, "Giá trị của 3(2 + 1) là?", 1))
        opts2 = [
            (str(uuid.uuid4()), qid2, "9", 1, None, None),
            (str(uuid.uuid4()), qid2, "7", 0, "MISCONCEPTION", "Hiểu sai phân phối"),
            (str(uuid.uuid4()), qid2, "6", 0, "LOGIC_GAP", "Nhảy bước tính"),
            (str(uuid.uuid4()), qid2, "5", 0, "RANDOM_GUESS", "Đoán mò"),
        ]
        cur.executemany("INSERT INTO options(id,question_id,content,is_correct,error_type,error_note) VALUES(?,?,?,?,?,?)", opts2)

        qid3 = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO questions(id,topic_id,content,difficulty) VALUES(?,?,?,?)",
            (qid3, english_topic, "Chọn câu đúng ngữ pháp: She ___ to school every day.", 1),
        )
        opts3 = [
            (str(uuid.uuid4()), qid3, "goes", 1, None, None),
            (str(uuid.uuid4()), qid3, "go", 0, "MISCONCEPTION", "Sai chia động từ ngôi thứ ba số ít"),
            (str(uuid.uuid4()), qid3, "going", 0, "CONFUSION", "Nhầm dạng V-ing với thì hiện tại đơn"),
            (str(uuid.uuid4()), qid3, "gone", 0, "RANDOM_GUESS", "Đoán ngẫu nhiên"),
        ]
        cur.executemany("INSERT INTO options(id,question_id,content,is_correct,error_type,error_note) VALUES(?,?,?,?,?,?)", opts3)

        qid4 = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO questions(id,topic_id,content,difficulty) VALUES(?,?,?,?)",
            (qid4, science_topic, "Khí CO2 tăng gây hiệu ứng gì chính trong khí hậu?", 1),
        )
        opts4 = [
            (str(uuid.uuid4()), qid4, "Tăng hiệu ứng nhà kính", 1, None, None),
            (str(uuid.uuid4()), qid4, "Giảm nhiệt độ Trái Đất ngay lập tức", 0, "MISCONCEPTION", "Hiểu sai cơ chế nhà kính"),
            (str(uuid.uuid4()), qid4, "Không ảnh hưởng gì đến khí hậu", 0, "LOGIC_GAP", "Bỏ qua quan hệ nguyên nhân-kết quả"),
            (str(uuid.uuid4()), qid4, "Làm nước biển mặn hơn trực tiếp", 0, "RANDOM_GUESS", "Đoán mò"),
        ]
        cur.executemany("INSERT INTO options(id,question_id,content,is_correct,error_type,error_note) VALUES(?,?,?,?,?,?)", opts4)

    cur.execute("SELECT COUNT(*) AS c FROM users")
    if cur.fetchone()["c"] == 0:
        cur.execute(
            "INSERT INTO users(id,email,password_hash,full_name,role,created_at) VALUES(?,?,?,?,?,?)",
            (str(uuid.uuid4()), "admin@lab.local", hash_password("Admin123!"), "System Admin", "ADMIN", now_ts()),
        )
    conn.commit()
    conn.close()


class Handler(BaseHTTPRequestHandler):
    def _json(self, code, data):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def _body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _auth(self):
        header = self.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return None
        return verify_token(header[7:])

    def _serve_static(self, path):
        if path == "/":
            path = "/index.html"
        target = (STATIC_DIR / path.lstrip("/")).resolve()
        if not str(target).startswith(str(STATIC_DIR.resolve())) or not target.exists():
            self.send_error(404)
            return
        ctype = "text/plain"
        if str(target).endswith(".html"):
            ctype = "text/html; charset=utf-8"
        elif str(target).endswith(".css"):
            ctype = "text/css; charset=utf-8"
        elif str(target).endswith(".js"):
            ctype = "application/javascript; charset=utf-8"
        raw = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if not path.startswith("/api/"):
            return self._serve_static(path)

        user = self._auth()

        if path == "/api/v1/topics":
            if not user:
                return self._json(401, {"error": "Unauthorized"})
            conn = db_conn()
            rows = conn.execute("SELECT id,name,description FROM topics ORDER BY name").fetchall()
            conn.close()
            return self._json(200, {"data": [dict(r) for r in rows]})

        if path == "/api/v1/questions":
            if not user:
                return self._json(401, {"error": "Unauthorized"})
            topic_id = parse_qs(parsed.query).get("topicId", [None])[0]
            conn = db_conn()
            rows = conn.execute(
                "SELECT id,content,difficulty FROM questions WHERE topic_id = ? ORDER BY difficulty, rowid",
                (topic_id,),
            ).fetchall()
            data = []
            for r in rows:
                opts = conn.execute(
                    "SELECT id,content FROM options WHERE question_id = ? ORDER BY rowid", (r["id"],)
                ).fetchall()
                data.append({"id": r["id"], "content": r["content"], "difficulty": r["difficulty"], "options": [dict(x) for x in opts]})
            conn.close()
            return self._json(200, {"data": data})

        if path == "/api/v1/me/analytics/errors":
            if not user:
                return self._json(401, {"error": "Unauthorized"})
            conn = db_conn()
            rows = conn.execute(
                """
                SELECT COALESCE(o.error_type, 'NONE') AS error_type, COUNT(*) AS total
                FROM attempts a
                JOIN options o ON o.id = a.selected_option_id
                JOIN sessions s ON s.id = a.session_id
                WHERE s.user_id = ? AND a.is_correct = 0
                GROUP BY COALESCE(o.error_type, 'NONE')
                ORDER BY total DESC
                """,
                (user["user_id"],),
            ).fetchall()
            conn.close()
            return self._json(200, {"data": [dict(r) for r in rows]})

        self._json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._body()

        if path == "/api/v1/auth/register":
            for k in ["email", "password", "fullName"]:
                if not body.get(k):
                    return self._json(400, {"error": f"Missing {k}"})
            uid = str(uuid.uuid4())
            conn = db_conn()
            try:
                conn.execute(
                    "INSERT INTO users(id,email,password_hash,full_name,role,created_at) VALUES(?,?,?,?,?,?)",
                    (uid, body["email"].lower(), hash_password(body["password"]), body["fullName"], "STUDENT", now_ts()),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                conn.close()
                return self._json(409, {"error": "Email already exists"})
            conn.close()
            token = make_token(uid, "STUDENT")
            return self._json(201, {"data": {"accessToken": token, "role": "STUDENT"}})

        if path == "/api/v1/auth/login":
            email = (body.get("email") or "").lower()
            password = body.get("password") or ""
            conn = db_conn()
            row = conn.execute("SELECT id,password_hash,role,full_name FROM users WHERE email = ?", (email,)).fetchone()
            conn.close()
            if not row or row["password_hash"] != hash_password(password):
                return self._json(401, {"error": "Invalid credentials"})
            token = make_token(row["id"], row["role"])
            return self._json(200, {"data": {"accessToken": token, "role": row["role"], "fullName": row["full_name"]}})

        user = self._auth()
        if not user:
            return self._json(401, {"error": "Unauthorized"})

        if path == "/api/v1/sessions":
            topic_id = body.get("topicId")
            if not topic_id:
                return self._json(400, {"error": "Missing topicId"})
            sid = str(uuid.uuid4())
            conn = db_conn()
            conn.execute(
                "INSERT INTO sessions(id,user_id,topic_id,status,started_at) VALUES(?,?,?,?,?)",
                (sid, user["user_id"], topic_id, "IN_PROGRESS", now_ts()),
            )
            conn.commit()
            conn.close()
            return self._json(201, {"data": {"sessionId": sid}})

        if path.startswith("/api/v1/sessions/") and path.endswith("/attempts"):
            parts = path.strip("/").split("/")
            session_id = parts[3]
            qid = body.get("questionId")
            oid = body.get("selectedOptionId")
            latency_ms = int(body.get("latencyMs") or 0)
            conn = db_conn()
            is_owner = conn.execute("SELECT id FROM sessions WHERE id = ? AND user_id = ? AND status='IN_PROGRESS'", (session_id, user["user_id"])).fetchone()
            if not is_owner:
                conn.close()
                return self._json(403, {"error": "Session denied"})
            opt = conn.execute("SELECT is_correct FROM options WHERE id = ? AND question_id = ?", (oid, qid)).fetchone()
            if not opt:
                conn.close()
                return self._json(400, {"error": "Invalid option/question"})
            try:
                conn.execute(
                    "INSERT INTO attempts(id,session_id,question_id,selected_option_id,is_correct,latency_ms,created_at) VALUES(?,?,?,?,?,?,?)",
                    (str(uuid.uuid4()), session_id, qid, oid, int(opt["is_correct"]), latency_ms, now_ts()),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                conn.close()
                return self._json(409, {"error": "Question already answered"})
            conn.close()
            return self._json(201, {"data": {"isCorrect": bool(opt["is_correct"])}})

        if path.startswith("/api/v1/sessions/") and path.endswith("/submit"):
            parts = path.strip("/").split("/")
            session_id = parts[3]
            conn = db_conn()
            session = conn.execute("SELECT id,status FROM sessions WHERE id = ? AND user_id = ?", (session_id, user["user_id"])).fetchone()
            if not session:
                conn.close()
                return self._json(403, {"error": "Session denied"})
            if session["status"] == "SUBMITTED":
                conn.close()
                return self._json(409, {"error": "Session already submitted"})

            rows = conn.execute(
                """
                SELECT a.is_correct, o.error_type, o.error_note
                FROM attempts a
                JOIN options o ON o.id = a.selected_option_id
                WHERE a.session_id = ?
                """,
                (session_id,),
            ).fetchall()
            total = len(rows)
            if total == 0:
                conn.close()
                return self._json(400, {"error": "No attempts submitted"})
            correct = sum(1 for r in rows if r["is_correct"] == 1)
            errors = {}
            for r in rows:
                if r["is_correct"] == 0:
                    et = r["error_type"] or "UNKNOWN"
                    errors[et] = errors.get(et, 0) + 1
            conn.execute("UPDATE sessions SET status='SUBMITTED', submitted_at=? WHERE id=?", (now_ts(), session_id))
            conn.commit()
            conn.close()
            return self._json(
                200,
                {
                    "data": {
                        "score": 0 if total == 0 else round(correct * 100 / total, 2),
                        "total": total,
                        "correct": correct,
                        "errorBreakdown": errors,
                    }
                },
            )

        self._json(404, {"error": "Not found"})


def run():
    init_db()
    port = int(os.getenv("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Learning Failure Lab running at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
