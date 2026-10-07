"""Setup script of django-blog-zinnia"""
from setuptools import find_packages
from setuptools import setup

import zinnia

setup(
    name='django-blog-zinnia',
    version=zinnia.__version__,

    description='A clear and powerful weblog application powered with Django',
    long_description='\n'.join([open('README.rst').read(),
                                open('CHANGELOG').read()]),
    keywords='django, blog, weblog, zinnia, post, news',

    author=zinnia.__author__,
    author_email=zinnia.__email__,
    url=zinnia.__url__,

    packages=find_packages(exclude=['demo']),
    classifiers=[
        'Framework :: Django',
        'Framework :: Django :: 5.0',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries :: Python Modules'],

    license=zinnia.__license__,
    include_package_data=True,
    python_requires='>=3.12,<3.13',
    zip_safe=False,
    install_requires=['Django>=5.0.14,<5.1',
                      'beautifulsoup4>=4.15.0',
                      'django-mptt>=0.14.0',
                      ('django-tagging @ git+https://github.com/'
                       'dolphin-emu/django-tagging.git@'
                       '0d282f1203470f8d4f83bfda9a5b1edd878d52ba'),
                      'mots-vides>=2015.5.11',
                      'pillow>=10.4.0',
                      'pyparsing>=3.1.4',
                      'pytz>=2026.3.post1',
                      'regex>=2024.11.6']
)
