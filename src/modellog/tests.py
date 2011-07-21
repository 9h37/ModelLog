# -*- coding: utf-8 -*-
from django.test import TestCase
from models import ModelLog
from datetime import datetime, timedelta
from socket import gethostname
from hashlib import sha256
import unittest
import settings
import logging
import json
from random import randint
import os

class ModelLogTestCase(TestCase):

    __LOG_FILE = 'test_log_file'

    def __assert_logfile(self, event_id, event_action_code, user_id, instance_id):
        f = open(self.__LOG_FILE, 'r')
        file_lines = f.readlines()
        log = json.loads(file_lines[len(file_lines) - 1])
        try:
            log['event_id']             #5.1.1. Event ID                        required
            log['event_action_code']    #5.1.2. Event Action Code,              optional
            log['event_date']           #5.1.3. Event Date/Time                 required
            log['event_outcome']        #5.1.4. Event Outcome Indicator         required
            log['user_id']              #5.2.1. User ID                         required
            log['access_point_ip']      #5.3.2. Network Access Point ID         optional
            log['source_id']            #5.4.2. Audit Source ID                 required
            log['instance_id_type']     #5.5.4. Participant Object ID Type Code required
            log['instance_id']          #5.5.6. Participant Object ID           required
        except Exception as e:
            raise e #One of the required keys (see above) is missing
        log_keys = log.keys()
        log_keys.sort()
        log_hash = sha256(settings.SECRET_KEY)
        for key in log_keys:
            if key != 'signature':
                log_hash.update(str(log[key]))
        self.assertEqual(log['event_id'], event_id)
        self.assertEqual(log['event_action_code'], event_action_code)
        self.assertEqual(log['event_outcome'], 0)
        self.assertEqual(log['user_id'], user_id)
        self.assertEqual(log['source_id'], gethostname())
        self.assertEqual(log['instance_id_type'], -1)
        self.assertEqual(log['instance_id'], instance_id)
        self.assertEqual(log['signature'], log_hash.hexdigest())
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
        event_id = randint(1, 100)
        user_id = randint(1, 100)
        p.save(event_id, user_id)
        self.__assert_logfile(event_id, 'C', user_id, p.id)

    def test_update(self):
        p = ModelLog()
        event_id = randint(1, 100)
        user_id = randint(1, 100)
        p.save(event_id, user_id)
        p.save(event_id, user_id)
        self.__assert_logfile(event_id, 'U', user_id, p.id)

    def test_delete(self):
        p = ModelLog()
        event_id = randint(1, 100)
        user_id = randint(1, 100)
        p.save(event_id, user_id)
        instance_id = p.id
        p.delete(event_id, user_id)
        self.__assert_logfile(event_id, 'D', user_id, instance_id)
