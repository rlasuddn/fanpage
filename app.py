import hashlib
import os
import certifi
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from pymongo import MongoClient

ca = certifi.where()

client = MongoClient("mongodb+srv://test:sparta@cluster0.zkful.mongodb.net/Cluster0?retryWrites=true&w=majority",
                     tlsCAfile=ca)
db = client.test

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/main/join')
def join_view():
    return render_template('join.html')


@app.route('/join', methods=['POST'])
def join():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nick_receive = request.form['nick_give']
    result = db.user.find_one({'id': id_receive})

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    pw_result = db.user.find_one({'pw': pw_hash})

    if result is not None:
        return jsonify({'result': 'id_fail', 'msg': '아이디를 확인해주세요.'})

    elif pw_result is not None:
        return jsonify({'result': 'pw_fail', 'msg': '비밀번호를 확인해주세요'})

    elif result is None:
        db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nickname': nick_receive})
        return jsonify({'result': 'success', 'msg': '회원가입이 완료되었습니다'})


@app.route('/main/login')
def login_view():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})
    username = result['nickname']

    if result is not None:
        session['username'] = username
        return jsonify({'result': 'success', 'session': session['username']})
    elif result is None:
        return jsonify({'result': 'fail', 'msg': '로그인실패!'})


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return jsonify({'result': 'success'})


@app.route('/index')
def index():
    nickname = db.user.find_one({'nickname': session['username']})
    username = nickname['nickname']
    return render_template('login_home.html', nickname=username)


@app.route("/homework", methods=["POST"])
def homework_post():
    nickname_receive = request.form['nickname_give']
    comment_receive = request.form['comment_give']

    string = ''

    if nickname_receive or comment_receive is not string:
        doc = {
            'nickname': nickname_receive,
            'comment': comment_receive
        }
        db.fanpage.insert_one(doc)
        return jsonify({'msg': '저장완료'})
    else:
        return jsonify({'msg': '입력해주세요'})


@app.route("/homework", methods=["GET"])
def homework_get():
    fan_list = list(db.fanpage.find({}, {'_id': False}))

    return jsonify({'fan_comment': fan_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
