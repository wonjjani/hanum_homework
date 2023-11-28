from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)
db = pymysql.connect(host="localhost", user="root", passwd="8947", db="posts_postid", charset="utf8")
cur = db.cursor()

@app.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')
    content = data.get('content')
    password = data.get('password')

    sql = "INSERT INTO board (title, author, content, password) VALUES (%s, %s, %s, %s)"
    cur.execute(sql, (title, author, content, password))
    db.commit()

    cur.execute("SELECT LAST_INSERT_ID()")
    postId = cur.fetchone()[0]

    response_data = {"postId": postId}

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)