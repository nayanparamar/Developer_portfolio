import hashlib
import json
import os
import secrets
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parent
STATIC_ROOT = ROOT / "static"
DB_LOCK = threading.Lock()


def load_dotenv():
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def env_int(name, default):
    try:
        return int(os.environ.get(name, str(default)))
    except ValueError:
        return default


def env_bool(name, default):
    return os.environ.get(name, str(default)).lower() in {"1", "true", "yes", "on"}


load_dotenv()

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = env_int("PORT", 4280)
DB_PATH = Path(os.environ.get("DB_PATH", str(ROOT / "data" / "portfolio_studio.db")))
SESSION_COOKIE = os.environ.get("SESSION_COOKIE_NAME", "portfolio_studio_session")
CSRF_COOKIE = os.environ.get("CSRF_COOKIE_NAME", "portfolio_studio_csrf")
PBKDF2_ITERATIONS = env_int("PBKDF2_ITERATIONS", 310000)
SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", False)

STATIC_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def db_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def table_exists(conn, table_name):
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return bool(row)


def seed_content(conn):
    if conn.execute("SELECT COUNT(*) AS count FROM site_settings").fetchone()["count"]:
        return

    conn.execute(
        """
        INSERT INTO site_settings (
          id, owner_name, owner_role, owner_location, hero_title, hero_intro,
          hero_blurb, about_title, about_body, primary_cta_label, primary_cta_url,
          secondary_cta_label, secondary_cta_url, email, phone, github_url,
          linkedin_url, twitter_url, resume_url, availability_label,
          years_experience, projects_completed, happy_clients
        ) VALUES (
          1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        (
            "Nayan Paramar",
            "Smart contract developer and security researcher",
            "India",
            "I secure smart contracts and build reliable on-chain systems.",
            "Smart contract developer and security researcher.",
            "I work across Solidity development, protocol review, security research, and production-grade Web3 systems. This portfolio is ready for my projects, audits, writeups, and research notes as they are added.",
            "About me",
            "I am Nayan Paramar, a smart contract developer and security researcher focused on secure blockchain applications, Solidity engineering, and practical vulnerability research.",
            "View projects",
            "#projects",
            "Contact me",
            "#contact",
            "nayanparamar7@gmail.com",
            "+91 9601407983",
            "https://github.com/nayanparamar",
            "#",
            "#",
            "#",
            "Available for smart contract development, audits, and security research work",
            1,
            0,
            0,
        ),
    )

    projects = [
        (
            str(uuid.uuid4()),
            1,
            "Smart Contract Portfolio",
            "Web3 security profile",
            "A portfolio space for Solidity projects, audit notes, vulnerability research, and blockchain security work.",
            "Solidity, Security Research, Python, SQLite",
            "https://github.com/nayanparamar",
            "#",
            True,
            1,
        ),
        (
            str(uuid.uuid4()),
            1,
            "Audit Notes",
            "Security research",
            "A placeholder for future smart contract audit reports, vulnerability breakdowns, and protocol review notes.",
            "Solidity, Foundry, Slither, Manual Review",
            "#",
            "#",
            True,
            2,
        ),
        (
            str(uuid.uuid4()),
            1,
            "Solidity Experiments",
            "Smart contract development",
            "A placeholder collection for contracts, proof-of-concepts, and on-chain application experiments.",
            "Solidity, Foundry, Hardhat, EVM",
            "#",
            "#",
            False,
            3,
        ),
    ]
    conn.executemany(
        """
        INSERT INTO projects (
          id, owner_id, title, category, summary, stack, github_url,
          live_url, featured, sort_order
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        projects,
    )

    experiences = [
        (
            str(uuid.uuid4()),
            1,
            "Smart Contract Developer",
            "Independent",
            "2025",
            "Present",
            "Building Solidity projects, studying protocol design, and improving security review skills through practical research.",
            1,
        ),
        (
            str(uuid.uuid4()),
            1,
            "Security Researcher",
            "Independent",
            "2025",
            "Present",
            "Researching smart contract vulnerabilities, audit methodology, and secure development practices across EVM systems.",
            2,
        ),
    ]
    conn.executemany(
        """
        INSERT INTO experiences (
          id, owner_id, role, company, start_label, end_label, summary, sort_order
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        experiences,
    )

    skills = [
        (str(uuid.uuid4()), 1, "Solidity", "Smart Contracts", 1),
        (str(uuid.uuid4()), 1, "EVM Security", "Security", 2),
        (str(uuid.uuid4()), 1, "Manual Code Review", "Security", 3),
        (str(uuid.uuid4()), 1, "Foundry", "Tooling", 4),
        (str(uuid.uuid4()), 1, "Hardhat", "Tooling", 5),
        (str(uuid.uuid4()), 1, "Protocol Research", "Research", 6),
    ]
    conn.executemany(
        """
        INSERT INTO skills (id, owner_id, label, category, sort_order)
        VALUES (?, ?, ?, ?, ?)
        """,
        skills,
    )

    testimonials = [
        (
            str(uuid.uuid4()),
            1,
            "Future Collaborator",
            "Project Owner",
            "Add a client or collaborator testimonial here once your first public feedback is ready.",
            1,
        ),
        (
            str(uuid.uuid4()),
            1,
            "Future Audit Client",
            "Protocol Team",
            "Use this space for audit feedback, bug bounty recognition, or security research acknowledgements.",
            2,
        ),
    ]
    conn.executemany(
        """
        INSERT INTO testimonials (id, owner_id, author_name, author_role, quote, sort_order)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        testimonials,
    )


def init_db():
    with DB_LOCK:
        conn = db_connection()
        try:
            if not table_exists(conn, "users"):
                conn.executescript(
                    """
                    CREATE TABLE users (
                      id TEXT PRIMARY KEY,
                      name TEXT NOT NULL,
                      email TEXT NOT NULL UNIQUE,
                      password_hash TEXT NOT NULL,
                      is_admin INTEGER NOT NULL DEFAULT 0,
                      created_at TEXT NOT NULL
                    );

                    CREATE TABLE sessions (
                      id TEXT PRIMARY KEY,
                      user_id TEXT NOT NULL,
                      created_at TEXT NOT NULL
                    );

                    CREATE TABLE site_settings (
                      id INTEGER PRIMARY KEY CHECK (id = 1),
                      owner_name TEXT NOT NULL,
                      owner_role TEXT NOT NULL,
                      owner_location TEXT NOT NULL,
                      hero_title TEXT NOT NULL,
                      hero_intro TEXT NOT NULL,
                      hero_blurb TEXT NOT NULL,
                      about_title TEXT NOT NULL,
                      about_body TEXT NOT NULL,
                      primary_cta_label TEXT NOT NULL,
                      primary_cta_url TEXT NOT NULL,
                      secondary_cta_label TEXT NOT NULL,
                      secondary_cta_url TEXT NOT NULL,
                      email TEXT NOT NULL,
                      phone TEXT NOT NULL,
                      github_url TEXT NOT NULL,
                      linkedin_url TEXT NOT NULL,
                      twitter_url TEXT NOT NULL,
                      resume_url TEXT NOT NULL,
                      availability_label TEXT NOT NULL,
                      years_experience INTEGER NOT NULL,
                      projects_completed INTEGER NOT NULL,
                      happy_clients INTEGER NOT NULL
                    );

                    CREATE TABLE projects (
                      id TEXT PRIMARY KEY,
                      owner_id INTEGER NOT NULL DEFAULT 1,
                      title TEXT NOT NULL,
                      category TEXT NOT NULL,
                      summary TEXT NOT NULL,
                      stack TEXT NOT NULL,
                      github_url TEXT NOT NULL,
                      live_url TEXT NOT NULL,
                      featured INTEGER NOT NULL DEFAULT 0,
                      sort_order INTEGER NOT NULL DEFAULT 0
                    );

                    CREATE TABLE experiences (
                      id TEXT PRIMARY KEY,
                      owner_id INTEGER NOT NULL DEFAULT 1,
                      role TEXT NOT NULL,
                      company TEXT NOT NULL,
                      start_label TEXT NOT NULL,
                      end_label TEXT NOT NULL,
                      summary TEXT NOT NULL,
                      sort_order INTEGER NOT NULL DEFAULT 0
                    );

                    CREATE TABLE skills (
                      id TEXT PRIMARY KEY,
                      owner_id INTEGER NOT NULL DEFAULT 1,
                      label TEXT NOT NULL,
                      category TEXT NOT NULL,
                      sort_order INTEGER NOT NULL DEFAULT 0
                    );

                    CREATE TABLE testimonials (
                      id TEXT PRIMARY KEY,
                      owner_id INTEGER NOT NULL DEFAULT 1,
                      author_name TEXT NOT NULL,
                      author_role TEXT NOT NULL,
                      quote TEXT NOT NULL,
                      sort_order INTEGER NOT NULL DEFAULT 0
                    );

                    CREATE TABLE contact_messages (
                      id TEXT PRIMARY KEY,
                      name TEXT NOT NULL,
                      email TEXT NOT NULL,
                      company TEXT NOT NULL,
                      budget TEXT NOT NULL,
                      message TEXT NOT NULL,
                      created_at TEXT NOT NULL
                    );

                    CREATE INDEX idx_sessions_user_id ON sessions(user_id);
                    CREATE INDEX idx_projects_order ON projects(sort_order);
                    CREATE INDEX idx_experiences_order ON experiences(sort_order);
                    CREATE INDEX idx_skills_order ON skills(sort_order);
                    CREATE INDEX idx_testimonials_order ON testimonials(sort_order);
                    CREATE INDEX idx_messages_created_at ON contact_messages(created_at DESC);
                    """
                )
                seed_content(conn)
            conn.commit()
        finally:
            conn.close()


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password, stored):
    try:
        algorithm, iterations, salt, digest = stored.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    candidate = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()
    return secrets.compare_digest(candidate, digest)


