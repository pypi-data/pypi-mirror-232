"""Python Package for controlling Alexa devices (echo dot, etc) programmatically.

SPDX-License-Identifier: Apache-2.0

Constants.

For more details about this api, please refer to the documentation at
https://gitlab.com/keatontaylor/alexapy
"""

EXCEPTION_TEMPLATE = "An exception of type {0} occurred. Arguments:\n{1!r}"

CALL_VERSION = "2.2.556530.0"
APP_NAME = "Alexa Media Player"
USER_AGENT = f"AmazonWebView/Amazon Alexa/{CALL_VERSION}/iOS/16.6/iPhone"
LOCALE_KEY = {
    ".de": "de_DE",
    ".com.au": "en_AU",
    ".ca": "en_CA",
    ".co.uk": "en_GB",
    ".in": "en_IN",
    ".com": "en_US",
    ".es": "es_ES",
    ".mx": "es_MX",
    ".fr": "fr_FR",
    ".it": "it_IT",
    ".co.jp": "ja_JP",
    ".com.br": "pt_BR",
}
HTTP2_AUTHORITY = {
    "amazon.com": "bob-dispatch-prod-na.amazon.com",
    "amazon.com.br": "bob-dispatch-prod-na.amazon.com",
    "amazon.co.jp": "bob-dispatch-prod-fe.amazon.com",
    "amazon.com.au": "bob-dispatch-prod-fe.amazon.com",
}
HTTP2_DEFAULT = "bob-dispatch-prod-eu.amazon.com"
