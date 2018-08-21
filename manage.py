#!usr/bin/env python
# -*- coding:utf-8 -*-

from MyInstagram import app, db
from flask_script import Manager
from MyInstagram.models import User, Image, Comment
import random
import unittest

manager = Manager(app)


def get_image_url():
    return 'http://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 'm.png'


@manager.command
def init_database():
    # db.drop_all()
    # db.create_all()
    # # db.session.add(User('user1', 'name1'))
    #
    # for i in range(0, 100):
    #     db.session.add(User('User'+str(i), 'a'+str(i)))
    #     for j in range(0, 3):
    #         db.session.add(Image(get_image_url(), i+1))
    #         for k in range(0, 3):
    #             db.session.add(Comment('This is comment'+str(k), 3*i+j+1, i+1))
    # db.session.commit()
    #
    # u = User.query.get(1)
    # print(1, u)
    # print(2, u.images.all())
    # print(3, Image.query.get(2).user)

    user = User.query.filter_by(username='xx').first()
    for i in range(0, 10):
        db.session.add(Image(get_image_url(), user.id))
    db.session.commit()


@manager.command
def run_test():
    db.drop_all()
    db.create_all()
    test = unittest.TestLoader().discover('./')
    unittest.TextTestRunner().run(test)




if __name__ == '__main__':
    manager.run()
