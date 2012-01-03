# coding: utf8
# Tables for the Fitness Challenge website

db.define_table('events',
    Field('name', 'string'),
    Field('description','text'),
    Field('start_date','date'),
    Field('end_date','date'),
    Field('participants', 'list:reference auth_user'),
    Field('frequency', 'string'),
    Field('status', 'string'),
    Field('metric_name', 'string'),
    Field('metric_type', 'string'),
    auth.signature,
    format='%(name)s')

db.events.name.requires=IS_NOT_EMPTY(error_message='Enter a name for the challenge')
db.events.start_date.requires=IS_DATE(error_message='Enter a date in the format YYYY-MM-DD')
db.events.end_date.requires=IS_DATE(error_message='Enter a date in the format YYYY-MM-DD')
db.events.frequency.requires=IS_IN_SET(('Single Day', 'Daily','Weekly','Monthly'))
db.events.status.requires=IS_EMPTY_OR(IS_IN_SET(('Pending','In-Progress','Ended')))
db.events.metric_name.requires=IS_NOT_EMPTY(error_message='Enter a metric name')
db.events.metric_type.requires=IS_IN_SET(('Repetitions', 'Laps', 'Miles', 'Time', 'BMI', 
                                          '% Weight Loss', 'lbs lost', 'Steps'),
                                          error_message='Enter a metric type')

db.define_table('event_users',
    Field('event', 'reference events'),
    Field('user_name', 'reference auth_user'),  
    Field('goal', 'double'),
    Field('last_entry', 'date'),
#    Field('frequency', 'list:string'),
    format = lambda row: "%s - %s" % (row.event.name,  row.user_name.first_name))

db.event_users.event.requires=IS_IN_DB(db, 'events.id')
db.event_users.last_entry.requires=IS_EMPTY_OR(IS_DATE())
    
db.define_table('entries',
    Field('user', 'reference event_users'),
    Field('date_entered', 'date'),
    Field('value', 'double'),
    format='%(user)s %(date_entered)s')

#db.entries.user.requires=IS_IN_DB(db, 'event_users.id')