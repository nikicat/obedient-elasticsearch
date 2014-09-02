from dominator.entities import SourceImage, Image, DataVolume, ConfigVolume, TemplateFile, TextFile, Container


def create(ships, zookeepers, name, httpport=9200, peerport=9300, jmxport=9400, marvel_hosts=[]):
    containers = []
    image = SourceImage(
        name='elasticsearch',
        parent=Image('yandex/trusty'),
        scripts=[
            'curl http://packages.elasticsearch.org/GPG-KEY-elasticsearch | apt-key add -',
            'echo "deb http://packages.elasticsearch.org/elasticsearch/1.2/debian stable main"'
            ' > /etc/apt/sources.list.d/elasticsearch.list',
            'apt-get update',
            'apt-get install -y --no-install-recommends maven elasticsearch=1.2.1 openjdk-7-jdk',
            'git clone https://github.com/grmblfrz/elasticsearch-zookeeper.git /tmp/elasticsearch-zookeeper',
            'cd /tmp/elasticsearch-zookeeper && git checkout v1.2.0 && '
            'mvn package -Dmaven.test.skip=true -Dzookeeper.version=3.4.6',
            '/usr/share/elasticsearch/bin/plugin -v '
            '  -u file:///tmp/elasticsearch-zookeeper/target/releases/elasticsearch-zookeeper-1.2.0.zip '
            '  -i elasticsearch-zookeeper-1.2.0',
            '/usr/share/elasticsearch/bin/plugin -v -i elasticsearch/marvel/latest',
            '/usr/share/elasticsearch/bin/plugin -v -i mobz/elasticsearch-head',
        ],
        ports={'http': 9200, 'peer': 9300, 'jmx': 9400},
        volumes={
            'logs': '/var/log/elasticsearch',
            'data': '/var/lib/elasticsearch',
            'config': '/etc/elasticsearch'
        },
        files={'/root/run.sh': 'run.sh'},
        command='bash /root/run.sh',
    )
    config = ConfigVolume(
        dest=image.volumes['config'],
        files={
            'elasticsearch.yml': TemplateFile(
                TextFile('elasticsearch.yml'),
                name=name, zookeepers=zookeepers,
                containers=containers, marvel_hosts=marvel_hosts
            ),
            'mapping.json': TextFile('mapping.json'),
            'logging.yml': TextFile('logging.yml'),
        },
    )
    data = DataVolume(image.volumes['data'])
    logs = DataVolume(image.volumes['logs'])

    containers.extend([
        Container(
            name='elasticsearch',
            ship=ship,
            image=image,
            volumes={
                'data': data,
                'logs': logs,
                'config': config,
            },
            ports=image.ports,
            extports={'http': httpport, 'peer': peerport, 'jmx': jmxport},
            env={
                'JAVA_RMI_PORT': image.ports['jmx'],
                'JAVA_RMI_SERVER_HOSTNAME': ship.fqdn,
                'ES_HEAP_SIZE': ship.memory // 2,
                'ES_JAVA_OPTS': '-XX:NewRatio=5',
            },
            memory=ship.memory * 3 // 4,
        ) for ship in ships])
    return containers
