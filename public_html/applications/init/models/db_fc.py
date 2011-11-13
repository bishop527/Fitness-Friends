# coding: utf8
# Tables for the Fitness Challenge website

db.define_table('challenges',
    Field('name', 'string'),
    Field('description','text'),
    Field('start_date','date'),
    Field('end_date','date'),
    Field('participants', 'list:reference auth_user'),
    Field('check_in', 'string'),
    Field('status', 'string'),
    Field('metric',),
    auth.signature,
    format='%(name)s')

db.challenges.check_in.requires=IS_IN_SET(('Daily','Weekly','Monthly'))
db.challenges.status.requires=IS_IN_SET(('Pending','In-Progress','Ended'))
