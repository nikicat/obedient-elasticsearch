from dominator.utils import resource_string
from dominator.entities import (SourceImage, Image, DataVolume, ConfigVolume, TemplateFile,
                                TextFile, Container, LogVolume, RotatedLogFile, LocalShip,
                                Shipment, Door)
import obedient.zookeeper


def create(ships, zookeepers, name, ports=None, marvel_hosts=[]):
    ports = ports or {}
    containers = []
    image = SourceImage(
        name='elasticsearch',
        parent=Image(namespace='yandex', repository='trusty'),
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
        files={'/root/run.sh': resource_string('run.sh')},
        command='bash /root/run.sh',
    )
    config = ConfigVolume(
        dest=image.volumes['config'],
        files={
            'elasticsearch.yml': TemplateFile(
                resource_string('elasticsearch.yml'),
                name=name, zookeepers=zookeepers,
                containers=containers, marvel_hosts=marvel_hosts
            ),
            'mapping.json': TextFile('mapping.json'),
            'logging.yml': TextFile('logging.yml'),
        },
    )
    data = DataVolume(image.volumes['data'])
    logs = LogVolume(
        image.volumes['logs'],
        files={
            '{}.log'.format(name): RotatedLogFile('[%Y-%m-%d %H:%M:%S,%f]', 25)
        },
    )

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
            doors={
                'http': Door(
                    schema='http',
                    port=image.ports['http'],
                    externalport=ports.get('http'),
                    paths=[
                        '/',
                        '/_plugin/head/',
                        '/_plugin/marvel/',
                    ],
                ),
                'peer': Door(schema='elasticsearch-peer', port=image.ports['peer'],
                             externalport=ports.get('peer')),
                'jmx': Door(schema='rmi', port=image.ports['jmx'], externalport=ports.get('jxm')),
            },
            env={
                'JAVA_RMI_PORT': image.ports['jmx'],
                'JAVA_RMI_SERVER_HOSTNAME': ship.fqdn,
                'ES_HEAP_SIZE': ship.memory // 2,
                'ES_JAVA_OPTS': '-XX:NewRatio=5',
            },
            memory=ship.memory * 3 // 4,
        ) for ship in ships])
    return containers


def make_local():
    ships = [LocalShip()]
    zookeepers = obedient.zookeeper.create(ships=ships)
    containers = create(ships=ships, zookeepers=zookeepers, name='local')
    return Shipment(name='local', containers=containers)
