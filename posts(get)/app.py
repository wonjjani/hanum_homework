from flask import Flask, request, jsonify
import pymysql
import math

app = Flask(__name__)
db = pymysql.connect(host="localhost", user="root", passwd="8947", db="post1", charset="utf8")

cur = db.cursor()

@app.route('/posts', methods=['GET'])
def posts():
    limit = request.args.get("limit", default=10, type=int)
    page = request.args.get("page", default=1, type=int)
    
    sql_count = "SELECT COUNT(*) FROM board"
    cur.execute(sql_count)
    data_count = cur.fetchall()

    sql = "SELECT * FROM board ORDER BY uploadAt DESC LIMIT %s OFFSET %s;"
    cur.execute(sql, (limit, (page - 1) * limit))

    data_list = cur.fetchall()
    
    page_count = math.ceil(data_count[0][0] / limit)
    

    response_data = {
        "pageCount": page_count,
        "posts": [{'title': row[1], 
                   'id': row[0], 
                   'author': row[2], 
                   'comments': row[3], 
                   'uploadAt': row[4]
                   } for row in data_list]
    }
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
