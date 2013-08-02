# -*- encoding: utf-8 -*-
from flask import render_template, abort, request, redirect, url_for, flash, session, current_app
from flask.views import MethodView

from jinja2 import TemplateNotFound
from flask.ext.wtf import Form, TextField, PasswordField, IntegerField, Required
from flask.ext.principal import Principal, Identity, AnonymousIdentity, identity_changed
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user

from application.app import app, db
from application.context_processors import general_menu
from models import Settings, Users, Roles
from lib.user import User
from forms import EditUserForm


# Principal(app)
#
# login_manager = LoginManager()
# login_manager.init_app(app)


# @login_manager.user_loader
# def load_user(user_id):
#     # Return an instance of the User model
#     return db.session.query(Users).get(user_id)


class LoginForm(Form):
    login = TextField()
    password = PasswordField()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/settings/', methods=['GET', 'POST'])
def settings():
    try:
        class ConfigVariablesForm(Form):
            pass

        variables = db.session.query(Settings).order_by('id').all()
        for variable in variables:
            setattr(ConfigVariablesForm,
                    variable.code,
                    TextField(variable.code, validators=[Required()], default="", description=variable.name))

        form = ConfigVariablesForm()
        for variable in variables:
            form[variable.code].value = variable.value

        if form.validate_on_submit():
            for variable in variables:
                variable.value = form.data[variable.code]
            db.session.commit()
            flash(u'Настройки изменены')
            return redirect(url_for('settings'))

        return render_template('settings.html', form=form)
    except TemplateNotFound:
        abort(404)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    # A hypothetical login form that uses Flask-WTF
    form = LoginForm()

    # Validate form input
    if form.validate_on_submit():
        # Retrieve the user from the hypothetical datastore
        user = db.session.query(Users).filter(login=form.login.data.strip()).first()
        check_user = User(user.login)

        # Compare passwords (use password hashing production)
        if check_user.check_password(form.password.data.strip(), user.password):
            # Keep the user info in the session using Flask-Login
            login_user(user)

            # Tell Flask-Principal the identity changed
            identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))

            return redirect(request.args.get('next') or url_for('index'))

    return render_template('user/login.html', form=form)


@app.route('/logout/')
@login_required
def logout():
    # Remove the user information from the session
    logout_user()

    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())

    return redirect(request.args.get('next') or '/')


@app.route('/users/')
def users():
    # return a list of users
    return render_template('user/list.html', users=db.session.query(Users).order_by(Users.id).all())


@app.route('/users/add/', methods=['GET', 'POST'])
def post_user():
    # create a new user
    db_roles = db.session.query(Roles).all()
    radio_roles = [(role.id, role.name) for role in db_roles]
    form = EditUserForm()
    form.role.choices = radio_roles
    if form.validate_on_submit():
        user = User(form.login.data.strip(), form.password.data.strip())
        if db.session.query(Users).filter(Users.login == user.login).count() > 0:
            return render_template('user/edit.html',
                                   errors=[u'Пользователь с логином <b>%s</b> уже существует' % user.login], form=form)
        db_user = Users(user.login, user.pw_hash)
        db_role = db.session.query(Roles).get(form.role.data)
        db_user.roles.append(db_role)
        db.session.add(db_user)
        db.session.commit()
        flash(u'Пользователь добавлен')
        return redirect(url_for('users'))
    return render_template('user/edit.html', form=form)


@app.route('/users/<int:user_id>/', methods=['GET', 'POST'])
def put_user(user_id):
    db_user = db.session.query(Users).get(user_id)
    if db_user is None:
        return render_template('user/list.html',
                               users=db.session.query(Users).order_by(Users.id).all(),
                               errors=u'Пользователя с id=%s не существует' % user_id)
    db_roles = db.session.query(Roles).all()
    radio_roles = [(role.id, role.name) for role in db_roles]
    form = EditUserForm(login=db_user.login)
    form.role.choices = radio_roles
    if form.validate_on_submit():
        password = form.password.data.strip()
        if password:
            user = User(form.login.data.strip(), form.password.data.strip())
            db_user.password = user.pw_hash
        else:
            user = User(form.login.data.strip())

        if db_user.login != user.login and db.session.query(Users).filter(Users.login == user.login).count() > 0:
            return render_template('user/edit.html',
                                   errors=[u'Пользователь с логином <b>%s</b> уже существует' % user.login], form=form)
        db_user.login = user.login
        db_role = db.session.query(Roles).get(form.role.data)
        db_user.roles[0] = db_role
        db.session.commit()
        flash(u'Пользователь изменен')
        return redirect(url_for('users'))
    return render_template('user/edit.html', form=form, user=db_user)


@app.route('/users/delete/<int:user_id>/', methods=['POST'])
def delete_user(user_id):
    # delete a single user
    errors = list()
    try:
        user = db.session.query(Users).get(user_id)
        db.session.delete(user)
        db.session.commit()
    except Exception, e:
        errors.append(u'Ошибка при удалении пользователя: %s' % e)
    else:
        flash(u'Пользователь удалён')
        return redirect(url_for('users'))
    return render_template('user/list.html', users=db.session.query(Users).order_by(Users.id).all(), errors=errors)
