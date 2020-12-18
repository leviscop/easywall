"""The app module contains all information of the Flask app."""
from datetime import datetime, timezone
from inspect import stack
from logging import info, warning, debug
from time import sleep
from typing import Tuple, Union
from flask import Flask, wrappers
from flask_ipban import IpBan
from werkzeug.wrappers import Response

from easywall.config import Config
from easywall.log import Log
from easywall.rules_handler import RulesHandler
from easywall.utility import execute_os_command, create_file_if_not_exists
from easywall.web.apply import apply, apply_save, apply_forceful
from easywall.web.blacklist import blacklist, blacklist_save
from easywall.web.custom import custom, custom_save
from easywall.web.error import forbidden, page_not_found
from easywall.web.firstrun import firstrun, firstrun_save
from easywall.web.forwarding import forwarding, forwarding_save
from easywall.web.index import index
from easywall.web.login import login_post, logout
from easywall.web.options import options, options_save
from easywall.web.ports import ports, ports_save, add_port
from easywall.web.webutils import Webutils
from easywall.web.whitelist import whitelist, whitelist_save

import os

INSTALL_PATH = os.environ["INSTALL_PATH"]

APP = Flask(__name__)
CONFIG_PATH = INSTALL_PATH + "/config/web.ini"
LOG_CONFIG_PATH = INSTALL_PATH + "/config/log.ini"


@APP.after_request
def apply_headers(response: wrappers.Response) -> wrappers.Response:
    """TODO: Doku."""
    response.headers["Connection"] = "keep-alive"
    response.headers["Date"] = datetime.now(tz=timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "script-src 'self' ; frame-ancestors 'none'"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Permissions-Policy"] = (
        "accelerometer=(), "
        "camera=(), "
        "geolocation=(), "
        "gyroscope=(), "
        "magnetometer=(), "
        "microphone=(), "
        "payment=(), "
        "usb=()"
    )
    response.headers["Expect-CT"] = (
        "max-age=0, "
        "report-uri=\"https://wdkro.de/expect-ct/csp-report/create\""
    )
    return response


@APP.route('/')
def index_route() -> Union[Response, str]:
    """Call the corresponding function from the appropriate module."""
    utils = Webutils()
    if utils.check_first_run() is True:
        return firstrun()
    return index()


@APP.route('/options')
def options_route() -> str:
    """Call the corresponding function from the appropriate module."""
    return options()


@APP.route('/options-save', methods=['POST'])
def options_save_route() -> str:
    """Call the corresponding function from the appropriate module."""
    return options_save()


@APP.route('/blacklist')
def blacklist_route() -> str:
    """Call the corresponding function from the appropriate module."""
    return blacklist()


@APP.route('/blacklist-save', methods=['POST'])
def blacklist_save_route() -> str:
    """Call the corresponding function from the appropriate module."""
    return blacklist_save()


@APP.route('/whitelist')
def whitelist_route() -> str:
    """Call the corresponding function from the appropriate module."""
    return whitelist()


@APP.route('/whitelist-save', methods=['POST'])
def whitelist_save_route() -> str:
    """Call the corresponding function from the appropriate module."""
    return whitelist_save()


@APP.route('/forwarding')
def forwarding_route() -> str:
    """Call the corresponding function from the appropriate module."""
    return forwarding()


@APP.route('/forwarding-save', methods=['POST'])
def forwarding_save_route() -> str:
    """Call the corresponding function from the appropriate module."""
    return forwarding_save()


@APP.route('/ports')
def ports_route() -> str:
    """Call the corresponding function from the appropriate module."""
    return ports()


@APP.route('/ports-save', methods=['POST'])
def ports_save_route() -> str:
    """Call the corresponding function from the appropriate module."""
    return ports_save()


@APP.route('/custom')
def custom_route() -> str:
    """Call the corresponding function from the appropriate module."""
    return custom()


@APP.route('/custom-save', methods=['POST'])
def custom_save_route() -> str:
    """Call the corresponding function from the appropriate module."""
    return custom_save()


@APP.route('/apply')
def apply_route() -> str:
    """Call the corresponding function from the appropriate module."""
    return apply()


@APP.route('/apply-save', methods=['POST'])
def apply_save_route() -> str:
    """Call the corresponding function from the appropriate module."""
    return apply_save()


@APP.route('/login', methods=['POST'])
def login_post_route() -> Union[Response, str]:
    """Call the corresponding function from the appropriate module."""
    return login_post(MAIN.ip_ban)


@APP.route("/logout")
def logout_route() -> str:
    """Call the corresponding function from the appropriate module."""
    return logout()


