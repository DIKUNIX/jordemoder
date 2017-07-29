#!/bin/sh

uwsgi --ini "$(dirname "$0")/uwsgi.ini"
