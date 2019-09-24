# EC2 Web Application Deployment Playbook

This document (work in progress) is meant to be a documentation of the full process of deploying an application to an ec2 node on AWS

## 1. Deploy The Server

Later this will include some indication of how to do this programmatically, with the expectation that it will eventually be automated.

For now, just deploy a new ubuntu 18.04 instance

## 2. Update

```
sudo apt update && sudo apt upgrade
```

## 3. Install Things
```
sudo apt install build-essential python3-dev python3-pip mysql-server virtualenv virtualenvwrapper nginx
sudo pip3 install uwsgi
```

## 4. Environment Variables For VirtualenvWrapper
```
echo "export WORKON_HOME=~/Env" >> ~/.bashrc
echo "source /usr/share/virtualenvwrapper/virtualenvwrapper.sh" >> ~/.bashrc
source /home/ubuntu/.bashrc
```

## 5. Create Filesystem

```
/home/ubuntu/
	/django/
	/auth/
		key.txt (for django secret key)
		mysql.cnf
	/public/
		/static/
		/media/
```

## 6. Setup Django Project

```
cd /home/ubuntu/django && git clone https://github.com/cbfield/DJANGO_PROJECT_NAME
cd /home/ubuntu && mkvirtualenv django --python=/usr/bin/python3
cd /home/ubuntu/django/DJANGO_PROJECT_NAME && pip install -r requirements.txt
```
Make sure the mysql installation is configured right (for Django, which has bad config for some reason)

```
In:

venv/lib/python3.*/site-packages/django/db/backends/mysql/base.py

replace:

if version < (1, 3, 13):
	raise ImproperlyConfigured('mysqlclient 1.3.13 or newer is required; you have %s.'

with:

if version < (1, 3, 13):
	pass

```

```

In:

venv/lib/python3.*/site-packages/django/db/backends/mysql/operations.py

replace:

query = query.decode(errors='replace')

with:

query = query.encode(errors='replace')

```

```
cd /home/ubuntu/django/DJANGO_PROJECT_NAME && python manage.py collectstatic
```
## 7. Fill In Auth Files

-- mysql.cnf --
```
[client]
database='DATABASE_NAME'
user='USERNAME'
password='PASSWORD'
default-character-set='utf8'
```

-- key.txt --
```
[random 50 character string]
```

## 8. MySQL Setup
```
sudo mysql_secure_installation
mysql
	>create database django_database_name;
	>grant all privileges on *.* to 'django_user'@'localhost' identified by 'django_user_password';
	>flush privileges;
```

## 9. Configure uWSGI

/etc/uwsgi/sites/django.ini:
```
[uwsgi]
project = DJANGO_PROJECT_NAME
base = /home/ubuntu

chdir = %(base)/django/%(project)
home = %(base)/Env/django
module = main.wsgi:application

master = true
processes = 2

socket = %(base)/Env/django/%(project).sock
chmod-socket = 666
vacuum = true
```

/etc/systemd/system/uwsgi.service:
```
[Unit]
Description=uWSGI Emperor service
After=syslog.target

[Service]
ExecStart=/usr/local/bin/uwsgi --emperor /etc/uwsgi/sites
Restart=always
KillSignal=SIGQUIT
Type=notify
StandardError=syslog
NotifyAccess=all

[Install]
WantedBy=multi-user.target
```
```
sudo systemctl daemon-reload
sudo systemctl start uwsgi
```

## 10. Configure Nginx

```
cd /etc/nginx/sites-available && sudo rm default
```

/etc/nginx/sites-available:

```
server {
    listen 80;
    server_name www.bucketmeadow.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/ubuntu/django/DJANGO_PROJECT_NAME;
    }

    location / {
        include         uwsgi_params;
        uwsgi_pass      unix:/home/ubuntu/Env/django/DJANGO_PROJECT_NAME.sock;
    }
}

server {
    listen 80;
    listen 443 ssl;
    server_name bucketmeadow.com;
    return 301 https://www.bucketmeadow.com$request_uri;
}
```
```
sudo ln -s /etc/nginx/sites-available/sample /etc/nginx/sites-enabled
nginx -t (to test config)
sudo systemctl restart nginx
```

## 11. Certbot

#### Installation

```
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo add-apt-repository ppa:certbot/certbot
sudo apt update

sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx
```
#### Crontab

You won't want to have to manually renew the SSL certificate every time it expires, so you should set up a cronjob to do that for you.
