# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

flag=0
from gluon.tools import Crud
crud = Crud(db)
auth.settings.login_next=URL('Gallery')
auth.settings.logout_next=URL('index')
auth.settings.register_next = URL('Gallery')
crud.settings.delete_next = URL('Gallery')

if db(db.auth_group.role=='manager').isempty():
    group_id=auth.add_group('manager', 'can access the manage action')
    auth.add_permission(group_id, 'access to manage')
    auth.add_permission(group_id, 'create', db, 0)
    auth.add_permission(group_id, 'read', db, 0)
    auth.add_permission(group_id, 'delete', db, 0)
    auth.add_permission(group_id, 'update', db, 0)
    auth.add_permission(group_id, 'select', db, 0)

@auth.requires_permission('access to manage')
def manage():
    grid = SQLFORM.smartgrid(db.image)
    return dict(grid=grid)
    
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    images = db().select(db.image.ALL, orderby=db.image.title)
    return dict(images=images)

@auth.requires_login()
def Gallery():
    form = SQLFORM(db.image)
    if form.process().accepted:
        response.flash = 'The image is uploaded!'
    images = db().select(db.image.ALL, orderby=db.image.title)
    return dict(images=images, form=form)
    
def show():
    image = db.image(request.args(0)) or redirect(URL('index'))
    db.comment.image_id.default = image.id
    form = crud.create(db.comment, next=URL(args=image.id),
                     message='Your comment is posted!')
    comments = db(db.comment.image_id==image.id).select()
    return dict(image=image, comments=comments, form=form)
    
def delete():
    crud.delete(db.image, request.args(0)) 
    return dict()
    
def list_items():
    items = db().select(db.image.ALL, orderby=~db.image.votes)
    counter = db(db.auth_user.id > 0).count()
    return dict(items=items,counter=counter)

def download():
    return response.download(request, db)

def vote():
    item = db.image[request.vars.id]
    new_votes = item.votes
    l = item.voted
    if auth.user.username not in l:
        new_votes = item.votes + 1
        l = l + [str(auth.user.username)]
    item.update_record(voted=l)
    item.update_record(votes=new_votes)
    return str(new_votes)

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
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
