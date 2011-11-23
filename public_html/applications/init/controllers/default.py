# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

##### Page Functions #####
@auth.requires_login()
def index():
   redirect(URL('home'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """

    return dict(form=auth())

## Users home page.
@auth.requires_login()
def home():

    db.events.name.represent = lambda name, row: A(name, _href=URL('home'))
        
    ## get the challenges the users is currently enrolled in
    query = db.events.participants.contains(auth.user.id)
    events = db(query).select(orderby=db.events.name)

    return dict(events=events)

# Create a new challenge
@auth.requires_login()
def create():

    form = SQLFORM(db.events)
         
    if form.process(session=None, onvalidation=date_compare, formname='create').accepted:
        response.flash = 'form accepted'
        redirect(URL('home'))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
 
    return dict(form = form)

# Edit an existing Challenge. You can only edit challenges you created
@auth.requires_login()
def edit():

    event_id= request.vars.event
    event_query = db.events.id == event_id
    event = db(event_query).select().first()
    db.events.participants.writable = False
    
    form= SQLFORM(db.events, event)
    
    if form.process(session=None, onvalidation=date_compare, formname='edit').accepted:
        response.flash = 'form accepted'
        redirect(URL('home'))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'

    return dict(form = form)
    
## View the details of a challenge        
@auth.requires_login()
def challenge():

    event_id= request.vars.event
    event_query = db.events.id == event_id
    form= db(event_query).select().first()
    users = db(db.event_users.event == event_id).select()
    
    # Get the registered users for this event

    # a bunch of selects used while testing the leaders board
    # keeping them here for reference for now
#    entries = db().select(db.entries.user, distinct=True)
#    entries = db(db.event_users.event==event_id).select(db.event_users.event)
#    entries = db(db.event_users.event==event_id).select(db.event_users.event, db.event_users.user_name)
#    entries = db(db.event_users.event==event_id).select()      
    
    entries = db(db.entries.user.belongs(db(db.event_users.event==event_id).select())).\
        select(groupby=db.entries.user, orderby=~db.entries.date_entered)

    num_users = len(users)        
    form.writable = False

    return dict(form=form, entries=entries, num_users=num_users)

# User joins an existing Challenge
@auth.requires_login()
def join():
 
    event_id = request.vars.event
    user = auth.user.id
    goal = '0'
    
    # add this user to the event_users table
    db.event_users.insert(event=event_id, user_name=user, goal=goal)
 
    # update the event participants list with this user
    event_update = db.events.id == event_id
    event = db(event_update).select().first()
    partcipants = event.participants
    partcipants.append(auth.user.id)
    update = db(event_update).update(participants=partcipants)
        
    redirect(URL('home'))
 
# User can see their entries and make a new entry
@auth.requires_login()
def check_in():
    import time
    from datetime import date

    event_id = request.vars.event
    
    # Get data for this Event
    event = __get_event(event_id)
    metric_name = event.metric_name
    metric_type = event.metric_type
    
    # Get this users entries for this event
    entries = __get_entries(event_id)
    
    # Get users registered for this Event
    event_users = __get_event_users(event_id)
    user = event_users.id
    
    # Check frequency
    freq_result, err_msg = __check_frequency(event)
    
    # Check the date range of the event
    if __check_date_range(event):
        # Check the frequency range 
        if freq_result:
            # check if there's already been an entry today
            # TODO - this should check the check-in frequency field to see when a user is allowed to check-in
            entry = db((db.entries.user == user) & (db.entries.date_entered == date.today())).select().first()
        
            if entry is None:
                id = db.entries.insert(user=user, date_entered=date.today())                 
                entry = db(db.entries.id == id).select().first()
                exists = False
            elif entry.value is not None:
                exists = True
        
            db.entries.user.writable = False
            db.entries.date_entered.writable = False
    
            form = SQLFORM(db.entries, entry)
            if form.process().accepted:
                response.flash = 'form accepted'
                redirect(URL(r=request, f='challenge', vars=dict(event=event.id)))
            elif form.errors:
                response.flash = 'form has errors'
            else:
                response.flash = 'please fill the form'
    
        # Out of freq range so send the error message
        else:
            form = err_msg
    # Out of date range so send error message
    else:
        form = "This Challenge is not currently active. You can not submit any entries"
        
    return dict(entries=entries, metric_name=metric_name, form=form)

@auth.requires_login()
def search():

    ## get all challenges
    events = db(db.events).select(orderby=db.events.name)

    return dict(events=events)
        
# display the contact page        
def contact():

    return dict()

# display the about page
def about():
    
    return dict()
    
##### Utility Functions #####    

# Check the 
def __check_frequency(event):
    import time
    from datetime import date
    
    date_entered = date.today()
    start_date = event.start_date
    todays_date = date.today()
    timedelta = todays_date.day - start_date.day
    
    frequency = event.frequency
    
    if frequency == "Daily": 
        if timedelta % 1 == 0:
            return(True, "")
        else:
            remainder = timedelta % 1
            return(False, "It is not time to check-in yet. Check back in " + str(remainder) + " day")
    if frequency == "Weekly":
        if timedelta % 7 == 0:
            return(True, "")
        else:
            remainder = timedelta % 7
            return(False, "It is not time to check-in yet. Check back in " + str(remainder) + " days")
        
    # need to figure out a better way to hanldle months
    if frequency == "Monthly":
        if timedelta % 30 == 0:
            return(True, "")
        else:
            remainder = timedelta % 30
            return(False, "It is not time to check-in yet. Check back in " + str(remainder) + " days")

    if frequency == "1 Day":
        if timedelta % 1 == 0:
            return(True, "")
        else:
            # this should never happen
            remainder = timedelta % 1
            return(False, "It is not time to check-in yet. Check back in " + str(remainder) + " day")

# check if today is in between the start and end date of the challenge 
def __check_date_range(event):
    import time
    from datetime import date
    
    start_date = event.start_date
    end_date = event.end_date
    result = False
    if date.today() >= start_date:
        if date.today() <= end_date:
            result = True
        
    return(result)
        
# Get the users registered for this event
def get_users(event_id):

    user_query = db.event_users.event == event_id
    users = db(user_query).select()
            
    return (users)
    
# Get this users entries for the given event
def __get_entries(event_id):
    
    return(db(db.entries.user.belongs(db((db.event_users.event==event_id) & (db.event_users.user_name==auth.user.id)).select())).\
        select(orderby=db.entries.date_entered))

# Get event users
def __get_event_users(event_id):
    
    return(db((db.event_users.event==event_id) & (db.event_users.user_name==auth.user.id)).select(groupby=db.event_users.user_name).first())

    
# Get event data for selected event
def __get_event(event_id):
    
    event_query = db.events.id == event_id
    return (db(event_query).select().first())
    

# Make sure Start Date is less then End Date
def date_compare(form):
    if form.vars.start_date > form.vars.end_date:
        form.errors.end_date = 'End Date must be after Start Date'

def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs bust be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
