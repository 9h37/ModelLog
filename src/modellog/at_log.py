# -*- coding: utf-8 -*-
from hashlib import sha256
import settings
import json

def at_log(log):
    for required in (
        'event_id',             #5.1.1. Event ID                        required
        'event_action_code',    #5.1.2. Event Action Code,              optional
        'event_date',           #5.1.3. Event Date/Time                 required
        'event_outcome',        #5.1.4. Event Outcome Indicator         required
        'user_id',              #5.2.1. User ID                         required
        'access_point_ip',      #5.3.2. Network Access Point ID         optional
        'source_id',            #5.4.2. Audit Source ID                 required
        'instance_id_type',     #5.5.4. Participant Object ID Type Code required
        'instance_id',          #5.5.6. Participant Object ID           required
        ):
        if required not in log.keys():
            print('warning: ' + required + ' datafield not given in the log message')

    log_keys = log.keys()
    log_keys.sort()
    log_hash = sha256(settings.SECRET_KEY)
    for key in log_keys:
        log_hash.update(str(log[key]))
    log['signature'] = log_hash.hexdigest()

    settings.logger.info(json.dumps(log))
