from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)
db = pymysql.connect(host="localhost", user="root", passwd="8947", db="posts_postid", charset="utf8")
cur = db.cursor()

@app.route('/posts', methods=['POST'])
def posts_post():

    ## JSON 형태로 title, author, content, password 를 받습니다.
    data = request.get_json()

    title = data.get('title')
    author = data.get('author')
    content = data.get('content')
    password = data.get('password')

    ## 게시글을 올립니다. password 는 int로 저장합니다. (password로 저장해도 괜찮습니다.)
    sql = "INSERT INTO board (title, author, content, password) VALUES (%s, %s, %s, %s)"
    cur.execute(sql, (title, author, content, password))
    db.commit()

    ## 삽입한 게시글의 ID를 가져옵니다.
    cur.execute("SELECT LAST_INSERT_ID()")
    postId = cur.fetchone()[0]

    ## postId를 반환합니다. 
    response_data = {"postId": postId}

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)