# connect ssh
``
chmod 400 ~/.ssh/zap_ass.pem
ssh -i ~/.ssh/zap_ass.pem ec2-user@<ip>
``

# Check system version
``
cat /etc/os-release
``

# Update system packages
``
sudo apt-get update && sudo apt-get -y upgrade
sudo reboot
``

# Install Python 3.11 build tools
``
sudo apt install python3-pip python3-dev libpq-dev nginx curl
``

# Confirm GCC version:
``
gcc --version
``

# Install Python 3.11
``
sudo apt install python3.11 python3.11-venv
``

# Install docker and postgres client
``
sudo apt install docker.io
sudo apt install docker-compose
sudo apt install postgresql-client-common
sudo apt install postgresql-client-14
``

# Configure git
* Fork the project add the ssh public key to your github account.
``
git config --global user.name "PedroS3"
git config --global user.email "dev@pedromadureira.xyz"
cd ~/.ssh
ssh-keygen -t ed25519 -C "dev@pedromadureira.xyz"
chmod  400 .ssh/ubuntu_server
chmod  400 .ssh/ubuntu_server.pub
``
* Add public key to repository's Deploy-keys
* Create .ssh/config
``
Host github-zap-ec2-hostname
	HostName github.com
	IdentityFile /home/ubuntu/.ssh/ubuntu_server
``

# Clone the project

* OBS _Don't miss the f*cking hostname_
``
git clone git@github-zap-ec2-hostname:pedromadureira000/zap_assistant.git
``

# Other configs
* Install neovim
``
sudo apt install neovim
``
* vim .bashrc
``
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
alias gup='cd zap_assistant && git pull && sudo systemctl restart gunicorn && source .venv/bin/activate && python manage.py migrate && cd .. && echo "Done"'
``

# Run Postgres and Redis container
-----------------------------------------
You must run this in the same folder where the 'docker-compose.yml' file is.

``
sudo docker-compose up -d
``

# Connect to default database and create the database that you will use
``
psql postgres://admin_zap:asdf@localhost:5432/postgres
create database zap_agent_db;
\q
``

# Initial project settings
``
cd zap_assistant
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp contrib/env-sample .env
python3.11 manage.py migrate
python3.11 manage.py createsuperuser
``

