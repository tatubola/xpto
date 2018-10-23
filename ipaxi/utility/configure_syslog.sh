#!/usr/bin/env bash

# This script configure rsyslogd to centralize django and docker files into
# /var/log/ixapi.log file

rsyslogd_conf_dir="/etc/rsyslog.d"

cp ./22-ixapi.conf $rsyslogd_conf_dir
service rsyslog status
