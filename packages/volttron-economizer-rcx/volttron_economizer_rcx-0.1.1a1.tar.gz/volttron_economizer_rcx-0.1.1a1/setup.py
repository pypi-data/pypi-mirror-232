# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['economizer', 'economizer.diagnostics']

package_data = \
{'': ['*']}

install_requires = \
['volttron>=10.0.2rc0,<11.0']

entry_points = \
{'console_scripts': ['volttron-economizer-rcx = '
                     'economizer.economizer_agent:main']}

setup_kwargs = {
    'name': 'volttron-economizer-rcx',
    'version': '0.1.1a1',
    'description': "Economizer Agent helps in the re-tuning process and addresses some of the issues associated with RCx. RCx is known to save energy consumption , but the process used is not cost-effective.  Economizer Agent and it's diagnostics allow continuous re-tuning and problem identification which can lower the costs of RCx",
    'long_description': '# Economizer RCx Agent\n\n![Eclipse VOLTTRON 10.0.4rc](https://img.shields.io/badge/Eclipse%20VOLTTRON-10.0.4rc-red.svg)\n![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)\n![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)\n[![Passing?](https://github.com/eclipse-volttron/volttron-economizer-rcx/actions/workflows/run-tests.yml/badge.svg)](https://github.com/VOLTTRON/volttron-economizer-rcx/actions/workflows/run-tests.yml)\n[![pypi version](https://img.shields.io/pypi/v/volttron-economizer-rcx.svg)](https://pypi.org/project/volttron-economizer-rcx/)\n\nEconomizer Agent helps in the re-tuning process and addresses some of the issues\nassociated with RCx. RCx is known to save energy consumption , but the process\nused is not cost-effective.  Economizer Agent and it\'s diagnostics allow continuous\nre-tuning and problem identification which can lower the costs of RCx\n\n## Requirements\n\n* python >= 3.10\n* volttron >= 10.0\n\n## Documentation\n\nMore detailed documentation can be found on [ReadTheDocs](https://eclipse-volttron.readthedocs.io/). The RST source\nof the documentation for this agent is located in the "docs" directory of this repository.\n\n## Installation\n\nBefore installing, VOLTTRON should be installed and running.  Its virtual environment should be active.\nInformation on how to install of the VOLTTRON platform can be found\n[here](https://github.com/eclipse-volttron/volttron-core).\n\nInstall and start the Economizer RCx Agent (assuming the vip identity "economizer.ahu1").\n\n```shell\n   vctl config store economizer.ahu1 config <path/to/config/file>\n   vctl install volttron-economizer-rcx --vip-identity economizer.ahu1 --tag economizer --start\n```\n\nView the status of the installed agent\n\n```shell\nvctl status\n```\n\n## Development\n\nPlease see the following for contributing guidelines [contributing](https://github.com/eclipse-volttron/volttron-core/blob/develop/CONTRIBUTING.md).\n\nPlease see the following helpful guide about [developing modular VOLTTRON agents](https://github.com/eclipse-volttron/volttron-core/blob/develop/DEVELOPING_ON_MODULAR.md)\n',
    'author': 'VOLTTRON Team',
    'author_email': 'volttron@pnnl.gov',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/eclipse-volttron/volttron-economizer-rcx',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
