from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
  name = 'moorse',
  packages = [
    'moorse',
    'moorse/service',
    'moorse/service/message',
    'moorse/service/validators',
    'moorse/clients',
    'moorse/clients/message',
    'moorse/enums',
    'moorse/enums/template',
    'moorse/enums/webhook',
    'moorse/dto',
    'moorse/dto/webhook',
    'moorse/dto/webhook/response',
    'moorse/dto/template',
    'moorse/dto/template/button',
    'moorse/dto/template/component',
    'moorse/dto/template/request',
    'moorse/dto/template/response/multiple',
    'moorse/dto/template/response/single',
    'moorse/dto/reports/channel',
    'moorse/dto/reports/standard',
    'moorse/dto/reports/timeline',
    'moorse/dto/message',
    'moorse/dto/message/buttons',
    'moorse/dto/message/menu',
    'moorse/dto/message/template',
    'moorse/dto/message/template/parameter',
    'moorse/dto/message/template/parameter/file_info',
    'moorse/dto/integration',
    'moorse/dto/integration/delete',
    'moorse/dto/integration/get_all',
    'moorse/dto/integration/get_one',
    'moorse/dto/integration/get_status',
    'moorse/dto/billing',
    'moorse/dto/authorization'
  ],
  version = '1.0.4',
  license = 'MIT',
  description='A sdk that allows Moorse customers to write some simplified calls to the Moorse resources.',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author = 'Moorse.io',
  author_email = 'douglas.alv.sousa@gmail.com',
  url = 'https://moorse.io',
  keywords = ['DEVELOPMENT KIT', 'MOORSE', 'SDK'],
  install_requires = [],
  classifiers=[
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.10'
  ],
)