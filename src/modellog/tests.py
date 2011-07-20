# -*- coding: utf-8 -*-
from django.test import TestCase
from models import ModelLog
from datetime import datetime, timedelta
from socket import gethostname
from hashlib import sha256
import unittest
import settings
import logging
import os

class ModelLogTestCase(TestCase):

    __LOG_FILE = 'test_log_file'

    def __assert_logfile(self, action, model):
        current_datetime = datetime.now()
        current_datetime -= timedelta(microseconds=current_datetime.microsecond)
        log = {
            'date':current_datetime.isoformat(' '),
            'host':gethostname(),
            'ip':'[warning:unknown]',
            'type':type(model),
            'id':model.id,
            'action':action,
            'secret':settings.SECRET_KEY,
        }
        log_data_format = '%(date)s %(host)s %(ip)s %(type)s %(id)s %(action)s'
        log['hash'] = sha256((log_data_format + ' $(secret)s') % log).hexdigest()
        f = open(self.__LOG_FILE, 'r')
        file_lines = f.readlines()
        self.assertEqual((log_data_format + ' %(hash)s') % log + '\n', file_lines[len(file_lines) - 1])
        f.close()

    def __rm_logfile(self):
        try:
            os.remove(self.__LOG_FILE)
        except:
            pass

    def setUp(self):
        settings.logger.addHandler(logging.FileHandler(self.__LOG_FILE))

    def tearDown(self):
        self.__rm_logfile()

    def test_create(self):
        p = ModelLog()
        p.save()
        self.__assert_logfile('C', p)

    def test_update(self):
        p = ModelLog()
        p.save()
        p.save()
        self.__assert_logfile('U', p)

    def test_delete(self):
        p = ModelLog()
        p.save()
        p.delete()
        self.__assert_logfile('D', p)
