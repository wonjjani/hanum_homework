from flask import Flask, request, jsonify, redirect, url_for
import pymysql
import math
import os

app = Flask(__name__)

## DATA BASE를 불러와줍니다.
db = pymysql.connect(host="localhost", user="root", passwd="8947", db="posts_postid", charset="utf8")
cur = db.cursor()


######### GET  /posts
######### 모든 게시글을 가져옵니다. 

## method = GET
@app.route('/posts', methods=['GET'])
def posts():
    ## limit, page 값을 받아옵니다.
    limit = request.args.get("limit", default=10, type=int)
    page = request.args.get("page", default=1, type=int)
    
    ## board 안에 있는 모든 데이터를 가져옵니다.
    sql_count = "SELECT COUNT(*) FROM board"
    cur.execute(sql_count)
    data_count = cur.fetchall()

    ## board 에서 최신 게시물을 내림차순으로 정렬 한 후, LIMIT 만큼 가져오고, 지정한 OFFSET가져옵니다.
    sql = "SELECT * FROM board ORDER BY uploadAt DESC LIMIT %s OFFSET %s;"

    ## 첫번째 %s 에는 limit, 두번째 %s 에는 (page -1) * limit 를 넣은 후, 쿼리문을 실행합니다.
    ### (page - 1) * limit 는 offset 값으로 페이지당 표시되는 항목의 수를 곱한 값입니다.
    cur.execute(sql, (limit, (page - 1) * limit))
    data_list = cur.fetchall()
    
    # 데이터의 총 개수를 페이지당 표시되는 항목의 수로 나누어서 전체 페이지의 수를 계산합니다.
    page_count = math.ceil(data_count[0][0] / limit)

    ## 기본 response 값입니다.
    response_data = {
        "pageCount": page_count,
        "posts": []
        }
    
    ## 현재 페이지가 전체 페이지를 넘어갈 경우 error 를 반환합니다.
    if page <= page_count:
        for row in data_list:
            
            ## 댓글의 수를 불러옵니다. 
            sql_comment = "SELECT COUNT(*) FROM comments WHERE post_id = %s"
            cur.execute(sql_comment, (row[0], ))
            comment_count = cur.fetchone()[0]

            ## post response 입니다.
            post_data = {
                'title': row[1], 
                'id': row[0], 
                'author': row[2], 
                'comments': comment_count, 
                'uploadAt': row[5].strftime("%Y-%m-%dT%H:%M:%S.%fZ") if row[5] else None
            }

            ## post_data 의 값을 response_data 의 posts 로 전달합니다.
            response_data["posts"].append(post_data)
    else:
        ## page가 page_count 를 넘어갈 경우 반환합니다.
        response_data = {
            "error": "No posts"
        }
    return jsonify(response_data)


######### GET  /posts/{postId}
######### 게시글 내용을 가져옵니다.

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
    
######### POST  /posts
######### 게시글을 올립니다. 

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

######### POST  /posts/{postId}/comments
######### 댓글을 올립니다.

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

######### DELETE  /posts/{postId}
######### 게시글을 지웁니다.
###### GET /posts와 중복되어 작동이 안되므로 /posts/{postId}를 /delposts/{postId}로 수정하였습니다.
###### 원본 파일을 보시면 /posts/ 로 되어있습니다.
@app.route('/delposts/<int:post_id>', methods=('GET', 'DELETE'))
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
    
######### DELETE  /posts/{postId}/comments/{commentId}
######### 댓글을 지웁니다.
##### 해당 코드도 posts와 중복되오니 /delposts/ 로 수정하겠습니다.
@app.route('/delposts/<int:post_id>/comments/<int:comment_id>', methods=('GET', 'DELETE'))
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


## 코드에 변화가 있을 경우 디버깅 합니다.
if __name__ == '__main__':
    app.run(debug=True)
