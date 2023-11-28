from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)
db = pymysql.connect(host="localhost", user="root", passwd="8947", db="posts_postid", charset="utf8")
cur = db.cursor()

@app.route('/posts/<int:post_id>', methods=('GET', 'DELETE'))
def delete_post(post_id):

    password = int(request.args.get("password"))
    sql = "SELECT * FROM board WHERE id = %s"
    pos = cur.fetchone()

    if pos:
        pw_query = "SELECT password FROM board WHERE id = %s"
        cur.execute(pw_query, (post_id,))
        pww = cur.fetchone()

        if pww and pww[0] == password:
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
