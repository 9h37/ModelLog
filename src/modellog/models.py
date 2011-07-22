# -*- coding: utf-8 -*-
from django.db import models
from django.http import HttpRequest
from django.conf import settings
from datetime import datetime, tzinfo
from socket import gethostname
from at_log import at_log

class ModelLog(models.Model):

    #RFC3881: http://www.faqs.org/rfcs/rfc3881.html

    LOG_ACTION_CREATE   = 'C'
    LOG_ACTION_READ     = 'R'
    LOG_ACTION_UPDATE   = 'U'
    LOG_ACTION_DELETE   = 'D'
    LOG_ACTION_EXECUTE  = 'E'

    LOG_OUTCOME_SUCCESS = 0
    LOG_OUTCOME_ERROR   = 12

    def __unicode__(self):
        return str(self.id)

    def __log_data_collect(self, log, event_id, user_id, request):
        log['event_id'] = event_id
        log['event_date'] = datetime.utcnow().isoformat()
        log['user_id'] = user_id
        log['source_id'] = gethostname()
        log['instance_id'] = self.id
        try:
            log['instance_id_type'] = getattr(self, 'Meta').id_type  
        except:
            log['instance_id_type'] = -1
        try:
            log['access_point_ip'] = request.get_host()
        except:
            log['access_point_ip'] = 'warning_unknown_ip'
        return log

    def save(self, event_id, user_id, request = HttpRequest()):
        log = {}
        prev_id = self.id
        try:
            super(ModelLog, self).save()
            log['event_outcome'] = self.LOG_OUTCOME_SUCCESS
        except Exception as e:
            raise e
            log['event_outcome'] = self.LOG_OUTCOME_ERROR
        if str(prev_id) == 'None':
            log['event_action_code'] = self.LOG_ACTION_CREATE
        else:
            log['event_action_code'] = self.LOG_ACTION_UPDATE
        self.__log_data_collect(log, event_id, user_id, request)
        at_log(log)

    def delete(self, event_id, user_id, request = HttpRequest()):
        log = {'event_action_code': self.LOG_ACTION_DELETE}
        self.__log_data_collect(log, event_id, user_id, request)
        try:
            super(ModelLog, self).delete()
            log['event_outcome'] = self.LOG_OUTCOME_SUCCESS
        except Exception as e:
            raise e
            log['event_outcome'] = self.LOG_OUTCOME_ERROR
        at_log(log)

