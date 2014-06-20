from pkg_resources import resource_string
from dominator import *

def text_file(filename):
    return TextFile(filename, resource_string(__name__, filename).decode())

def make_containers(ships, zookeepers, name):
    containers = []
    config = ConfigVolume(
        dest='/etc/elasticsearch',
        files = [
            TemplateFile(text_file('elasticsearch.yml'),
                name=name, zookeepers=zookeepers, containers=containers),
            text_file('mapping.json'),
            text_file('logging.yml'),
        ],
    )

    containers.extend([
        Container(
            name='elasticsearch',
            ship=ship,
            image=Image(repository='nikicat/elasticsearch', tag='latest'),
            volumes=[
                DataVolume(
                    dest='/var/lib/elasticsearch',
                    path='/var/lib/elasticsearch',
                ),
                config,
            ],
            ports={'http': 9200, 'peer': 9300},
            memory=ship.memory * 3 // 4,
        ) for ship in ships])
    return containers
