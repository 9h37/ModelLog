# -*- coding: utf-8 -*-
from django.db import models
from django.http import HttpRequest
from django.conf import settings
from datetime import datetime, tzinfo
from socket import gethostname
from hashlib import sha256
import settings
import json

def model_log(log):
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
        raise e #TODO: I don't know
    log_keys = log.keys()
    log_keys.sort()
    log_hash = sha256(settings.SECRET_KEY)
    for key in log_keys:
        log_hash.update(str(log[key]))
    log['signature'] = log_hash.hexdigest()
    #Logging
    settings.logger.info(json.dumps(log, sort_keys = True))

class ModelLog(models.Model):

    #RFC3881: http://www.faqs.org/rfcs/rfc3881.html

    LOG_ACTION_CREATE   = 'C'
    LOG_ACTION_READ     = 'R'
    LOG_ACTION_UPDATE   = 'U'
    LOG_ACTION_DELETE   = 'D'
    LOG_ACTION_EXECUTE  = 'E'

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
            log['event_outcome'] = 0
        except Exception as e:
            raise e
            log['event_outcome'] = 12
        if str(prev_id) == 'None':
            log['event_action_code'] = self.LOG_ACTION_CREATE
        else:
            log['event_action_code'] = self.LOG_ACTION_UPDATE
        self.__log_data_collect(log, event_id, user_id, request)
        model_log(log)

    def delete(self, event_id, user_id, request = HttpRequest()):
        log = {'event_action_code': self.LOG_ACTION_DELETE}
        self.__log_data_collect(log, event_id, user_id, request)
        try:
            super(ModelLog, self).delete()
            log['event_outcome'] = 0
        except Exception as e:
            raise e
            log['event_outcome'] = 12
        model_log(log)

