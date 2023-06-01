# connect ssh
```
chmod 400 ~/.ssh/zap_ass.pem
ssh -i ~/.ssh/zap_ass.pem ec2-user@<ip>
```

# Check system version
```
cat /etc/os-release
```

# Update system packages
```
yum check-update
sudo yum makecache (Update the package manager's cache by running the following command:)
sudo yum update
<!-- sudo yum -y update -->
sudo systemctl reboot
```

# Install Python 3.11 build tools
```
sudo yum -y install epel-release  XXX Did not work
sudo yum install wget make cmake gcc bzip2-devel libffi-devel zlib-devel
sudo yum -y groupinstall "Development Tools"
```

# Confirm GCC version:
```
gcc --version
```

# Install OpenSSL 1.1
```
yum install openssl-devel -y
```

# Install Python 3.11
```
wget https://www.python.org/ftp/python/3.11.2/Python-3.11.2.tgz
tar xvf Python-3.11.2.tgz
cd Python-3.11*/
```
1. configure the build
```
LDFLAGS="${LDFLAGS} -Wl,-rpath=/usr/local/openssl/lib" ./configure --with-openssl=/usr/local/openssl 
./configure --enable-optimizations --with-ssl (--with-ssl is needed?)
make (lead to `could not build ssl module openssl 1.1.0 or newer error`)
```
2. install
```
sudo make altinstall
```
3. Check it
```
python3.11 --version
python3.11
>>> import ssl
>>> ssl.OPENSSL_VERSION
>>> exit()
pip3.11 --version
```

# Update pip
```
pip3.11 install --upgrade pip
```

# Now use PIP to install any module
```
sudo pip3.11 install <module-name>
```

# Install docker and postgres client
```
sudo yum install docker
```
* docker-compose
```
sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)"  -o /usr/local/bin/docker-compose
sudo mv /usr/local/bin/docker-compose /usr/bin/docker-compose
sudo chmod +x /usr/bin/docker-compose
```
* Install postgres
```
sudo yum install postgresql15
```

# Configure git
```
git config --global user.name "PedroS3"
git config --global user.email "dev@pedromadureira.xyz"
cd ~/.ssh
ssh-keygen -t ed25519 -C "dev@pedromadureira.xyz"
chmod  400 .ssh/git_deploy_key
chmod  400 .ssh/git_deploy_key.pub
```
* Add public key to repository's Deploy-keys
* .ssh/config
```
Host github-zap-ec2
	HostName github.com
	IdentityFile /home/ec2-user/.ssh/git_deploy_key
```

# clone repository
```
git clone git@github-zap-ec2:pedromadureira000/zap_assistant.git
```

# Nginx
```
sudo yum nginx
```

# Other configs
* enable epel
```
$ wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
$ sudo rpm -ihv --nodeps ./epel-release-latest-8.noarch.rpm
sudo yum -y install epel-release
```
* Install neovim
```
curl -o /etc/yum.repos.d/dperson-neovim-epel-7.repo https://copr.fedorainfracloud.org/coprs/dperson/neovim/repo/epel-7/dperson-neovim-epel-7.repo 
sudo yum -y install neovim
```
* Install other packages
```
sudo yum install curl --skip-broken
```
* copy .bashrc configs
```
# Aliases
alias vim='nvim'
alias la='ls -A'
alias du='du -h --max-depth=1'
alias grep='grep --color=auto'
alias ..='cd ..'
alias gc='git commit -m'
alias gC='git checkout'
alias gp='git push'
alias ga='git add'
alias gs='git status'
alias gd='git diff'
alias gl='git log --graph --abbrev-commit'
alias gb='git branch'
alias journal='journalctl -e'
alias used_space='sudo du -h --max-depth=1 | sort -h'
```

# Run Postgres
* You must run this in the same folder where the 'docker-compose.yml' file is.
```
sudo docker-compose up -d
```

# Connect to default database and create the database that you will use
```
psql postgres://admin_zap:asdf@localhost:5432/postgres
postgres=# create database zap_ass_db;
postgres=# \q
```

# Initial project settings
```
cd zap_assistant
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp contrib/env-sample .env
python3.11 manage.py migrate
python3.11 manage.py createsuperuser
```

