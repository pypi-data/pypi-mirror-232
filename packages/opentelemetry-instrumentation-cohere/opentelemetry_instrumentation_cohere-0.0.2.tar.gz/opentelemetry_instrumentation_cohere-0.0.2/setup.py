# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cohere']

package_data = \
{'': ['*']}

install_requires = \
['opentelemetry-api>=1.19.0,<2.0.0',
 'opentelemetry-instrumentation>=0.40b0,<0.41',
 'opentelemetry-semantic-conventions-ai>=0.0.4,<0.0.5']

setup_kwargs = {
    'name': 'opentelemetry-instrumentation-cohere',
    'version': '0.0.2',
    'description': 'OpenTelemetry Cohere instrumentation',
    'long_description': '# opentelemetry-instrumentation-cohere\n\nProject description here.\n',
    'author': 'Gal Kleinman',
    'author_email': 'gal@traceloop.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.1,<4',
}


setup(**setup_kwargs)
