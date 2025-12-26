import logging
from flask import Flask, redirect, render_template, request, url_for, session

from google.auth.transport import requests
import google.oauth2.id_token

logger = logging.getLogger(__name__)

firebase_request_adapter = requests.Request()


def claim():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    logger.info('IdToken: {}'.format(id_token))
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            logger.info(claims)
        except ValueError as exc:
            error_message = str(exc)
            logger.error(error_message)
    return claims


def nickname():
    if 'nickname' in session:
        logger.debug('Session[nickname]: {}'.format(session['nickname']))
        return session['nickname']
    claims = claim()
    logger.debug('claims: {}'.format(claims))
    if claims:
        session['nickname'] = _nickname_from_email(claims['email'])
        return session['nickname']
    return None


def _nickname_from_email(email):
    return email.split("@")[0]
