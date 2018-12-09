from setuptools import setup, find_packages

setup(
    name='aliyun-exporter',
    version='0.0.1',
    description='Elasticsearch query Prometheus exporter',
    url='https://github.com/Braedon/prometheus-es-exporter',
    author='Aylei Wu',
    author_email='rayingecho@gmail.com',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Monitoring',
        'License :: OSI Approved :: Apache 2.0 License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='monitoring prometheus exporter aliyun alibaba cloudmonitor',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'prometheus-client',
        'aliyun-python-sdk-cms',
        'aliyun-python-sdk-core-v3',
        'pyyaml',
        'ratelimiter',
    ],
    entry_points={
        'console_scripts': [
            'aliyun-exporter=aliyun_exporter:main',
        ],
    },
)