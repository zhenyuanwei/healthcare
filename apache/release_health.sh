#!/bin/sh
cd /var/www/Health
git reset --hard FETCH_HEAD
git clean -f -d
git pull healthcare master
service apache2 restart
