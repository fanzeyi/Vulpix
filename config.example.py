# -*- coding: utf-8 -*-

import os

mysql_config = {
    'mysql_host'     : '', 
    'mysql_user'     : '', 
    'mysql_password' : '', 
    'mysql_database' : ''
}

accept_lang = {
    'zh_cn' : 'zh_CN', 
    'en'    : 'en_US', 
}

site_config = {
    'site_title' : u'Online Judge',
    'base_domain' : '', 
    'login_url' : '/signin',
    'template_path' : os.path.join(os.path.dirname(__file__), 'tpl'),
    'static_path' : os.path.join(os.path.dirname(__file__), "static"),
    'i18n_path' : os.path.join(os.path.dirname(__file__), 'i18n'), 
    'xsrf_cookies' : True,
    'cookie_secret' : '', # 
    'bcrypt_salt' : '',  # import bcrypt; bcrypt.gensalt(log_rounds=4)
    'default_mail' : 'no-reply@fanhe.org', 
    'mail_server' : '127.0.0.1', 
}
