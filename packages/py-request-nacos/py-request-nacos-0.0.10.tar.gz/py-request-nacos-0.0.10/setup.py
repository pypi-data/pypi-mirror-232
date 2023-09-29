from setuptools import setup

setup(
    name='py-request-nacos',
    version='0.0.10',
    author='lidaning',
    author_email='453882101@qq.com',
    description='request service from nacos',
    packages=['py_request_nacos'],
    install_requires=[
        'requests',
        'numpy',
    ],
)