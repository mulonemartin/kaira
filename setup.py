from distutils.core import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='kaira',
    version='0.1.3',
    packages=['kaira', 'kaira.routing'],
    url='https://github.com/mulonemartin/kaira/',
    license='MIT',
    author='Martin Mulone',
    author_email='mulone.martin@gmail.com',
    description='Web Micro framework - Python',
    long_description=readme(),
    install_requires=[
              'whitenoise'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ],
    include_package_data=True,
    zip_safe=False
)
