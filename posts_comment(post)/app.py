from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)
db = pymysql.connect(host="localhost", user="root", passwd="8947", db="posts_postid", charset="utf8")
cur = db.cursor()

@app.route('/posts/<int:postId>/comments', methods=('GET', 'POST'))
def create_post(postId):
    data = request.get_json()
    author = data.get('author')
    content = data.get('content')
    password = data.get('password')

    sql = "INSERT INTO comments (author, content, password, post_id) VALUES (%s, %s, %s, %s)"
    cur.execute(sql, (author, content, password, postId))
    db.commit()

    cur.execute("SELECT LAST_INSERT_ID()")
    commentId = cur.fetchone()[0]

    response_data = {"commentId": commentId}

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)