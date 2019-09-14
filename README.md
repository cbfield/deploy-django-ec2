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

Packages to install:

1. sudo apt install apache2
2. sudo apt install libapache2-mod-wsgi-py3
3. sudo apt install mysql-server

## 4. Create Filesystem

```
/webapp
	/auth
		mysql.cnf
		key.txt
	/django
		[django project]
	/site
		/logs
		/public
			/static
			/media
```

## 5. Fill In Auth Files

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

## 6. Configure MySQL and Apache

-- mysql --

```
sudo mysql_secure_installation utility
```

Make sure the mysql installation is configured right

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

-- apache (no ssl cert) --

/etc/apache2/sites-enabled/django.conf:

```
<VirtualHost *:80>

        ServerName IP_ADDRESS
        ServerAdmin MY_EMAIL_ADDRESS@gmail.com
        DocumentRoot /var/www/html

        ErrorLog /webapp/site/logs/error.log
        CustomLog /webapp/site/logs/access.log combined

        <Directory /webapp/django/PROJECT_NAME/main>
                <Files wsgi.py>
                        Require all granted
                </Files>
        </Directory>

        alias /static /webapp/site/public/static
        <Directory /webapp/site/public/static>
                Require all granted
        </Directory>

        alias /media /webapp/site/public/media
        <Directory /webapp/site/public/media>
                Require all granted
        </Directory>

        WSGIDaemonProcess webapp python-path=/webapp/django/PROJECT_NAME python-home=/webapp/venv
        WSGIProcessGroup webapp
        WSGIScriptAlias / /webapp/django/PROJECT_NAME/main/wsgi.py

</VirtualHost>

```
-- apache (with ssl cert) --

/etc/apache2/sites-enabled/django.conf:

```
<VirtualHost *:80>

        ServerName DOMAIN_NAME.com
        ServerAlias www.DOMAIN_NAME.com
        ServerAdmin MY_EMAIL_ADDRESS@gmail.com
        DocumentRoot /var/www/html

        ErrorLog /webapp/site/logs/error.log
        CustomLog /webapp/site/logs/access.log combined

        RewriteEngine on
        RewriteCond %{HTTP_HOST} ^(www\.)?DOMAIN_NAME\.com$ [OR]
        RewriteCond %{HTTPS_HOST} ^(www\.)?DOMAIN_NAME\.com$
        RewriteRule ^(.*)$ https://www.DOMAIN_NAME.com%{REQUEST_URI} [END,NE,R=permanent]
</VirtualHost>

```
/etc/apache2/sites-enabled/django-ssl.conf:

```

<VirtualHost *:443>

        ServerName DOMAIN_NAME.com
        ServerAlias www.DOMAIN_NAME.com
        ServerAdmin MY_EMAIL_ADDRESS@gmail.com
        DocumentRoot /var/www/html

        ErrorLog /webapp/site/logs/error.log
        CustomLog /webapp/site/logs/access.log combined

        <Directory /webapp/django/PROJECT_NAME/main/>
                <Files wsgi.py>
                        Require all granted
                </Files>
        </Directory>

        alias /static /webapp/site/public/static
        <Directory /webapp/site/public/static>
                Require all granted
        </Directory>

        alias /media /webapp/site/public/media
        <Directory /webapp/site/public/media>
                Require all granted
        </Directory>

        WSGIDaemonProcess webapp python-path=/webapp/django/PROJECT_NAME python-home=/webapp/venv
        WSGIProcessGroup webapp
        WSGIScriptAlias / /webapp/django/PROJECT_NAME/jkd/wsgi.py


Include /etc/letsencrypt/options-ssl-apache.conf
SSLCertificateFile /etc/letsencrypt/live/DOMAIN_NAME.com/fullchain.pem
SSLCertificateKeyFile /etc/letsencrypt/live/DOMAIN_NAME.com/privkey.pem
</VirtualHost>

```
## 7. Certbot

### Installation

```
sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository universe
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update

sudo apt-get install certbot python-certbot-apache
sudo certbot --apache
sudo certbot certonly --apache
```
### Certbot Crontab

words
