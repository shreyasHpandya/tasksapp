db.define_table('task',
                Field('name', 'string'),
                Field('due', 'date'),
                Field('status', 'boolean'),
                Field('attachment', 'upload'),
                format='%(name)s %(id)s')

db.define_table('task_user_mapping',
                Field('task', 'reference task'),
                Field('auth_user', 'reference auth_user')
                )