@APP.route("/firstrun")
def firstrun_route() -> Union[Response, str]:
    """Call the corresponding function from the appropriate module."""
    return firstrun()


@APP.route("/firstrun", methods=['POST'])
def firstrun_save_route() -> Union[Response, str]:
    """Call the corresponding function from the appropriate module."""
    return firstrun_save()


@APP.errorhandler(404)
def page_not_found_route(error: str) -> Union[str, Tuple[str, int]]:
    """Call the corresponding function from the appropriate module."""
    return page_not_found(error)


@APP.errorhandler(403)
def forbidden_route(error: str) -> Union[str, Tuple[str, int]]:
    """Call the corresponding function from the appropriate module."""
    return forbidden(error)


@APP.before_request
def before_request_func() -> None:
    """TODO: Doku."""
    MAIN.ip_ban.ip_record.read_updates(True)


class DefaultConfig(object):
    """TODO: Doku."""

    DEBUG = False
    TESTING = False
    SECRET_KEY = os.urandom(265)
    ENV = "production"
    SESSION_COOKIE_NAME = "easywall"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 600
    PREFERRED_URL_SCHEME = "https"
    MAX_CONTENT_LENGTH = 10240


class ProductionConfigSecure(DefaultConfig):
    """TODO: Doku."""


class ProductionConfig(DefaultConfig):
    """TODO: Doku."""

    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False
    PREFERRED_URL_SCHEME = "http"


class DevelopmentConfig(ProductionConfig):
    """TODO: Doku."""

    DEBUG = True
    TESTING = True
    ENV = "development"


class Main:
    """TODO: Doku."""

    def __init__(self, debug_mode: bool = False) -> None:
        """TODO: Doku."""

        self.cfg_log = Config(LOG_CONFIG_PATH)
        loglevel = self.cfg_log.get_value("LOG", "level")
        to_stdout = self.cfg_log.get_value("LOG", "to_stdout")
        to_files = self.cfg_log.get_value("LOG", "to_files")
        logpath = self.cfg_log.get_value("LOG", "filepath")
        logfile = self.cfg_log.get_value("LOG", "filename")
        self.log = Log(str(loglevel), bool(to_stdout), bool(to_files), str(logpath), str(logfile))

        if is_already_started():
            return

        info("starting easywall-web")

        self.cfg = Config(CONFIG_PATH)

        if debug_mode is True:
            info("loading Flask debug configuration")
            APP.config.from_object('easywall.web.__main__.DevelopmentConfig')
        else:
            info("loading Flask production configuration")
            if self.cfg.get_value("uwsgi", "http-socket") != "":
                warn = ("Running server through HTTP. This is not recommended nor"
                        " safe unless running behind a trusted reverse proxy.")
                warning(warn)
                APP.config.from_object('easywall.web.__main__.ProductionConfig')
            else:
                APP.config.from_object('easywall.web.__main__.ProductionConfigSecure')
            
        self.rules_handler = RulesHandler()

        self.login_attempts = self.cfg.get_value("WEB", "login_attempts")
        self.login_bantime = self.cfg.get_value("WEB", "login_bantime")
        self.ip_ban = IpBan(app=APP, ban_count=self.login_attempts,
                            ban_seconds=self.login_bantime, ipc=True)
        self.ip_ban.url_pattern_add('^/static.*$', match_type='regex')

        info("loading iptables rules...")
        load_rules()

    def run_debug(self) -> None:
        """TODO: Doku."""
        port = self.cfg.get_value("WEB", "bindport")
        host = self.cfg.get_value("WEB", "bindip")
        APP.run(str(host), str(port))


def is_already_started() -> bool:
    flag_file = f"{INSTALL_PATH}/.web-started"
    if os.path.isfile(flag_file):
        warning("easywall-web is already started!")
        debug(f"| Call stack: {stack()}")
        return True
    create_file_if_not_exists(flag_file)
    return False


def load_rules():
    open_web_port()
    apply_forceful()


def open_web_port() -> bool:
    running_port = execute_os_command("ss -tpan | grep uwsgi | xargs | cut -d ' ' -f4 | cut -d ':' -f2").output.strip()
    entry: dict = {"ruletype": "tcp", "port": running_port, "description": "easywall-web", "ssh": False}
    added = add_port(entry)
    if not added:
        return False
    # Remove previous easywall-web rule (if any)
    for rule in RulesHandler().rules["current"]["tcp"]:
        if rule["description"] == "easywall-web" and rule["port"] != running_port:
            del rule
    return True


if __name__ == "__main__":
    MAIN = Main(debug_mode=True)
    MAIN.run_debug()
else:
    MAIN = Main()
