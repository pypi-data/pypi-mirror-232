import platform
import os
from setuptools import setup, find_packages

path_to_my_project = os.path.dirname(__file__)  # Do any sort of fancy resolving of the path here if you need to

install_requires = [
    'pytz'
]
packages = find_packages(exclude=['tests'])

setup(name='ceotr_sensor_tracker_proxy',
      version='1.0.1',
      description="Common Python",
      author="CEOTR",
      author_email="support@ceotr.ca",
      url="https://gitlab.oceantrack.org/ceotr-public/ceotr_app_common/ceotr_notifications",
      packages=packages,
      include_package_data=True,
      license="GNU General Public License v3 (GPLv3)",
      install_requires=install_requires,
      zip_safe=True
      )
