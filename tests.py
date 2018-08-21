#!usr/bin/env python
# -*- coding:utf-8 -*-
import unittest
from MyInstagram import app


class MyInstagramTest(unittest.TestCase):
    def setUp(self):
        print('setUp')
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        print('tearDown')

    def register(self, username, password):
        return self.app.post('/reg/', data={'username': username, 'password': password}, follow_redirects=True)

    def login(self, username, password):
        return self.app.post('/login/', data={'username': username, 'password': password}, follow_redirects=True)

    def logout(self):
        return self.app.get('/logout/')

    def test_reg_logout_login(self):
        assert self.register('hello', 'world').status_code ==200
        assert '-hello' in str(self.app.open('/').data)
        self.logout()
        assert '-hello' not in str(self.app.open('/').data)
        self.login('hello', 'world')
        assert '-hello' in str(self.app.open('/').data)

    def test_profile(self):
        r = self.app.get('/profile/3/', follow_redirects=True)
        assert r.status_code == 200
        assert 'password' in str(r.data)
        self.register('hello2', 'world')
        assert 'hello2' in str(self.app.open('/profile/1/', follow_redirects=True).data)
