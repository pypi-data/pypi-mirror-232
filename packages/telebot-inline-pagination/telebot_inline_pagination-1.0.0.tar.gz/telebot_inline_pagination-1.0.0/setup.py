from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='telebot_inline_pagination',
  version='1.0.0',
  author='kremastra',
  author_email='fotisgrek@gmail.com',
  description='Pageable inline keyboard for pyTelegramBotAPI (telebot)',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/kremastra/telebot-inline-pagination',
  packages=find_packages(),
  install_requires=['telebot'],
  classifiers=[
    'License :: OSI Approved :: MIT License'
  ]
)