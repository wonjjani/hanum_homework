from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)
db = pymysql.connect(host="localhost", user="root", passwd="8947", db="posts_postid", charset="utf8")
cur = db.cursor()

@app.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=('GET', 'DELETE'))
def delete_comment(post_id, comment_id):

    ## password 와 post_id, comment_id를 받은 후 게시글을 가져옵니다.
    password = int(request.args.get("password"))
    sql = "SELECT * FROM comments WHERE post_id = %s"
    cur.execute(sql, (post_id,))
    comms = cur.fetchall()

    ## 댓글이 있을 경우
    if comms:
        
        ## 해당 댓글의 password를 가져옵니다.
        com_sql = "SELECT password FROM comments WHERE post_id = %s and id = %s"
        cur.execute(com_sql, (post_id, comment_id))
        com_pass = cur.fetchone()

        ## password가 일치할 경우에 
        if com_pass and com_pass[0] == password:

            ## 해당 댓글을 삭제합니다.
            dele_sql = "DELETE FROM comments WHERE id = %s"
            cur.execute(dele_sql, (comment_id))
            db.commit()
            response = {"ok": "true"}
            return jsonify(response)
    else:
        pass
    return jsonify({"ok": "false"})
    


if __name__ == '__main__':
    app.run(debug=True)
