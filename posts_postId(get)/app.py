from flask import Flask, request, jsonify, redirect, url_for
import pymysql

app = Flask(__name__)
db = pymysql.connect(host="localhost", user="root", passwd="", db="posts_postid", charset="utf8")
cur = db.cursor()

@app.route('/posts/<int:postId>', methods=['GET'])
def get_post(postId):
    
    ## id 가 postId 인 게시글을 가져옵니다.
    sql = "SELECT * FROM board WHERE id = %s"
    cur.execute(sql, (postId,))
    post = cur.fetchone()


    if post:    ## 게시글이 있을때

        ## post_id 가 postId 인 모든 댓글을 가져옵니다.
        sql = "SELECT * FROM comments WHERE post_id = %s"
        cur.execute(sql, (postId,))
        comments = cur.fetchall()

        comment_list = [] # comment 값 저장
        ## 댓글이 존재하는지 확인합니다.
        if comments:
            ## comments에 있는 모든 댓글들을 json 형태로 comment_list 안에 저장합니다.
            for comment in comments:
                comment_data = {
                    "id": comment[0],
                    "author": comment[1],
                    "content": comment[2],
                    "uploadedAt": comment[3].strftime("%Y-%m-%dT%H:%M:%S.%fZ") if comment[3] else None
                }
                comment_list.append(comment_data)
        else:
            comment_list.append("No comments")

        ## comment_list와 post의 내용을 토대로 최종 response_data를 작성합니다.
        response_data = {
            "post": {'id': post[0], 
                    'title': post[1], 
                    'author': post[2], 
                    'content': post[3], 
                    'comments': comment_list, 
                    'uploadedAt': post[5].strftime("%Y-%m-%dT%H:%M:%S.%fZ") if post[5] else None
                    }
        }
        return jsonify(response_data)
    
    else:   ## 게시글이 없을경우 /posts로 전환해줍니다.
        return redirect(url_for('posts'))

if __name__ == '__main__':
    app.run(debug=True)
