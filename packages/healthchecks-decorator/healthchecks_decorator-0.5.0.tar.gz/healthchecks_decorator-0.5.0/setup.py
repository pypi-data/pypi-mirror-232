# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['healthchecks_decorator']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['healthchecks-decorator = '
                     'healthchecks_decorator.__main__:main']}

setup_kwargs = {
    'name': 'healthchecks-decorator',
    'version': '0.5.0',
    'description': 'Healthchecks Decorator',
    'long_description': 'Healthchecks Decorator\n======================\n\n|PyPI| |Status| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/healthchecks-decorator.svg\n   :target: https://pypi.org/project/healthchecks-decorator/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/healthchecks-decorator.svg\n   :target: https://pypi.org/project/healthchecks-decorator/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/healthchecks-decorator\n   :target: https://pypi.org/project/healthchecks-decorator\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/healthchecks-decorator\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/healthchecks-decorator/latest.svg?label=Read%20the%20Docs\n   :target: https://healthchecks-decorator.readthedocs.io/\n   :alt: Read the documentation at https://healthchecks-decorator.readthedocs.io/\n.. |Tests| image:: https://github.com/danidelvalle/healthchecks-decorator/workflows/Tests/badge.svg\n   :target: https://github.com/danidelvalle/healthchecks-decorator/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/danidelvalle/healthchecks-decorator/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/danidelvalle/healthchecks-decorator\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n\nA simple python decorator for `healthchecks.io`_.\n\nFeatures\n--------\n\nThe `healthchecks-decorator` library provides the following features:\n\n* 🚀 **Easy to use:** Simply decorate your function with `@healthcheck` to enable health checks.\n* ⏲️ **Execution time measurement:** Supports sending `/start` signals to measure job execution times.\n* 🔥 **Exception handling:** Automatically sends `/failure` signals when jobs produce exceptions.\n* 🤖 **Auto-provisioning:** Supports automatic provisioning of new health checks by adding `?create=1` to the ping URL.\n* 🌡️ **Diagnostics information:** Send diagnostics information to help diagnose issues.\n* 😊 **Flexible endpoint support:** Supports both SaaS and self-hosted endpoints.\n\n\nRequirements\n------------\n\n* None - just pure python 🐍.\n\n\nInstallation\n------------\n\nYou can install *Healthchecks Decorator* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install healthchecks-decorator\n\n\nUsage\n-----\n\nBasic usage\n^^^^^^^^^^^\n\n.. code:: python\n\n   from healthchecks_decorator import healthcheck\n\n   @healthcheck(url="https://hc-ping.com/<uuid1>")\n   def job():\n      """Job with a success healthcheck signal when done"""\n      pass\n\n\n   @healthcheck(url="https://hc-ping.com/<uuid2>", send_start=True)\n   def job_with_start():\n      """Send also a /start signal before starting"""\n      pass\n\n\n   @healthcheck(url="https://hc-ping.com/<uuid3>")\n   def job_with_exception():\n      """This will produce a /fail signal"""\n      raise Exception("I\'ll be propagated")\n\n\n   @healthcheck(url="https://hc-ping.com/<uuid4>", send_diagnostics=True)\n   def job_with_diagnostics():\n      """Send the returned value in the POST body.\n      The returned value must be a valid input for `urllib.parse.urlencode`.\n      Otherwise, nothing will be sent."""\n      return {"temperature": -7}\n\n\nEnvironment variables\n^^^^^^^^^^^^^^^^^^^^^\n\nIt is possible to set options through environment variables. Each option has a corresponding environment variable\ndefined by the option name in *upper snake case* with the ``HEALTHCHECK_`` prefix.\n\nFor example, setting:\n\n* ``HEALTHCHECK_URL=http://fake-hc.com/uuid``\n* ``HEALTHCHECK_SEND_DIAGNOSTICS=TRUE``\n* ``HEALTHCHECK_SEND_START=1``\n\nwill allow having the most minimalist usage:\n\n.. code:: python\n\n   @healthcheck\n   def job():\n      """Url, send_diagnostics and send_start are grabbed from environment."""\n      pass\n\n\n.. note::  Boolean options will be parsed as ``True`` if the env var is set to the word \'true\' (in any case) or \'1\'.\n   Otherwise, the option is set to ``False``.\n\n.. note::  Explicit values take precedence over environment variables.\n\nPlease see the `Documentation`_ for details.\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `MIT license`_,\n*Healthchecks Decorator* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n* `healthchecks.io`_.\n* This project was generated from `@cjolowicz`_\'s `Hypermodern Python Cookiecutter`_ template.\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _MIT license: https://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/danidelvalle/healthchecks-decorator/issues\n.. _pip: https://pip.pypa.io/\n.. _Documentation: https://healthchecks-decorator.readthedocs.io/\n.. _healthchecks.io: https://healthchecks.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n',
    'author': 'Daniel del Valle',
    'author_email': 'delvalle.dani@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/danidelvalle/healthchecks-decorator',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
