import os
import sqlite3
from flask import Flask, render_template

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'ranking.db')


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_column(conn, column_name, definition):
    columns = conn.execute('PRAGMA table_info(rankings)').fetchall()
    existing_columns = [column['name'] for column in columns]
    if column_name not in existing_columns:
        conn.execute(f'ALTER TABLE rankings ADD COLUMN {column_name} {definition}')


def init_db():
    conn = get_db_connection()
    conn.execute(
        '''
        CREATE TABLE IF NOT EXISTS rankings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            affiliation TEXT DEFAULT '',
            career TEXT DEFAULT '',
            incident TEXT DEFAULT '',
            photo TEXT DEFAULT '',
            status INTEGER NOT NULL UNIQUE CHECK(status IN (1, 2, 3))
        )
        '''
    )

    ensure_column(conn, 'affiliation', "TEXT DEFAULT ''")
    ensure_column(conn, 'career', "TEXT DEFAULT ''")
    ensure_column(conn, 'incident', "TEXT DEFAULT ''")
    ensure_column(conn, 'photo', "TEXT DEFAULT ''")

    existing_count = conn.execute('SELECT COUNT(*) FROM rankings').fetchone()[0]

    if existing_count == 0:
        demo_rows = [
            ('1등 예시', '예시 소속', '예시 경력', '대표 사건 예시', 'profile1.jpg', 1),
            ('2등 예시', '예시 소속', '예시 경력', '대표 사건 예시', 'profile2.jpg', 2),
            ('3등 예시', '예시 소속', '예시 경력', '대표 사건 예시', 'profile3.jpg', 3),
        ]
        conn.executemany(
            '''
            INSERT INTO rankings (name, affiliation, career, incident, photo, status)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            demo_rows,
        )

    conn.commit()
    conn.close()


@app.route('/')
def index():
    conn = get_db_connection()
    rows = conn.execute(
        '''
        SELECT name, affiliation, career, incident, photo, status
        FROM rankings
        WHERE status IN (1, 2, 3)
        ORDER BY status ASC
        '''
    ).fetchall()
    conn.close()

    ranking_map = {
        1: {
            'name': '1등 데이터 없음',
            'affiliation': '소속 없음',
            'career': '경력 없음',
            'incident': '대표 사건 없음',
            'photo': '',
        },
        2: {
            'name': '2등 데이터 없음',
            'affiliation': '소속 없음',
            'career': '경력 없음',
            'incident': '대표 사건 없음',
            'photo': '',
        },
        3: {
            'name': '3등 데이터 없음',
            'affiliation': '소속 없음',
            'career': '경력 없음',
            'incident': '대표 사건 없음',
            'photo': '',
        },
    }

    for row in rows:
        ranking_map[row['status']] = {
            'name': row['name'],
            'affiliation': row['affiliation'],
            'career': row['career'],
            'incident': row['incident'],
            'photo': row['photo'],
        }

    return render_template(
        'index.html',
        first=ranking_map[1],
        second=ranking_map[2],
        third=ranking_map[3],
    )


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
else:
    init_db()
