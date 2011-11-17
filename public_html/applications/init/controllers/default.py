# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

@auth.requires_login()
def index():
   redirect(URL('home'))

##def index():

    ## if user is already logged in, redirect to the user home page.
##    if auth.user:
##        redirect(URL(r=request, f='home'))  
##    else:
##        redirect(URL(r=request, f='user'))

##    form = auth()        
##    return dict(form = form)

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
    query = db.events.participants == auth.user.id
    events = db(query).select(orderby=db.events.name)

    return dict(events=events)


@auth.requires_login()
def create_challenge():

    form = SQLFORM(db.events)
    
    if form.process(session=None, onvalidation=date_compare, formname='create_challenge').accepted:
        response.flash = 'form accepted'
        redirect(URL('home'))
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'

    return dict(form = form)

def date_compare(form):
    if form.vars.start_date > form.vars.end_date:
        form.errors.end_date = 'End Date must be after Start Date'
        
@auth.requires_login()
def view_challenge():

    event_id= request.vars.events
    event_query = db.events.id == event_id
    event = db(event_query).select().first()
    
    form = SQLFORM(db.events, event)

    return dict(form = form)

def get_leaders_board(event_id):

    
    return dict()
    
@auth.requires_login()
def search():

    ## get all challenges

    events = db(db.events).select(orderby=db.events.name)

    return dict(events=events)
        
def contact():

    return dict()

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