def row_to_user(row):
    if not row:
        return None
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "isAdmin": bool(row["is_admin"]),
    }


def serialize_site_settings(row):
    return {
        "ownerName": row["owner_name"],
        "ownerRole": row["owner_role"],
        "ownerLocation": row["owner_location"],
        "heroTitle": row["hero_title"],
        "heroIntro": row["hero_intro"],
        "heroBlurb": row["hero_blurb"],
        "aboutTitle": row["about_title"],
        "aboutBody": row["about_body"],
        "primaryCtaLabel": row["primary_cta_label"],
        "primaryCtaUrl": row["primary_cta_url"],
        "secondaryCtaLabel": row["secondary_cta_label"],
        "secondaryCtaUrl": row["secondary_cta_url"],
        "email": row["email"],
        "phone": row["phone"],
        "githubUrl": row["github_url"],
        "linkedinUrl": row["linkedin_url"],
        "twitterUrl": row["twitter_url"],
        "resumeUrl": row["resume_url"],
        "availabilityLabel": row["availability_label"],
        "yearsExperience": row["years_experience"],
        "projectsCompleted": row["projects_completed"],
        "happyClients": row["happy_clients"],
    }


def serialize_list_rows(rows, mapping):
    items = []
    for row in rows:
        items.append(mapping(row))
    return items


