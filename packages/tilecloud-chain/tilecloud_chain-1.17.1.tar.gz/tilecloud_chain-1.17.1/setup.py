# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tilecloud_chain', 'tilecloud_chain.tests', 'tilecloud_chain.views']

package_data = \
{'': ['*'],
 'tilecloud_chain': ['static/*', 'templates/*'],
 'tilecloud_chain.tests': ['mapfile/*',
                           'tilegeneration/*',
                           'tilegeneration/hooks/*']}

install_requires = \
['Jinja2',
 'PyYAML',
 'Shapely',
 'azure-storage-blob',
 'c2cwsgiutils[broadcast,standard]',
 'certifi',
 'jsonschema',
 'jsonschema-gentypes',
 'pyramid',
 'pyramid-mako',
 'python-dateutil',
 'tilecloud[aws,azure,redis,wsgi]',
 'waitress']

entry_points = \
{'console_scripts': ['generate-controller = tilecloud_chain.controller:main',
                     'generate-copy = tilecloud_chain.copy_:main',
                     'generate-cost = tilecloud_chain.cost:main',
                     'generate-process = tilecloud_chain.copy_:process',
                     'generate-tiles = tilecloud_chain.generate:main',
                     'import-expiretiles = tilecloud_chain.expiretiles:main'],
 'paste.app_factory': ['main = tilecloud_chain.server:main'],
 'pyramid.scaffold': ['tilecloud_chain = tilecloud_chain.scaffolds:Create']}

setup_kwargs = {
    'name': 'tilecloud-chain',
    'version': '1.17.1',
    'description': 'Tools to generate tiles from WMS or Mapnik, to S3, Berkeley DB, MBTiles, or local filesystem in WMTS layout using Amazon cloud services.',
    'long_description': '# TileCloud Chain\n\nThe goal of TileCloud Chain is to provide tools around tile generation on a chain like:\n\nSource: WMS, Mapnik.\n\nOptionally using an SQS queue, AWS host, SNS topic.\n\nDestination in WMTS layout, on S3, on Berkeley DB (`bsddb`), on MBTiles, or on local filesystem.\n\nFeatures:\n\n- Generate tiles.\n- Drop empty tiles.\n- Drop tiles outside a geometry or a bbox.\n- Use MetaTiles.\n- Generate the legend images.\n- Generate GetCapabilities.\n- Generate OpenLayers example page.\n- Obtain the hash of an empty tile.\n- In the future, measure tile generation speed.\n- Calculate cost and generation time.\n- In the future, manage the AWS hosts that generate tiles.\n- Delete empty tiles.\n- Copy files between caches.\n- Be able to use an SQS queue to dispatch the generation.\n- Post processing the generated tiles.\n- ...\n\nLegacy features:\n\n- bsddb support\n- sqlite (mbtiles) support\n- mapnik support (should be updated for Python3)\n\n## Get it\n\nCreate the config file `tilegeneration/config.yaml` see as [example](https://github.com/camptocamp/tilecloud-chain/blob/master/example/tilegeneration/config.yaml).\n\n### Support\n\nOnly the latest release is supported and version &lt; 1.11 contains security issues.\n\n## From sources\n\nBuild it:\n\n```bash\ngit submodule update --recursive\npython3 -m venv .build/venv\n.build/venv/bin/pip install -r requirements.txt\n.build/venv/bin/pip install -e .\n.build/venv/bin/pip install -r dev-requirements.txt\n```\n\n## Run prospector\n\n```bash\n.build/venv/bin/prospector\n```\n\n## Run the tests\n\nSetup your environment:\n\n```bash\ntouch tilecloud_chain/OpenLayers.js\ndocker build --tag camptocamp/tilecloud-chain .\ndocker-compose -p tilecloud up\n```\n\nTo run the tests:\n\n```bash\ndocker-compose -p tilecloud exec test python setup.py nosetests --logging-filter=tilecloud,tilecloud_chain --attr \'!\'nopy3\n```\n\n## Documentation\n\nAs documentation you can read the `https://github.com/camptocamp/tilecloud-chain/blob/master/tilecloud_chain/USAGE.rst`.\n\n## VSCode\n\nYou can add that in your workspace configuration to use the JSON schema:\n\n```json\n{\n  "yaml.schemas": {\n    "../tilecloud-chain/tilecloud_chain/schema.json": [\n      "tilecloud-chain/tilecloud_chain/tests/tilegeneration/*.yaml"\n    ]\n  }\n}\n```\n',
    'author': 'Camptocamp',
    'author_email': 'info@camptocamp.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/camptocamp/tilecloud-chain',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
