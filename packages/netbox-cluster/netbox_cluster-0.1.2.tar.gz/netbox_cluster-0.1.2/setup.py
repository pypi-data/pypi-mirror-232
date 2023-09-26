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
    'version': '0.1.2',
    'description': '',
    'long_description': '# netbox-clusters\n\nA netbox plugin for managing multiple cluster types by site\n\n## Installing the Plugin in Netbox\n\n### Prerequisites\n\n- The plugin is compatible with Netbox 3.5.0 and higher.\n- Databases supported: PostgreSQL\n\n### Install Guide\n\n!!! note\n    Plugins can be installed manually or using Python\'s `pip`. See the [netbox documentation](https://docs.netbox.dev/en/stable/plugins/) for more details. The pip package name for this plugin is [`netbox_cluster`](https://pypi.org/project/netbox_cluster/).\n\nThe plugin is available as a Python package via PyPI and can be installed with `pip`:\n\n```shell\npip install netbox-clusters\n```\n\nTo ensure the device cluster plugin is automatically re-installed during future upgrades, create a file named `local_requirements.txt` (if not already existing) in the Netbox root directory (alongside `requirements.txt`) and list the `netbox_cluster` package:\n\n```shell\necho netbox-clusters >> local_requirements.txt\n```\n\nOnce installed, the plugin needs to be enabled in your Netbox configuration. The following block of code below shows the additional configuration required to be added to your `$NETBOX_ROOT/netbox/configuration.py` file:\n\n- Append `"netbox_cluster"` to the `PLUGINS` list.\n- Append the `"netbox_cluster"` dictionary to the `PLUGINS_CONFIG` dictionary and override any defaults.\n\n```python\nPLUGINS = [\n    "netbox_cluster",\n]\n```\n\n## Post Install Steps\n\nOnce the Netbox configuration is updated, run the post install steps from the _Netbox Home_ to run migrations and clear any cache:\n\n```shell\n# Apply any database migrations\npython3 netbox/manage.py migrate\n# Trace any missing cable paths (not typically needed)\npython3 netbox/manage.py trace_paths --no-input\n# Collect static files\npython3 netbox/manage.py collectstatic --no-input\n# Delete any stale content types\npython3 netbox/manage.py remove_stale_contenttypes --no-input\n# Rebuild the search cache (lazily)\npython3 netbox/manage.py reindex --lazy\n# Delete any expired user sessions\npython3 netbox/manage.py clearsessions\n# Clear the cache\npython3 netbox/manage.py clearcache\n```\n\nThen restart the Netbox services:\n\n```shell\nsudo systemctl restart netbox netbox-rq\n```\n',
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
