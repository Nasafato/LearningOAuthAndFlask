# Catalog Project
## Getting Up and Running
I'm assuming that you're starting from scratch. These are the steps needed to run this in a virtual machine. We'll be using **vagrant**.

So first, you'll need **vagrant** and **VirtualBox** installed.. Once that's done, we can proceed.

#### Setting up your VirtualMachine
Make a folder and `cd` into it. Then start setting up your vagrant machine. Run the following in your terminal:

```sh
vagrant init ubuntu/trusty32
```
This initializes your `VagrantFile` in the current directory. 

Now, open up the `Vagrantfile`, delete everything, and paste the following into it:

```
# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.provision "shell", path: "pg_config.sh"
  config.vm.box = "ubuntu/trusty32"
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "forwarded_port", guest: 8080, host: 8080
  config.vm.network "forwarded_port", guest: 5000, host: 5000
end
```
Create a file called `pg_config.sh` and paste the following into it:

```
apt-get -qqy update
apt-get -qqy install postgresql python-psycopg2
apt-get -qqy install python-flask python-sqlalchemy
apt-get -qqy install python-pip
apt-get -qqy install git
pip install bleach
pip install oauth2client
pip install requests
pip install httplib2
```

Now, install your virtual machine and ssh into it:

```sh
vagrant up
vagrant ssh
```

### Running the application
Insde the virtual machine, we `cd` into the `vagrant` folder, clone the repository, and then run `application.py`.

```sh
cd vagrant
git clone https://github.com/Nasafato/LearningOAuthAndFlask.git
cd LearningOAuthAndFlask
python application.py
```
You should be able to access the application on `localhost:5000`. Note that the database it is linked to is a PostgreSQL database I have hosted on Heroku (I was originally going to host this on Heroku but decided it wasn't worth the effort).

***Local Database***
You can also use the local database provided (`catalog.db`). To do this, you need to comment out this line in `application.py`:

```py
engine = create_engine(
    ('postgres://mxjecomshjznqn:Ky9M6DXhTdpW3CV2sCFlUJExht@ec2-54-83-204-159.co'
     'mpute-1.amazonaws.com:5432/d6iivi4caaqog9'))
```
and uncomment this line:

```py
# engine = create_engine('sqlite:///catalog.db')
```
With that accomplished, you should be able to use the SQLite database instead of the PostgreSQL database.


## Characteristics
JSON endpoints can be accessed in the following way:

* JSON for entire catalog - `http://localhost:5000/catalog/JSON`
* JSON for one category - `http://localhost:5000/catalog/2/JSON`
* JSON for one item - `http://localhost:5000/catalog/2/7/JSON`

Images are stored in the filesystem, inside `static/img/` - the `picture` fields for a `category` or `item` are the paths to their respective images. Images, upon upload, are saved with a generated UUID4 as their name.