def public_site_payload(conn):
    site = conn.execute("SELECT * FROM site_settings WHERE id = 1").fetchone()
    return {
        "site": serialize_site_settings(site),
        "projects": serialize_list_rows(
            conn.execute("SELECT * FROM projects ORDER BY sort_order, title"),
            lambda row: {
                "id": row["id"],
                "title": row["title"],
                "category": row["category"],
                "summary": row["summary"],
                "stack": row["stack"],
                "githubUrl": row["github_url"],
                "liveUrl": row["live_url"],
                "featured": bool(row["featured"]),
                "sortOrder": row["sort_order"],
            },
        ),
        "experiences": serialize_list_rows(
            conn.execute("SELECT * FROM experiences ORDER BY sort_order, start_label DESC"),
            lambda row: {
                "id": row["id"],
                "role": row["role"],
                "company": row["company"],
                "startLabel": row["start_label"],
                "endLabel": row["end_label"],
                "summary": row["summary"],
                "sortOrder": row["sort_order"],
            },
        ),
        "skills": serialize_list_rows(
            conn.execute("SELECT * FROM skills ORDER BY sort_order, label"),
            lambda row: {
                "id": row["id"],
                "label": row["label"],
                "category": row["category"],
                "sortOrder": row["sort_order"],
            },
        ),
        "testimonials": serialize_list_rows(
            conn.execute("SELECT * FROM testimonials ORDER BY sort_order, author_name"),
            lambda row: {
                "id": row["id"],
                "authorName": row["author_name"],
                "authorRole": row["author_role"],
                "quote": row["quote"],
                "sortOrder": row["sort_order"],
            },
        ),
    }


