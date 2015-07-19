import requests
from xml.dom.minidom import parse, parseString
from xml.etree.ElementTree import Element, SubElement, tostring


def _build_xml(path, text=None, mode=None):
    mode = mode.upper()
    assert mode in ('GET', 'PUT')
    root = Element('YAMAHA_AV')
    root.set('cmd', mode)
    path = path.split('/')
    child = root
    for child_name in path:
        child = SubElement(child, child_name)
    child.text = text
    header = '<?xml version="1.0" encoding="utf-8"?>'
    contents = tostring(root, encoding='UTF-8')
    contents = contents.decode('unicode_escape')
    return header + contents


class RemoteController(object):
    _host_path = '/YamahaRemoteControl/ctrl'
    _paths = {
        'Power': 'System/Power_Control/Power',
    }

    def __init__(self, host):
        self._host = host

    def _post(self, xml):
        return requests.post(self._host + self._host_path, xml).text

    def _get_xml(self, path, text='GetParam'):
        return _build_xml(path, text, mode='get')

    def _put_xml(self, path, text=None):
        return _build_xml(path, text, mode='put')

    def _get(self, path, text='GetParam'):
        path = self._paths.get(path, path)
        return self._post(self._get_xml(path, text))

    def _put(self, path, text=None):
        path = self._paths.get(path, path)
        return self._post(self._put_xml(path, text))


if __name__ == '__main__':
    c = RemoteController('http://yamaha')
    print(c._get('Power'))
