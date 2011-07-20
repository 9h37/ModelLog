# -*- coding: utf-8 -*-
from django.db import models
from django.http import HttpRequest
from django.conf import settings
from datetime import datetime, timedelta
from socket import gethostname
from hashlib import sha256
import settings

class ModelLog(models.Model):

    #TODO (required) from RFC3881 (http://www.faqs.org/rfcs/rfc3881.html):
    #5.1.1  Event ID
    #5.4.2  Audit Source ID
    #5.5.4  Participant Object ID Type Code
    #5.5.6  Participant Object ID

    #RFC3881 5.1.2 Event Action Code, optional
    LOG_ACTION_CREATE   = 'C'
    LOG_ACTION_READ     = 'R'
    LOG_ACTION_UPDATE   = 'U'
    LOG_ACTION_DELETE   = 'D'
    LOG_ACTION_EXECUTE  = 'E'

    def __unicode__(self):
        return str(self.id)

    def __log(self, action, request):
        current_datetime = datetime.now()
        current_datetime -= timedelta(microseconds=current_datetime.microsecond) #get rid of the microseconds
        log = {
            'date':current_datetime.isoformat(' '), #RFC3881 5.1.3
            'host':gethostname(),
            'type':type(self),
            'id':self.id,
            'action':action,
            'secret':settings.SECRET_KEY,
        }
        try:
            log['ip'] = request.get_host()
        except:
            log['ip'] = '[warning:unknown]'
        log_data_format = '%(date)s %(host)s %(ip)s %(type)s %(id)s %(action)s'
        log['hash'] = sha256((log_data_format + ' $(secret)s') % log).hexdigest()
        settings.logger.info((log_data_format + ' %(hash)s') % log)

    def save(self, request = HttpRequest()):
        prev_id = self.id
        super(ModelLog, self).save()
        if str(prev_id) == 'None':
            self.__log(self.LOG_ACTION_CREATE, request)
        else:
            self.__log(self.LOG_ACTION_UPDATE, request)

    def delete(self, request = HttpRequest()):
        super(ModelLog, self).delete()
        self.__log(self.LOG_ACTION_DELETE, request)
