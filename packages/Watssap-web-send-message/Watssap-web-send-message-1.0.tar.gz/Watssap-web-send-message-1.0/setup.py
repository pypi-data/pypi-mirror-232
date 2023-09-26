from setuptools import setup, find_packages
from pathlib import Path


setup(
    name='Watssap-web-send-message',
    version=1.0,
    description='Este pacote fornece o basico para wattsap',
    long_description=Path('README.md').read_text(),
    author='Auto_Dev',
    author_email='ramonma31@gmail.com',
    keywords=['wattssap', 'mensagem', 'enviar', 'api wattssap'],
    packages=find_packages()
)
