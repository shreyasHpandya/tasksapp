# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#
# This is a samples controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# - call exposes all registered services (none by default)
#
from datetime import date


@auth.requires_login()
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simple replace the two lines below with:
    return auth.wiki()
    """
    tasks = db((db.task_user_mapping.auth_user == auth.user.id) & (db.task.status == False)).select(
        db.task.ALL,
        join=[db.auth_user.on(db.task.id == db.task_user_mapping.task)], groupby=db.task.id)
    return dict(tasks=tasks)


@auth.requires_login()
def closedTasks():
    tasks = db((db.task_user_mapping.auth_user == auth.user.id) & (db.task.status == True)).select(
        db.task.ALL,
        join=[db.auth_user.on(db.task.id == db.task_user_mapping.task)], groupby=db.task.id)
    return response.render('default/index.html', tasks=tasks)


@auth.requires_membership('manager')
def allTasks():
    tasks = db(db.task.id > 0).select()
    return dict(tasks=tasks)


@auth.requires_login()
def toggleTask():
    task_id = request.args[0]
    task = db(db.task.id == task_id).select().first()
    task.update_record(status=not task.status)
    return str(task.status)


@auth.requires_membership('manager')
def createOrUpdateTask():
    #Check whether Create or Update form required
    if request.args(0):
        task = db(db.task.id == request.args[0]).select().first()
        form = SQLFORM(db.task, task, upload=URL('default', 'download'))
        selected_user_rows = db(db.task_user_mapping.task == task.id).select(db.task_user_mapping.auth_user)
        selected_users = [user.auth_user for user in selected_user_rows]
    else:
        selected_users = []
        form = SQLFORM(db.task)
    #add multiple select field for users
    all_users = db(db.auth_user.id > 0).select()
    options = []
    for user in all_users:
        if user.id in selected_users:
            options.append(OPTION(user.first_name, _value=user.id, _selected="selected"))
        else:
            options.append(OPTION(user.first_name, _value=user.id))
    assingned_to = TR(LABEL('Assign To:'), SELECT(_name="users", _multiple='', *options))
    form[0].insert(-1, assingned_to)

    if request.env.request_method == "GET":
        response.flash = "please fill the form"
    else:
        form = form.process()
        if form.accepted:
            response.flash = "Done"
            db(db.task_user_mapping.task == form.vars.id).delete()
            for user in form.vars.users:
                db.task_user_mapping.insert(task=form.vars.id, auth_user=user)
        else:
            if form.errors:
                response.flash = "Correct Errors"
    return dict(form=form)


@auth.requires_login()
def taskAttachment():
    task = db(db.task.id == request.args[0]).select().first()
    task.update_record(attachment=db.task.attachment.store(request.post_vars.attachment.file,
                       request.post_vars.attachment.filename))
    return dict()


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
    return response.download(request, db)


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
