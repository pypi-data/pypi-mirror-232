# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['netbox_cluster',
 'netbox_cluster.api',
 'netbox_cluster.migrations',
 'netbox_cluster.models',
 'netbox_cluster.tests']

package_data = \
{'': ['*']}

install_requires = \
['bleach==6.0.0',
 'boto3==1.28.26',
 'django-cors-headers==4.2.0',
 'django-debug-toolbar==4.2.0',
 'django-filter==23.2',
 'django-graphiql-debug-toolbar==0.2.0',
 'django-mptt==0.14',
 'django-pglocks==1.0.4',
 'django-prometheus==2.3.1',
 'django-redis==5.3.0',
 'django-rich==1.7.0',
 'django-rq==2.8.1',
 'django-tables2==2.6.0',
 'django-taggit==4.0.0',
 'django-timezone-field==6.0',
 'django==4.2.5',
 'djangorestframework==3.14.0',
 'drf-spectacular-sidecar==2023.9.1',
 'drf-spectacular==0.26.4',
 'dulwich==0.21.5',
 'feedparser==6.0.10',
 'graphene-django==3.0.0',
 'gunicorn==21.2.0',
 'jinja2==3.1.2',
 'markdown==3.3.7',
 'netaddr==0.8.0',
 'pillow==10.0.0',
 'psycopg[binary,pool]==3.1.10',
 'pyyaml==6.0.1',
 'sentry-sdk==1.30.0',
 'social-auth-app-django==5.3.0',
 'social-auth-core[openidconnect]==4.4.2',
 'svgwrite==1.4.3',
 'tablib==3.5.0',
 'tzdata==2023.3']

setup_kwargs = {
    'name': 'netbox-cluster',
    'version': '0.1.1',
    'description': '',
    'long_description': '# netbox-clusters\n\nA netbox plugin for managing multiple cluster types by site\n\nTODO: Write plugin documentation, the outline here is provided as a guide and should be expanded upon.  If more detail is required you are encouraged to expand on the table of contents (TOC) in `mkdocs.yml` to add additional pages.\n',
    'author': 'Pat McLean',
    'author_email': 'patrick.mclean@sap.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
