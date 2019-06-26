import logging
import logging.config
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from flask_wtf.csrf import CsrfProtect
from flask_mail import Mail
from flask_marshmallow import Marshmallow

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

import json

env = os.environ.get('FLASK_ENV', 'development')

SENTRY_DSN = os.environ.get('SENTRY_DSN', None)
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[FlaskIntegration()])

app = Flask(__name__, static_folder="static")
app.config.from_pyfile('../config/config.py')

# setup logging
with open('config/logging-%s.yaml' % env) as f:
    import yaml
    logging.config.dictConfig(yaml.load(f))

logger = logging.getLogger(__name__)

# Setup Caching

if app.config['DEBUG'] and not app.config['DEBUG_CACHE']:
    cache_type = 'null'
else:
    cache_type = 'filesystem'

cache = Cache(
    app,
    config={
        'CACHE_TYPE': cache_type,
        'CACHE_DIR': '/tmp/pmg-cache',
        'CACHE_DEFAULT_TIMEOUT': 60 * 60,
    })


def should_skip_cache(request, current_user):
    if current_user.is_anonymous():
        if app.config['DEBUG_CACHE']:
            logger.debug("cached value ALLOWED for %r", request.url)
        return False
    else:
        if app.config['DEBUG_CACHE']:
            logger.debug("cached value NOT ALLOWED for %r", request.url)
        return True


def cache_key(request):
    if app.config['DEBUG_CACHE']:
        logger.debug("cache key %r", request.url)
    return request.url


db = SQLAlchemy(app, session_options={"autoflush": False})
# Define naming constraints so that Alembic just works
# See http://docs.sqlalchemy.org/en/rel_0_9/core/constraints.html#constraint-naming-conventions
db.metadata.naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
migrate = Migrate(app, db, transaction_per_migration=True)
csrf = CsrfProtect(app)
mail = Mail(app)
ma = Marshmallow(app)

UPLOAD_PATH = app.config['UPLOAD_PATH']
if not os.path.isdir(UPLOAD_PATH):
    os.mkdir(UPLOAD_PATH)

# override flask mail's send operation to inject some customer headers
original_send = mail.send


def send_email_with_sendgrid(message):
    extra_headers = {
        "filters": {
            "templates": {
                "settings": {
                    "enable": "1",
                    "template_id":
                    app.config['SENDGRID_TRANSACTIONAL_TEMPLATE_ID']
                }
            },
            "ganalytics": {
                "settings": {
                    "enable": "1",
                    "utm_medium": "email",
                    "utm_source": "transactional",
                    "utm_campaign": "user-account"
                }
            }
        }
    }
    message.extra_headers = {'X-SMTPAPI': json.dumps(extra_headers)}
    original_send(message)


app.extensions.get('mail').send = send_email_with_sendgrid

# setup assets
from flask_assets import Environment, Bundle
assets = Environment(app)
assets.url_expire = False
assets.debug = app.debug
# source files
assets.load_path = ['%s/static' % app.config.root_path]

from webassets.filter.pyscss import PyScss

assets.register(
    'css',
    Bundle(
        'font-awesome-4.7.0/css/font-awesome.min.css',
        'chosen/chosen.min.css',
        'resources/css/review.css',
        Bundle(
            'resources/css/style.scss',
            'resources/css/bill-progress.scss',
            'resources/css/bootstrap-sortable.css',
            filters=PyScss(load_paths=assets.load_path),
            output='stylesheets/styles.%(version)s.css'),
        output='stylesheets/app.%(version)s.css'))

assets.register(
    'admin-css',
    Bundle(
        'font-awesome-4.7.0/css/font-awesome.min.css',
        Bundle(
            'resources/css/admin.scss',
            filters=PyScss(load_paths=assets.load_path),
            output='stylesheets/admin-styles.%(version)s.css'),
        output='stylesheets/admin.%(version)s.css'))

assets.register(
    'js',
    Bundle(
        'bower_components/jquery/dist/jquery.min.js',
        'bower_components/bootstrap-sass/assets/javascripts/bootstrap.min.js',
        'resources/javascript/vendor/lunr-0.7.1.min.js',
        'chosen/chosen.jquery.js',
        'resources/javascript/committees.js',
        'resources/javascript/users.js',
        'resources/javascript/members.js',
        'resources/javascript/hansards.js',
        'resources/javascript/provincial-overview.js',
        'resources/javascript/calls-for-comments.js',
        'resources/javascript/pmg.js',
        'resources/javascript/moment.min.js',
        'resources/javascript/bootstrap-sortable.js',
        'resources/javascript/bills.js',
        output='javascript/app.%(version)s.js'))

assets.register(
    'admin-js',
    Bundle(
        'resources/javascript/admin/admin.js',
        'resources/javascript/admin/email_alerts.js',
        output='javascript/admin.%(version)s.js'))

# background tasks
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from threading import Thread
scheduler = BackgroundScheduler({
    'apscheduler.jobstores.default':
    SQLAlchemyJobStore(engine=db.engine),
    'apscheduler.executors.default': {
        'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
        'max_workers': '2',
    },
    'apscheduler.timezone':
    'UTC',
})
if app.config['RUN_PERIODIC_TASKS']:
    scheduler.start()

# if we don't do this in a separate thread, we hang trying to connect to the db
import pmg.tasks
Thread(target=pmg.tasks.schedule).start()

import helpers
import views
import user_management
import admin

from pmg.api.v1 import api as api_v1
app.register_blueprint(api_v1, subdomain='api')
# api-internal.pmg.org.za resolves to the internal IP of the API host
app.register_blueprint(api_v1, subdomain='api-internal')

from pmg.api.v2 import api as api_v2
app.register_blueprint(api_v2, subdomain='api', url_prefix='/v2')
# api-internal.pmg.org.za resolves to the internal IP of the API host
app.register_blueprint(api_v2, subdomain='api-internal', url_prefix='/v2')
