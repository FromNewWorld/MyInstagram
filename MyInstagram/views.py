#!usr/bin/env python
# -*- coding:utf-8 -*-

from MyInstagram import app, db
from MyInstagram.models import Image, User, Comment
from flask import render_template, redirect, request, flash, get_flashed_messages, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
import random
import hashlib
import json
import uuid
import os
# from MyInstagram.qiniusdk import qiniu_upload_file



@app.route('/')
def index():
    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=1, per_page=10)
    return render_template('index.html', images=paginate.items, has_next=paginate.has_next)


@app.route('/index/<int:page>/<int:per_page>/')
def index_images(page, per_page):
    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=page, per_page=per_page, error_out=False)
    map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        comments = []
        for comment in image.comments:
            comments.append({'comment_uid': comment.user.id, 'comment_username': comment.user.username})
        imgvo = {'id': image.id, 'url': image.url, 'comment_count': len(image.comments), 'uid': image.user.id,
                 'username': image.user.username, 'user_head': image.user.head_url, 'time': image.created_time,
                 'comments': comments}
        images.append(imgvo)
    map['images'] = images
    return json.dumps(map)


@app.route('/image/<int:image_id>/')
def image(image_id):
    image = Image.query.get(image_id)
    if image == None:
        return redirect('/')
    else:
        return render_template('pageDetail.html', image=image)


@app.route('/profile/<int:user_id>/')
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    if user == None:
        return redirect('/')
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=1, per_page=3)
    return render_template('profile.html', user=user, has_next=paginate.has_next, images=paginate.items)


@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id, page, per_page):
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page)
    map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        imgvo = {'id': image.id, 'url': image.url, 'comment_count': len(image.comments)}
        images.append(imgvo)
    map['images'] = images
    return json.dumps(map)


def redirect_with_msg(target, msg, category):
    if msg != None:
        flash(msg, category=category)
    return redirect(target)


@app.route('/regloginpage/')
def reglogin(msg=''):
    if current_user.is_authenticated:
        return redirect('/')

    for m in get_flashed_messages(with_categories=False, category_filter=['registerfailed', 'loginfailed']):
        msg = msg + m
    return render_template('login.html', msg=msg, next=request.values.get('next'))

@app.route('/reg/', methods={'get', 'post'})
def reg():
    # 获取到提交的用户名和密码
    # args： url里的
    # form: body里的
    # values: 全部
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    # 校验
    user = User.query.filter_by(username=username).first()
    if user!=None:
        return redirect_with_msg('/regloginpage/', u'用户名已经存在！', 'registerfailed')
    if username == '' or password == '':
        return redirect_with_msg('/regloginpage/', u'用户名或密码不能为空！', 'registerfailed')

    salt = '.'.join(random.sample('0123456789abcdefghijklmnopqrstuvwxyz', 10))
    m = hashlib.md5()
    m.update((password+salt).encode('utf-8'))
    password = m.hexdigest()
    user = User(username, password, salt)
    db.session.add(user)
    db.session.commit()
    login_user(user)

    return redirect('/')


@app.route('/login/', methods={'get', 'post'})
def login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    # 检验
    if username == '' or password == '':
        return redirect_with_msg('/regloginpage/', u'用户名和密码不能为空！', 'loginfailed')

    user = User.query.filter_by(username=username).first()
    if user == None:
        return redirect_with_msg('/regloginpage/', u'用户名不存在！', 'loginfailed')

    m = hashlib.md5()
    m.update((password+user.salt).encode('utf-8'))
    if m.hexdigest() != user.password:
        return redirect_with_msg('/regloginpage', u'用户名或密码不正确！', 'loginfailed')

    login_user(user)
    next = request.values.get('next')
    if next != None and next.startswith('/') > 0:
        return redirect(next)
    return redirect('/')


@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')


def save_to_local(file, file_name):
    save_dir = app.config['UPLOAD_DIR']
    file.save(os.path.join(save_dir, file_name))
    return '/image/' + file_name


@app.route('/image/<image_name>/')
def view_image(image_name):
    return send_from_directory(app.config['UPLOAD_DIR'], image_name)


@app.route('/upload/', methods=['Post'])
def upload():
    file = request.files['file']

    file_ext = ''
    if file.filename.find('.') > 0:
        file_ext = file.filename.rsplit('.', 1)[1].strip().lower()
    if file_ext in app.config['ALLOWED_EXT']:
        file_name = str(uuid.uuid1()).replace('-', '') + '.' + file_ext
        url = save_to_local(file, file_name)
        # url = qiniu_upload_file(file, file_name)
        if url != None:
            db.session.add(Image(url, current_user.id))
            db.session.commit()

    return redirect('/profile/%d' % current_user.id)


@app.route('/addcomment/', methods=['POST'])
@login_required
def add_comment():
    image_id = int(request.values['image_id'])
    content = request.values['content']
    comment = Comment(content, image_id, current_user.id)
    db.session.add(comment)
    db.session.commit()
    return json.dumps({"code": 0, "id":comment.id,
                       "content": comment.content,
                       "username": comment.user.username,
                       "user_id": comment.user_id})
