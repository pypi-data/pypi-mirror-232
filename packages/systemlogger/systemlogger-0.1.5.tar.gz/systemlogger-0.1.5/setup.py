# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['systemlogger']

package_data = \
{'': ['*']}

install_requires = \
['python-logging-loki>=0.3.1,<0.4.0', 'sentry-sdk>=1.18.0,<2.0.0']

setup_kwargs = {
    'name': 'systemlogger',
    'version': '0.1.5',
    'description': 'Create and configure a logger using a global configuration file.',
    'long_description': 'SystemLogger\n============\n\n\n..image:: https://pyup.io/repos/github/d9pouces/SystemLogger/shield.svg\n:target: https://pyup.io/repos/github/d9pouces/SystemLogger/\n:alt: Updates\n\nCreate and configure a logger using a global configuration file.\nThis module is intended for logging my Python system scripts, without redeclaring a lot of boilerplate.\nThis module is not meant to be highly customizable, but to have the same logging configuration in scripts with a\nminimal effort.\n\nThe default configuration file is `/etc/python_logging.ini`.\n\nUsage\n-----\n\n```bash\npython3 -m pip install systemlogger\ncat << EOF | sudo tee /etc/python_logging.ini\n[logging]\nsentry_dsn = https://username@sentry.example.com/1\nloki_url = https://username:password@localhost:3100/loki/api/v1/push\nsyslog_url = tcp://127.0.0.1:10514\n# only udp:// and tcp:// protocols can be used for syslog\nlogfile_directory = /tmp\n# the filename will be /tmp/{application}.log\nlogfile_max_size = 1000000\n# if max_size is not set (or is 0), the file will never be rotated\nlogfile_backup_count = 3\n# number of backup files (for example, only /tmp/{application}.log.1 is created if logfile_backup_count == 1)\nconsole = true\n# errors and above are sent to stderr, infos and below are sent to stdout\nlevel = info\n# minimal level of transmitted log records\nsource = python\n# added as "log_source" tag in sentry and loki\nEOF\npython3 -c \'from systemlogger import getLogger ; logger = getLogger(name="demo") ; logger.warning("log warning test") ; logger.error("log error test")\'\n```\n\nIn Grafana/Loki and in Sentry, you can now select all Python scripts with the `log_source` tag and a specific script\nwith\nthe `application` tag.\n',
    'author': 'Matthieu Gallet',
    'author_email': 'github@19pouces.net',
    'maintainer': 'Matthieu Gallet',
    'maintainer_email': 'github@19pouces.net',
    'url': 'https://github.com/d9pouces/SystemLogger',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
