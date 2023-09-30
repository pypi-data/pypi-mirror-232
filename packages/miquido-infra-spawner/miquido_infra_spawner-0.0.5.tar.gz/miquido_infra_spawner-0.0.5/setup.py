from distutils.core import setup

setup(
    name='miquido_infra_spawner',
    packages=['miquido_infra_spawner'],
    version='0.0.5',
    license='MIT',
    description='Spawning Terraform repositories',
    author='Marek',
    author_email='marek.moscichowski@miquido.com',
    keywords=['GITLAB', 'Terraform'],
    install_requires=[
        'requests',
        'python-dateutil'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
