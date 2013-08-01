# -*- encoding: utf-8 -*-
from flask import render_template, abort, request, redirect, url_for, flash, session, current_app

from jinja2 import TemplateNotFound
from flask.ext.wtf import Form, TextField, PasswordField, IntegerField, Required
from flask.ext.principal import Principal, Identity, AnonymousIdentity, identity_changed
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user

from application.app import app, db
from application.context_processors import general_menu
from models import Settings, User


Principal(app)

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    # Return an instance of the User model
    return db.session.query(User).get(user_id)


class LoginForm(Form):
    login = TextField()
    password = PasswordField()


@app.route('/')
def index():
    return render_template('base.html')


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    # A hypothetical login form that uses Flask-WTF
    form = LoginForm()

    # Validate form input
    if form.validate_on_submit():
        # Retrieve the user from the hypothetical datastore
        user = db.session.query(User).filter(login=form.login.data).first()

        # Compare passwords (use password hashing production)
        if form.password.data == user.password:
            # Keep the user info in the session using Flask-Login
            login_user(user)

            # Tell Flask-Principal the identity changed
            identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))

            return redirect(request.args.get('next') or '/')

    return render_template('user/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    # Remove the user information from the session
    logout_user()

    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())

    return redirect(request.args.get('next') or '/')