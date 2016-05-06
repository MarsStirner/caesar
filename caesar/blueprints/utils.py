# coding: utf-8

from flask import abort

from nemesis.lib.user import UserProfileManager


def check_admin_profile():
    if not UserProfileManager.has_ui_admin():
        raise abort(403, u'Доступ возможен только администратору системы')