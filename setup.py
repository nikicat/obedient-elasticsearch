import setuptools

if __name__ == '__main__':
    setuptools.setup(
        name='obedient.elasticsearch',
        version='1.4',
        url='https://github.com/yandex-sysmon/obedient.elasticsearch',
        license='LGPLv3',
        author='Nikolay Bryskin',
        author_email='devel.niks@gmail.com',
        description='Elasticsearch obedient for Dominator',
        platforms='linux',
        packages=['obedient.elasticsearch'],
        namespace_packages=['obedient'],
        package_data={'obedient.elasticsearch': ['elasticsearch.yml', 'logging.yml', 'mapping.json', 'run.sh']},
        install_requires=['dominator[full] >=7'],
    )
