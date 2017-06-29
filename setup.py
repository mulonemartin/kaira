from distutils.core import setup

setup(
    name='kaira',
    version='0.1.1',
    packages=['kaira', 'kaira.routing'],
    url='https://github.com/mulonemartin/kaira/',
    license='MIT',
    author='martin',
    author_email='mulone.martin@gmail.com',
    description='Web Microframework - Python',
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
)
