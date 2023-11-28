from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)
db = pymysql.connect(host="localhost", user="root", passwd="8947", db="posts_postid", charset="utf8")
cur = db.cursor()

@app.route('/posts/<int:post_id>', methods=('GET', 'DELETE'))
def delete_post(post_id):

    ## password 와 post_id를 받은 후 해당 게시글을 가져옵니다.
    password = int(request.args.get("password"))
    sql = "SELECT * FROM board WHERE id = %s"
    cur.execute(sql, (post_id))
    pos = cur.fetchone()

    ## 게시글이 있는 경우에 
    if pos:
        ## 비밀번호를 가져옵니다.
        pw_query = "SELECT password FROM board WHERE id = %s"
        cur.execute(pw_query, (post_id,))
        pww = cur.fetchone()

        ## 가져온 비밀번호와 password와 비교합니다.
        if pww and pww[0] == password:
            ## 맞을 경우에 comments부터 삭제를 합니다. 
            ## comments를 삭제하지 않으면 에러가 납니다.
            delete_comm = "DELETE FROM comments WHERE post_id = %s"
            cur. execute(delete_comm, (post_id,))
            db.commit()
            ## 게시글을 삭제합니다.
            delete_query = "DELETE FROM board WHERE id = %s"
            cur.execute(delete_query, (post_id,))
            db.commit()
            response = {"ok": "true"}
            return jsonify(response)
        else:
            response = {"ok": "false password"}
            return jsonify(response)
    else:
        response = {"ok": "false id"}
        return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
