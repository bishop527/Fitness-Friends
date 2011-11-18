# coding: utf8
# Tables for the Fitness Challenge website

db.define_table('events',
    Field('name', 'string', requires=IS_NOT_EMPTY(error_message='Enter a name for the challenge')),
    Field('description','text'),
    Field('start_date','date', requires=IS_DATE(error_message='Enter a date in the format YYYY-MM-DD')),
    Field('end_date','date', requires=IS_DATE(error_message='Enter a date in the format YYYY-MM-DD')),
    Field('participants', 'list:reference auth_user'),
    Field('check_in', 'string'),
    Field('status', 'string'),
    Field('metric_name', 'string', requires=IS_NOT_EMPTY(error_message='Enter a metric name')),
    Field('metric_type', 'string'),
    auth.signature,
    format='%(name)s')

db.auth_user._format = '%(first_name)s %(last_name)s'
db.events.check_in.requires=IS_IN_SET(('Daily','Weekly','Monthly'))
db.events.status.requires=IS_EMPTY_OR(IS_IN_SET(('Pending','In-Progress','Ended')))
db.events.metric_type.requires=IS_IN_SET(('Repititions', 'Laps', 'Miles', 'Time', 'BMI', '% Weight Loss', 'lbs lost'), error_message='Enter a metric type')

db.define_table('event_status',
    Field('event', 'reference events'),
    Field('user_name', 'reference auth_user'),
    Field('goal', 'integer'),
    Field('check_in', 'list:integer'),
    format='%(event.name)s')
    
db.event_status.event._format = lambda row: "%s" % (row.name)
db.event_status.event.requires=IS_IN_DB(db, 'events.id')
