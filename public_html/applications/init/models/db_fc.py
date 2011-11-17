# coding: utf8
# Tables for the Fitness Challenge website

db.define_table('events',
    Field('name', 'string'),
    Field('description','text'),
    Field('start_date','date'),
    Field('end_date','date'),
    Field('participants', 'list:reference auth_user'),
    Field('check_in', 'string'),
    Field('status', 'string'),
    Field('metric_type', 'string'),
    auth.signature,
    format='%(name)s')

#format = lambda row: "%s - %s" % (row.series.name,  row.number) 
db.events.participants._format = lambda row: "%s %s" % (row.first_name, row.last_name)
#db.events.participants._format = '%(first_name)s %(last_name)s'
db.events.check_in.requires=IS_IN_SET(('Daily','Weekly','Monthly'))
db.events.status.requires=IS_EMPTY_OR(IS_IN_SET(('Pending','In-Progress','Ended')))
db.events.metric_type.requires=IS_IN_SET(('Reps/Laps','Time','BMI', '% Weight Loss', 'lbs lost'))

db.define_table('event_status',
    Field('event_name', 'string'),
    Field('user_name', 'string'),
    Field('goal', 'integer'),
    Field('check_in', 'list:integer'))
    
db.event_status.event_name.requires=IS_IN_DB(db, 'events.name')
