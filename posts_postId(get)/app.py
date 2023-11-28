from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)
db = pymysql.connect(host="localhost", user="root", passwd="8947", db="posts_postid", charset="utf8")
cur = db.cursor()

@app.route('/posts/<int:postId>', methods=['GET'])
def get_post(postId):
    

    sql = "SELECT * FROM board WHERE id = %s"
    cur.execute(sql, (postId,))
    post = cur.fetchone()

    sql = "SELECT * FROM comments WHERE post_id = %s"
    cur.execute(sql, (postId,))
    comments = cur.fetchall()

    
    comment_list = []
    for comment in comments:
        comment_data = {
            "id": comment[0],
            "author": comment[1],
            "content": comment[2],
            "uploadedAt": comment[3].strftime("%Y-%m-%d %H:%M:%S") if comment[3] else None
        }
        comment_list.append(comment_data)

    response_data = {
        "post": {'id': post[0], 
                  'title': post[1], 
                  'author': post[2], 
                  'content': post[3], 
                  'comments': comment_list, 
                  'uploadedAt': post[5].strftime("%Y-%m-%d %H:%M:%S") if post[5] else None
                  }
    }

    if post:
        return jsonify(response_data)
    else:
        return jsonify({"message": "게시물을 찾을 수 없습니다."}), 404

if __name__ == '__main__':
    app.run(debug=True)
