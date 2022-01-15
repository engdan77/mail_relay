from setuptools import setup

setup(
    name='mail_relay',
    version='0.0.2',
    packages=['tests', 'mail_relay'],
    install_requires=open('requirements.txt').read().split('\n'),
    url='https://github.com/engdan77/mail_relay',
    license='MIT',
    author='Daniel Engvall',
    author_email='daniel@engvalls.eu',
    description='A simplistic SMTP relay service for Gmail and Home Assistant',
    entry_points={
        'console_scripts': ['mail_relay = mail_relay.__main__:main']
        }
)
