"""Create functions for user login and logout."""
from logging import info, warning, debug
from typing import Union

from flask import redirect, render_template, request, session
from flask_ipban import IpBan
from werkzeug.wrappers import Response

from easywall.utility import generate_hash, generate_salt
from easywall.web.webutils import Webutils


def login(message: Union[None, str] = None, messagetype: Union[None, str] = None) -> str:
    """
    Return the login page which shows messages.

    also the function updates the last commit informations in the config file
    """
    utils = Webutils()
    utils.update_last_commit_infos()
    payload = utils.get_default_payload("Signin", "signin")
    if messagetype is not None:
        payload.messagetype = messagetype
    if message is not None:
        payload.message = message
    return render_template('login.html', vars=payload)


def login_post(ip_ban: IpBan) -> Union[Response, str]:
    """
    Handle the login post request and if all information are correct.

    a session variable is set to store the login information
    """
    utils = Webutils()
    salt = generate_salt()
    pw_hash = generate_hash(salt, request.form['password'])
    stored_pwd = utils.cfg.get_value("WEB", "password")
    debug(f"presented pass: {pw_hash} | stored pass: {stored_pwd}")
    if request.form['username'] == utils.cfg.get_value(
            "WEB", "username") and pw_hash == stored_pwd:
        session.clear()
        session['logged_in'] = True
        session['ip_address'] = request.remote_addr
        session.permanent = True
        info("Successful login for the user {}. ".format(request.form['username']) +
             "IP address of the remote device: {}".format(request.remote_addr))
        return redirect("/")
    else:
        warning("Failed login attempt for the user {} detected. ".format(request.form['username']) +
                "IP address of the remote device: {}".format(request.remote_addr))
    ip_ban.add(ip=request.remote_addr)
    return login("Wrong username or password.", "danger")


def logout() -> str:
    """Remove the logged_in session variable if the user is logged in."""
    utils = Webutils()
    if utils.check_login(request) is True:
        session['logged_in'] = False
        return login("You have been logged off successfully.", "success")
    else:
        return login()
