# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vanoma_api_utils',
 'vanoma_api_utils.django',
 'vanoma_api_utils.mini_huey',
 'vanoma_api_utils.rest_framework']

package_data = \
{'': ['*']}

install_requires = \
['Faker>=9.9.1,<10.0.0',
 'PyJWT>=2.3.0,<3.0.0',
 'babel>=2.12.1,<3.0.0',
 'boto3>=1.24.89,<2.0.0',
 'dj-database-url>=0.5.0,<0.6.0',
 'django-filter>=21.1,<22.0',
 'django-storages>=1.13.1,<2.0.0',
 'django>=4.2,<5.0',
 'djangorestframework-camel-case>=1.2.0,<2.0.0',
 'djangorestframework>=3.14.0,<4.0.0',
 'drf-extra-fields>=3.4.1,<4.0.0',
 'drf-flex-fields>=1.0.2,<2.0.0',
 'huey>=2.4.5,<3.0.0',
 'mutagen>=1.46.0,<2.0.0',
 'phonenumbers>=8.12.37,<9.0.0',
 'pillow>=9.4.0,<10.0.0',
 'psycopg2>=2.9.3,<3.0.0',
 'pyhumps>=3.5.3,<4.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'requests>=2.27.1,<3.0.0',
 'sentry-sdk>=1.12.1,<2.0.0',
 'shortuuid>=1.0.9,<2.0.0']

setup_kwargs = {
    'name': 'vanoma-api-utils',
    'version': '0.120.0',
    'description': 'Python utils for vanoma APIs',
    'long_description': 'None',
    'author': 'Vanoma',
    'author_email': 'contact@vanoma.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
