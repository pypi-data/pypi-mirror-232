from setuptools import find_packages, setup

from aldryn_people import __version__


REQUIREMENTS = [
    'djangocms-aldryn-common',
    'djangocms-aldryn-translation-tools',
    'djangocms-aldryn-search',
    'django-filer',
    'easy-thumbnails[svg]',
    'phonenumbers',
]

# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Framework :: Django :: 3.2',
    'Framework :: Django :: 4.0',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]

setup(
    name='djangocms-aldryn-people',
    version=__version__,
    description='Aldryn People publishes profile pages for people in your '
                'organisation including team members, collaborators, '
                'partners, clients, and so on, including photographs and '
                'address information.',
    author='Divio AG',
    author_email='info@divio.ch',
    url='https://github.com/CZ-NIC/djangocms-aldryn-people',
    packages=find_packages(),
    license='BSD',
    platforms=['OS Independent'],
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.7',
    test_suite="test_settings.run",
)
