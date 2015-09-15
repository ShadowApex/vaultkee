# VaultKee
VaultKee is a Qt graphical frontend for [Vault](https://www.vaultproject.io/)
that provides a KeePass-like interface to manage passwords and secrets.

![login](screenshot01.png)

![vaultkee](screenshot02.png)

![vaultkee](screenshot03.png)


# Installation
## Ubuntu
You can install VaultKee by running the following commands:

`sudo apt-get install python-qt4 python-requests`

After installing the needed dependencies, run VaultKee:

`cd vaultkee`

`./vaultkee.py`

## Mac OS X
Before installing VaultKee, ensure that you have brew installed. Then you can
perform the following steps to run VaultKee from source:

`git clone https://github.com/ShadowApex/vaultkee.git`

`brew install python`

`sudo easy_install pip`

`sudo pip install requests`

`sudo pip install keyring`

`brew install qt sip pyqt`

`cd vaultkee/vaultkee`

`python vaultkee.py`


# Distribution

## Mac OS X
`git clone https://github.com/ShadowApex/vaultkee.git`

`sudo easy_install pip`

`sudo pip install requests`

`sudo pip install keyring`

`brew install qt sip pyqt`

`cd vaultkee/vaultkee`

### cxfreeze
CX_Freeze allows you to create distributable binaries of VaultKee. You can run the following commands
to install and run CX_Freeze to create a Mac OS X binary:

`wget 'http://downloads.sourceforge.net/project/cx-freeze/4.3.1/cx_Freeze-4.3.1.tar.gz?r=http%3A%2F%2Fwww.pythonschool.net%2Fpyqt%2Fdistributing-your-application-on-mac-os-x%2F&ts=1431652406&use_mirror=colocrossing'`

`tar xvfz cx_Freeze*`

`python setup.py build`

`sudo python setup.py install`


`cd vaultkee/vaultkee`

`python setup.py bdsit_mac`
