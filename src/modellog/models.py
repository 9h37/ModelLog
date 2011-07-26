# -*- coding: utf-8 -*-
from django.db import models
from django.http import HttpRequest
from django.conf import settings
from datetime import datetime
import logging
import socket
import at_log

class ModelLog(models.Model):
    """
    Log various informations relative to the event and its source that led to
    the save() or delete() call along with any data that may or may not appear
    necessary to the RFC3881 compliance, ie. data about the object instance.
    RFC3881 compliance of the log messages is required.
    RFC3881 url: http://www.faqs.org/rfcs/rfc3881.html
    """

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
        log['source_id'] = socket.gethostname()
        log['instance_id'] = self.id
        try:
            log['instance_id_type'] = str(getattr(self, 'Meta').id_type)
        except AttributeError:
            logging.warning('{0} has no meta id_type attribute'.format(type(self)))
            log['instance_id_type'] = 'unknown'
        if request is not None:
            log['access_point_ip'] = request.get_host()
        else:
            logging.warning('unspecified access point ip')
            log['access_point_ip'] = 'unknown'
        return log

    def save(self, event_id, user_id, request = None):
        log = {}
        prev_id = self.id
        try:
            super(ModelLog, self).save()
            log['event_outcome'] = self.LOG_OUTCOME_SUCCESS
        except Exception as e:
            log['event_outcome'] = self.LOG_OUTCOME_ERROR
            at_log.at_log(log)
            raise e
        else:
            if prev_id is None:
                log['event_action_code'] = self.LOG_ACTION_CREATE
            else:
                log['event_action_code'] = self.LOG_ACTION_UPDATE
            self.__log_data_collect(log, event_id, user_id, request)
            at_log.at_log(log)

    def delete(self, event_id, user_id, request = None):
        log = {'event_action_code': self.LOG_ACTION_DELETE}
        self.__log_data_collect(log, event_id, user_id, request)
        try:
            super(ModelLog, self).delete()
            log['event_outcome'] = self.LOG_OUTCOME_SUCCESS
        except Exception as e:
            log['event_outcome'] = self.LOG_OUTCOME_ERROR
            at_log.at_log(log)
            raise e
        else:
            at_log.at_log(log)
