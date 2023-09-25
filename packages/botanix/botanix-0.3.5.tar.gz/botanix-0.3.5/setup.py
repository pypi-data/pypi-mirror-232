from setuptools import setup, find_packages

setup(
    name='botanix',
    version='0.3.5',
    license='MIT',
    author="Ali Kheyrollahi",
    author_email='aliostad@gmail.com',
    packages=find_packages(exclude=['tests', 'samples']),
    url='https://github.com/aliostad/botanix',
    keywords='Telegram bot',
    install_requires=[
          'python-telegram-bot',
      ],

)