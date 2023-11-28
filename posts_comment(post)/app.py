from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)
db = pymysql.connect(host="localhost", user="root", passwd="8947", db="posts_postid", charset="utf8")
cur = db.cursor()

@app.route('/posts/<int:postId>/comments', methods=('GET', 'POST'))
def create_comment(postId):

    ## JSON 형태로 author, content, password 를 받습니다.
    data = request.get_json()
    author = data.get('author')
    content = data.get('content')
    password = data.get('password')

    ## 받은 데이터로 게시글의 댓글을 올립니다.
    ### postId는 게시글의 id로 중복이 가능합니다. 1개의 게시글에 여러수의 댓글이 달릴수 있으며, 해당 댓글이 어느 게시글에 있는지 알려줍니다.
    sql = "INSERT INTO comments (author, content, password, post_id) VALUES (%s, %s, %s, %s)"
    cur.execute(sql, (author, content, password, postId))
    db.commit()

    ## 삽입한 댓글의 id를 가져옵니다.
    cur.execute("SELECT LAST_INSERT_ID()")
    commentId = cur.fetchone()[0]

    ## comment_id를 반환합니다.
    response_data = {"commentId": commentId}

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)