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
