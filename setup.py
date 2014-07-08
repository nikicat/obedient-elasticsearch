import setuptools

if __name__ == '__main__':
    setuptools.setup(
        name='obedient.elasticsearch',
        version='0.1',
        url='https://github.com/yandex-sysmon/obedient-elasticsearch',
        license='GPLv3',
        author='Nikolay Bryskin',
        author_email='devel.niks@gmail.com',
        description='Elasticsearch obedient for Dominator',
        platforms='linux',
        packages=['obedient.elasticsearch'],
        namespace_packages=['obedient'],
        package_data={'obedient.elasticsearch': ['elasticsearch.yml', 'logging.yml', 'mapping.json', 'run.sh']},
        install_requires=['dominator >=3, <4'],
    )
