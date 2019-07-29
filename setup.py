from setuptools import setup, find_packages

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aliyun-exporter',
    version='0.3.1',
    description='Alibaba Cloud CloudMonitor Prometheus exporter',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/aylei/aliyun-exporter',
    author='Aylei Wu',
    author_email='rayingecho@gmail.com',
    license='Apache 2.0',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Monitoring',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='monitoring prometheus exporter aliyun alibaba cloudmonitor',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    package_data={'aliyun_exporter': ['static/*','templates/*']},
    install_requires=[
        'prometheus-client',
        'aliyun-python-sdk-cms==6.0.13',
        'aliyun-python-sdk-core-v3==2.13.3',
        'pyyaml',
        'ratelimiter',
        'flask',
        'cachetools',
        'aliyun-python-sdk-ecs==4.16.5',
        'aliyun-python-sdk-rds==2.3.2',
        'aliyun-python-sdk-r-kvstore==2.0.5',
        'aliyun-python-sdk-slb==3.2.8',
        "aliyun-python-sdk-dds==2.0.4",
    ],
    entry_points={
        'console_scripts': [
            'aliyun-exporter=aliyun_exporter:main',
        ],
    },
)
