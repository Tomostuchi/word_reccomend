import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)
DB_NAME = "database.db"

# -------------------------------------------------
# データベース初期設定
# -------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            origin INTEGER, count INTEGER, article INTEGER, 
            group_score INTEGER, listening INTEGER, idiom INTEGER,
            now_level INTEGER, goal_level INTEGER
        )
    ''')
    cursor.execute('SELECT count(*) FROM book_scores')
    if cursor.fetchone()[0] == 0:
        # データ登録（数値が小さいほどその要素が強い/優秀）
        data = [
            ('システム英単語', 3, 2, 8, 3, 7, 7, 2, 3),
            ('システム英単語Basic', 4, 5, 5, 7, 6, 3, 1, 1),
            ('鉄壁', 2, 1, 9, 1, 8, 9, 3, 3),
            ('ターゲット1900', 5, 4, 6, 8, 5, 2, 1, 2),
            ('LEAP', 1, 3, 7, 2, 9, 8, 2, 3),
            ('速読英単語', 6, 9, 1, 9, 4, 1, 2, 2),
            ('DUO', 7, 8, 2, 4, 3, 6, 2, 2),
            ('ユメタン', 8, 6, 4, 5, 2, 5, 1, 1),
            ('キクタン', 9, 7, 3, 6, 1, 4, 1, 1)
        ]
        cursor.executemany('INSERT INTO book_scores (name, origin, count, article, group_score, listening, idiom, now_level, goal_level) VALUES (?,?,?,?,?,?,?,?,?)', data)
        conn.commit()
    conn.close()

init_db()

# -------------------------------------------------
# ルーティング
# -------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

# (前略... importなどはそのまま)

@app.route('/result')
def result():
    # -----------------------------------------------------------
    # 1. ユーザー入力の取得（省略：変更なし）
    # -----------------------------------------------------------
    try:
        user_ranks = {
            'origin': int(request.args.get('origin_rank', 6)),
            'count': int(request.args.get('count_rank', 6)),
            'article': int(request.args.get('article_rank', 6)),
            'group_score': int(request.args.get('group_rank', 6)),
            'listening': int(request.args.get('listening_rank', 6)),
            'idiom': int(request.args.get('idiom_rank', 6))
        }
    except ValueError:
        return "エラー: 全ての項目を選択してください。"

    level_map = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
    raw_current = request.args.get('current_level', 'beginner')
    raw_target = request.args.get('target_level', 'advanced')
    user_now = level_map.get(raw_current, 1)
    user_goal = level_map.get(raw_target, 3)

    # -----------------------------------------------------------
    # 2. 計算ロジック（省略：変更なし）
    # -----------------------------------------------------------
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM book_scores")
    books = cursor.fetchall()
    conn.close()

    best_book_name = "該当なし"
    min_score = float('inf')
    debug_log = []

    for book in books:
        # ... (計算部分は変更なしなので省略します) ...
        # ... 既存の計算コード ...
        
        # ※省略していますが、ここの計算ループは元のまま残してください
        score = 0
        score += user_ranks['origin'] * book['origin']
        score += user_ranks['count'] * book['count']
        score += user_ranks['article'] * book['article']
        score += user_ranks['group_score'] * book['group_score']
        score += user_ranks['listening'] * book['listening']
        score += user_ranks['idiom'] * book['idiom']

        level_match = True
        if book['now_level'] > user_now + 1: level_match = False
        if book['goal_level'] < user_goal: level_match = False

        status = ""
        if not level_match:
            score += 1000
            status = "(レベル不一致)"

        debug_log.append(f"{book['name']}: {score}点 {status}")

        if score < min_score:
            min_score = score
            best_book_name = book['name']
    
    # -----------------------------------------------------------
    # 【追加】画像ファイル名の紐付け
    # -----------------------------------------------------------
    # ここに保存した実際のファイル名を書いてください
    image_map = {
        'システム英単語': 'sisutan.jpg',
        'システム英単語Basic': 'sisutan_basic.jpg',
        '鉄壁': 'teppeki.jpg',
        'ターゲット1900': 'target1900.jpg',
        'LEAP': 'leap.jpg',
        '速読英単語': 'sokutan.jpg',
        'DUO': 'duo.jpg',
        'ユメタン': 'yumetan.jpg',
        'キクタン': 'kikutan.jpg'
    }
    # テスト：どの本が選ばれても強制的に duo.jpg を出す
    image_file = 'sokutan.jpg'

    # 辞書からファイル名を取得（もし登録がなければ no_image.png にする）
    #image_file = image_map.get(best_book_name, 'no_image.png')

    return render_template('result.html', 
                           book=best_book_name, 
                           book_image=image_file,  # ← 画像ファイル名をHTMLに渡す
                           user_level=f"現在:{raw_current} / 目標:{raw_target}",
                           log=debug_log)

if __name__ == '__main__':
    app.run(debug=True)