from flask import Flask, request, jsonify
import pymysql
import math

app = Flask(__name__)
db = pymysql.connect(host="localhost", user="root", passwd="8947", db="post1", charset="utf8")

cur = db.cursor()

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


if __name__ == '__main__':
    app.run(debug=True)
