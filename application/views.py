# -*- encoding: utf-8 -*-
from flask import render_template, abort, request, redirect, url_for, flash, session, current_app
from flask.views import MethodView

from jinja2 import TemplateNotFound
from flask.ext.wtf import Form, TextField, PasswordField, IntegerField, Required
from flask.ext.principal import Principal, Identity, AnonymousIdentity, identity_changed
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user

from application.app import app, db
from application.context_processors import general_menu
from models import Settings, Users
from lib.user import User
from forms import EditUserForm


Principal(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # Return an instance of the User model
    return db.session.query(Users).get(user_id)


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

            return redirect(request.args.get('next') or '/')

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


class UserAPI(MethodView):

    def get(self, user_id):
        if user_id is None:
            # return a list of users
            pass
        else:
            # expose a single user
            pass

    def post(self):
        # create a new user
        pass

    def delete(self, user_id):
        # delete a single user
        pass

    def put(self, user_id):
        form = EditUserForm()
        if form.validate_on_submit():
            user = User(form.login, form.password)
            db_user = db.session.query(Users).get(user_id)
            db_user.login = user.login
            db_user.password = user.pw_hash
            db.session.commit()
            flash(u'Пользователь изменен')


def register_api(view, endpoint, url, pk='id', pk_type='int'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET', ])
    app.add_url_rule(url, view_func=view_func, methods=['POST', ])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])

register_api(UserAPI, 'user_api', '/users/')