<!-- # Nginx configuration -->
<!-- * Install pytohn 3.6 -->
<!-- ``` -->
<!-- sudo curl https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tgz -O -->
<!-- tar -xvf Python-3.6.1.tgz -->
<!-- cd Python-3.6.1 -->
<!-- sudo ./configure --enable-optimizations -->
<!-- sudo make install -->
<!-- ``` -->
<!-- * install supervisor -->
<!-- ``` -->
<!-- sudo yum -y install supervisor --skip-broken -->
<!-- supervisorctl -->
<!-- ``` -->

Create systemd socket for Gunicorn
-----------------------------------------

* Create the file with:

```
sudo vim /etc/systemd/system/gunicorn.socket
```

* Then copy this to that file

```
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

Create systemd service for Gunicorn
-----------------------------------------

* Create the file with:

```
sudo vim /etc/systemd/system/gunicorn.service
```

* Then copy this to that file and edit the user field and working directory path

```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/zap_assistant
ExecStart=/home/ec2-user/zap_assistant/.venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock ai_experiment.wsgi:application

[Install]
WantedBy=multi-user.target
```

Start and enable the Gunicorn socket
-----------------------------------------

```
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
sudo systemctl status gunicorn.socket
```

Check the Gunicorn socket’s logs 
-----------------------------------------

```
sudo journalctl -u gunicorn.socket
```

Test socket activation
-----------------------------------------

It will be dead. The gunicorn.service will not be active yet since the socket has not yet received any connections

```
sudo systemctl status gunicorn  
```

Test the socket activation
-----------------------------------------

It must return a html response

```
curl --unix-socket /run/gunicorn.sock localhost 
```

If you don't receive a html, check the logs. Check your /etc/systemd/system/gunicorn.service file for problems. If you make changes to the /etc/systemd/system/gunicorn.service file, reload the daemon to reread the service definition and restart the Gunicorn process:
-----------------------------------------

```
sudo journalctl -u gunicorn
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
```

Configure Nginx to Proxy Pass to Gunicorn
-----------------------------------------

* Create the file

```
sudo nvim /etc/nginx/conf.d/file_name.conf
<!-- sudo nvim /etc/nginx/conf.d/sameple.com.conf -->
```

* Paste the nginx configuration code, and edit the sever name with your server IP.

```
server {
        listen 80;
        # Above is the server IP
        server_name <your server ip>;

        location = /favicon.ico { access_log off; log_not_found off; }

        location /static/ {
            root /home/ec2-user/zap_assistant/staticfiles;
        }

        location / {
                # Bellow, the proxy_params
                proxy_set_header Host $http_host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
                proxy_pass http://unix:/run/gunicorn.sock;
        }

        location /static/ {
		    autoindex on;
		    alias /home/ec2-user/zap_assistant/staticfiles/;
	    }
}
```

collectstatic
-----------------------------------------
```
manage.py collectstatic
```

Nginx serve static file and got 403 forbidden Problem
-----------------------------------------
* add permission (first try)
```
sudo chown -R :nginx /home/ec2-user/zap_assistant/staticfiles
```
* add permission (second try)
```
sudo usermod -a -G ec2-user nginx  # (adds the user "nginx" to the "ec2-user" group without removing them from their existing groups)
chmod 710 /home/ec2-user 
```

Test for syntax errors
-----------------------------------------

```
sudo nginx -t
```

Restart nginx
-----------------------------------------

```
sudo systemctl restart nginx
sudo systemctl reload nginx
sudo systemctl status nginx
```

Solving common errors
----------------------------------------
* Securit group
 - Add port 80 there
* ALLOWED_HOSTS (better set '\*' )
* Nginx Is Displaying a 502 Bad Gateway Error Instead of the Django Application
  - A 502 error indicates that Nginx is unable to successfully proxy the request. A wide range of configuration problems express themselves with a 502 error, so more information is required to troubleshoot properly.
  - The primary place to look for more information is in Nginx’s error logs. Generally, this will tell you what conditions caused problems during the proxying event. Follow the Nginx error logs by typing:
  ```
  sudo tail -F /var/log/nginx/error.log
  ```

Run celery
-----------------------------------------
* Just run it manualy
```
celery -A ai_experiment worker -l INFO --pool=gevent --concurrency=8 --hostname=worker -E --queues=send_completion_to_user &
```