def admin_payload(conn):
    payload = public_site_payload(conn)
    payload["messages"] = serialize_list_rows(
        conn.execute("SELECT * FROM contact_messages ORDER BY created_at DESC"),
        lambda row: {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "company": row["company"],
            "budget": row["budget"],
            "message": row["message"],
            "createdAt": row["created_at"],
        },
    )
    payload["summary"] = {
        "projects": conn.execute("SELECT COUNT(*) AS count FROM projects").fetchone()["count"],
        "experienceItems": conn.execute("SELECT COUNT(*) AS count FROM experiences").fetchone()["count"],
        "skills": conn.execute("SELECT COUNT(*) AS count FROM skills").fetchone()["count"],
        "testimonials": conn.execute("SELECT COUNT(*) AS count FROM testimonials").fetchone()["count"],
        "messages": conn.execute("SELECT COUNT(*) AS count FROM contact_messages").fetchone()["count"],
    }
    return payload


def parse_json_body(handler):
    length = int(handler.headers.get("Content-Length", "0") or "0")
    raw = handler.rfile.read(length) if length else b"{}"
    try:
        return json.loads(raw.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON payload.")


def get_cookies(handler):
    cookie = SimpleCookie()
    cookie.load(handler.headers.get("Cookie", ""))
    return cookie


def get_session(conn, handler):
    cookies = get_cookies(handler)
    session_cookie = cookies.get(SESSION_COOKIE)
    if not session_cookie:
        return None
    row = conn.execute(
        """
        SELECT users.*
        FROM sessions
        JOIN users ON users.id = sessions.user_id
        WHERE sessions.id = ?
        """,
        (session_cookie.value,),
    ).fetchone()
    return row


def require_auth(conn, handler):
    user = get_session(conn, handler)
    if not user:
        raise PermissionError("You need to sign in first.")
    return user


def require_admin(conn, handler):
    user = require_auth(conn, handler)
    if not user["is_admin"]:
        raise PermissionError("Admin access required.")
    return user


def get_or_create_csrf(handler):
    cookies = get_cookies(handler)
    token = cookies.get(CSRF_COOKIE)
    return token.value if token else secrets.token_urlsafe(24)


def set_cookie_headers(session_id=None, csrf_token=None, clear_session=False):
    headers = {}
    cookie_parts = []
    same_site = "SameSite=Lax"
    secure = "Secure" if SESSION_COOKIE_SECURE else None
    if session_id:
        session_cookie = [f"{SESSION_COOKIE}={session_id}", "HttpOnly", "Path=/", same_site]
        if secure:
            session_cookie.append(secure)
        cookie_parts.append("; ".join(session_cookie))
    if csrf_token:
        csrf_cookie = [f"{CSRF_COOKIE}={csrf_token}", "Path=/", same_site]
        if secure:
            csrf_cookie.append(secure)
        cookie_parts.append("; ".join(csrf_cookie))
    if clear_session:
        clearing = [f"{SESSION_COOKIE}=deleted", "Path=/", "Expires=Thu, 01 Jan 1970 00:00:00 GMT", same_site]
        if secure:
            clearing.append(secure)
        cookie_parts.append("; ".join(clearing))
    if cookie_parts:
        headers["Set-Cookie"] = cookie_parts
    return headers


def validate_csrf(handler):
    if handler.command in {"GET", "HEAD", "OPTIONS"}:
        return
    cookies = get_cookies(handler)
    csrf_cookie = cookies.get(CSRF_COOKIE)
    csrf_header = handler.headers.get("X-CSRF-Token", "")
    if not csrf_cookie or not csrf_header or not secrets.compare_digest(csrf_cookie.value, csrf_header):
        raise PermissionError("CSRF validation failed.")


def create_session(conn, user_id):
    session_id = secrets.token_urlsafe(32)
    conn.execute(
        "INSERT INTO sessions (id, user_id, created_at) VALUES (?, ?, ?)",
        (session_id, user_id, now_iso()),
    )
    return session_id


def upsert_site_settings(conn, payload):
    conn.execute(
        """
        UPDATE site_settings SET
          owner_name = ?, owner_role = ?, owner_location = ?, hero_title = ?, hero_intro = ?,
          hero_blurb = ?, about_title = ?, about_body = ?, primary_cta_label = ?, primary_cta_url = ?,
          secondary_cta_label = ?, secondary_cta_url = ?, email = ?, phone = ?, github_url = ?,
          linkedin_url = ?, twitter_url = ?, resume_url = ?, availability_label = ?, years_experience = ?,
          projects_completed = ?, happy_clients = ?
        WHERE id = 1
        """,
        (
            payload["ownerName"],
            payload["ownerRole"],
            payload["ownerLocation"],
            payload["heroTitle"],
            payload["heroIntro"],
            payload["heroBlurb"],
            payload["aboutTitle"],
            payload["aboutBody"],
            payload["primaryCtaLabel"],
            payload["primaryCtaUrl"],
            payload["secondaryCtaLabel"],
            payload["secondaryCtaUrl"],
            payload["email"],
            payload["phone"],
            payload["githubUrl"],
            payload["linkedinUrl"],
            payload["twitterUrl"],
            payload["resumeUrl"],
            payload["availabilityLabel"],
            int(payload["yearsExperience"]),
            int(payload["projectsCompleted"]),
            int(payload["happyClients"]),
        ),
    )


def replace_collection(conn, table_name, columns, items):
    conn.execute(f"DELETE FROM {table_name}")
    placeholders = ", ".join(["?"] * len(columns))
    column_sql = ", ".join(columns)
    values = []
    for item in items:
        row = []
        for column in columns:
            value = item.get(column)
            row.append(value)
        values.append(tuple(row))
    if values:
        conn.executemany(
            f"INSERT INTO {table_name} ({column_sql}) VALUES ({placeholders})",
            values,
        )


class PortfolioHandler(BaseHTTPRequestHandler):
    server_version = "PortfolioStudio/1.0"

    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def log_message(self, format, *args):
        return

    def write_json(self, status, payload, headers=None):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if headers:
            for key, value in headers.items():
                if isinstance(value, list):
                    for item in value:
                        self.send_header(key, item)
                else:
                    self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def serve_static(self, path):
        relative = "index.html" if path in {"/", ""} else path.lstrip("/")
        target = (STATIC_ROOT / relative).resolve()
        if not str(target).startswith(str(STATIC_ROOT.resolve())) or not target.exists() or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        body = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", STATIC_TYPES.get(target.suffix.lower(), "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_request(self, method):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if not path.startswith("/api/"):
                return self.serve_static(path)

            with DB_LOCK:
                conn = db_connection()
                try:
                    csrf_token = get_or_create_csrf(self)

                    if method == "GET" and path == "/api/public-site":
                        payload = public_site_payload(conn)
                        return self.write_json(HTTPStatus.OK, {**payload, "csrfToken": csrf_token}, set_cookie_headers(csrf_token=csrf_token))

                    if method == "GET" and path == "/api/health":
                        return self.write_json(
                            HTTPStatus.OK,
                            {"ok": True, "status": "healthy", "timestamp": now_iso()},
                            set_cookie_headers(csrf_token=csrf_token),
                        )

                    if method == "GET" and path == "/api/session":
                        user = get_session(conn, self)
                        response = {"user": row_to_user(user), "csrfToken": csrf_token}
                        if user and user["is_admin"]:
                            response["admin"] = admin_payload(conn)
                        return self.write_json(HTTPStatus.OK, response, set_cookie_headers(csrf_token=csrf_token))

                    if method == "POST" and path == "/api/register":
                        validate_csrf(self)
                        body = parse_json_body(self)
                        name = str(body.get("name", "")).strip()
                        email = str(body.get("email", "")).strip().lower()
                        password = str(body.get("password", ""))
                        if len(name) < 2:
                            raise ValueError("Name must be at least 2 characters.")
                        if "@" not in email:
                            raise ValueError("Enter a valid email.")
                        if len(password) < 8:
                            raise ValueError("Password must be at least 8 characters.")
                        existing = conn.execute("SELECT id FROM users WHERE lower(email) = lower(?)", (email,)).fetchone()
                        if existing:
                            raise ValueError("An account with that email already exists.")
                        is_first_user = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"] == 0
                        user_id = str(uuid.uuid4())
                        conn.execute(
                            "INSERT INTO users (id, name, email, password_hash, is_admin, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                            (user_id, name, email, hash_password(password), 1 if is_first_user else 0, now_iso()),
                        )
                        session_id = create_session(conn, user_id)
                        conn.commit()
                        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
                        return self.write_json(
                            HTTPStatus.CREATED,
                            {"user": row_to_user(user), "admin": admin_payload(conn) if user["is_admin"] else None, "csrfToken": csrf_token},
                            set_cookie_headers(session_id=session_id, csrf_token=csrf_token),
                        )

                    if method == "POST" and path == "/api/login":
                        validate_csrf(self)
                        body = parse_json_body(self)
                        email = str(body.get("email", "")).strip().lower()
                        password = str(body.get("password", ""))
                        user = conn.execute("SELECT * FROM users WHERE lower(email) = lower(?)", (email,)).fetchone()
                        if not user or not verify_password(password, user["password_hash"]):
                            raise ValueError("Invalid email or password.")
                        conn.execute("DELETE FROM sessions WHERE user_id = ?", (user["id"],))
                        session_id = create_session(conn, user["id"])
                        conn.commit()
                        return self.write_json(
                            HTTPStatus.OK,
                            {"user": row_to_user(user), "admin": admin_payload(conn) if user["is_admin"] else None, "csrfToken": csrf_token},
                            set_cookie_headers(session_id=session_id, csrf_token=csrf_token),
                        )

                    if method == "POST" and path == "/api/logout":
                        validate_csrf(self)
                        session_cookie = get_cookies(self).get(SESSION_COOKIE)
                        if session_cookie:
                            conn.execute("DELETE FROM sessions WHERE id = ?", (session_cookie.value,))
                            conn.commit()
                        return self.write_json(
                            HTTPStatus.OK,
                            {"ok": True, "csrfToken": csrf_token},
                            set_cookie_headers(csrf_token=csrf_token, clear_session=True),
                        )

                    if method == "POST" and path == "/api/contact":
                        validate_csrf(self)
                        body = parse_json_body(self)
                        name = str(body.get("name", "")).strip()
                        email = str(body.get("email", "")).strip()
                        company = str(body.get("company", "")).strip()
                        budget = str(body.get("budget", "")).strip()
                        message = str(body.get("message", "")).strip()
                        if len(name) < 2 or "@" not in email or len(message) < 12:
                            raise ValueError("Please fill out the contact form properly.")
                        conn.execute(
                            """
                            INSERT INTO contact_messages (id, name, email, company, budget, message, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            (str(uuid.uuid4()), name, email, company, budget, message, now_iso()),
                        )
                        conn.commit()
                        return self.write_json(HTTPStatus.CREATED, {"ok": True, "csrfToken": csrf_token}, set_cookie_headers(csrf_token=csrf_token))

                    if method == "GET" and path == "/api/admin/site":
                        require_admin(conn, self)
                        return self.write_json(
                            HTTPStatus.OK,
                            {**admin_payload(conn), "csrfToken": csrf_token},
                            set_cookie_headers(csrf_token=csrf_token),
                        )

                    if method == "POST" and path == "/api/admin/site":
                        require_admin(conn, self)
                        validate_csrf(self)
                        body = parse_json_body(self)
                        site = body.get("site") or {}
                        projects = body.get("projects") or []
                        experiences = body.get("experiences") or []
                        skills = body.get("skills") or []
                        testimonials = body.get("testimonials") or []
                        upsert_site_settings(conn, site)
                        replace_collection(
                            conn,
                            "projects",
                            ["id", "owner_id", "title", "category", "summary", "stack", "github_url", "live_url", "featured", "sort_order"],
                            [
                                {
                                    "id": item.get("id") or str(uuid.uuid4()),
                                    "owner_id": 1,
                                    "title": str(item.get("title", "")).strip(),
                                    "category": str(item.get("category", "")).strip(),
                                    "summary": str(item.get("summary", "")).strip(),
                                    "stack": str(item.get("stack", "")).strip(),
                                    "github_url": str(item.get("githubUrl", "")).strip(),
                                    "live_url": str(item.get("liveUrl", "")).strip(),
                                    "featured": 1 if item.get("featured") else 0,
                                    "sort_order": int(item.get("sortOrder", 0)),
                                }
                                for item in projects
                                if str(item.get("title", "")).strip()
                            ],
                        )
                        replace_collection(
                            conn,
                            "experiences",
                            ["id", "owner_id", "role", "company", "start_label", "end_label", "summary", "sort_order"],
                            [
                                {
                                    "id": item.get("id") or str(uuid.uuid4()),
                                    "owner_id": 1,
                                    "role": str(item.get("role", "")).strip(),
                                    "company": str(item.get("company", "")).strip(),
                                    "start_label": str(item.get("startLabel", "")).strip(),
                                    "end_label": str(item.get("endLabel", "")).strip(),
                                    "summary": str(item.get("summary", "")).strip(),
                                    "sort_order": int(item.get("sortOrder", 0)),
                                }
                                for item in experiences
                                if str(item.get("role", "")).strip()
                            ],
                        )
                        replace_collection(
                            conn,
                            "skills",
                            ["id", "owner_id", "label", "category", "sort_order"],
                            [
                                {
                                    "id": item.get("id") or str(uuid.uuid4()),
                                    "owner_id": 1,
                                    "label": str(item.get("label", "")).strip(),
                                    "category": str(item.get("category", "")).strip(),
                                    "sort_order": int(item.get("sortOrder", 0)),
                                }
                                for item in skills
                                if str(item.get("label", "")).strip()
                            ],
                        )
                        replace_collection(
                            conn,
                            "testimonials",
                            ["id", "owner_id", "author_name", "author_role", "quote", "sort_order"],
                            [
                                {
                                    "id": item.get("id") or str(uuid.uuid4()),
                                    "owner_id": 1,
                                    "author_name": str(item.get("authorName", "")).strip(),
                                    "author_role": str(item.get("authorRole", "")).strip(),
                                    "quote": str(item.get("quote", "")).strip(),
                                    "sort_order": int(item.get("sortOrder", 0)),
                                }
                                for item in testimonials
                                if str(item.get("authorName", "")).strip()
                            ],
                        )
                        conn.commit()
                        return self.write_json(
                            HTTPStatus.OK,
                            {**admin_payload(conn), "csrfToken": csrf_token},
                            set_cookie_headers(csrf_token=csrf_token),
                        )

                    if method == "POST" and path == "/api/admin/messages/delete":
                        require_admin(conn, self)
                        validate_csrf(self)
                        body = parse_json_body(self)
                        message_id = str(body.get("id", "")).strip()
                        if not message_id:
                            raise ValueError("Message id is required.")
                        conn.execute("DELETE FROM contact_messages WHERE id = ?", (message_id,))
                        conn.commit()
                        return self.write_json(
                            HTTPStatus.OK,
                            {**admin_payload(conn), "csrfToken": csrf_token},
                            set_cookie_headers(csrf_token=csrf_token),
                        )

                finally:
                    conn.close()

            self.send_error(HTTPStatus.NOT_FOUND)
        except PermissionError as error:
            self.write_json(HTTPStatus.FORBIDDEN, {"error": str(error), "csrfToken": get_or_create_csrf(self)}, set_cookie_headers(csrf_token=get_or_create_csrf(self)))
        except ValueError as error:
            self.write_json(HTTPStatus.BAD_REQUEST, {"error": str(error), "csrfToken": get_or_create_csrf(self)}, set_cookie_headers(csrf_token=get_or_create_csrf(self)))
        except Exception:
            self.write_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"error": "Something went wrong on the server.", "csrfToken": get_or_create_csrf(self)},
                set_cookie_headers(csrf_token=get_or_create_csrf(self)),
            )


def main():
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), PortfolioHandler)
    print(f"Portfolio Studio running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
