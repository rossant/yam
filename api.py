import requests
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.etree import ElementTree as ET
from six import string_types


def _build_xml(path, text=None, mode=None):
    mode = mode.upper()
    assert mode in ('GET', 'PUT')
    root = Element('YAMAHA_AV')
    root.set('cmd', mode)
    if isinstance(path, string_types):
        path = [path]
    if isinstance(text, string_types):
        text = [text]
    nodes = {}
    for p, t in zip(path, text):
        p = p.split('/')
        child = root
        cur = []
        for child_name in p:
            cur.append(child_name)
            n = '/'.join(cur)
            if n in nodes:
                child = nodes[n]
            else:
                child = SubElement(child, child_name)
                nodes[n] = child
        child.text = t
    header = '<?xml version="1.0" encoding="utf-8"?>'
    contents = tostring(root, encoding='UTF-8')
    contents = contents.decode('unicode_escape')
    return header + contents


def _get_path_xml(xml, path):
    node = ET.fromstring(xml)
    for child_name in path.split('/'):
        if node is None:
            return
        node = node.find(child_name)
    return node.text if node is not None else None


class RemoteController(object):
    _host_path = '/YamahaRemoteControl/ctrl'
    _paths = {
        'Power': 'System/Power_Control/Power',
        'Volume': ('Main_Zone/Volume/Lvl', 'Main_Zone/Volume/Lvl/Val'),
        'ModelName': ('System/Config', 'System/Config/Model_Name'),
        'Info': 'System/Service/Info',
        'Input': 'Main_Zone/Input/Input_Sel',  # SERVER

        'Config': 'SERVER/Config',
        'List_Info': 'SERVER/List_Info',
        'Play_Info': 'SERVER/Play_Info',
        'Select': 'SERVER/List_Control/Direct_Sel',
        'Cursor': 'SERVER/List_Control/Cursor',

        # 'Play/Pause/Stop/Skip Fwd/Skip Rev'
        'Playback': 'SERVER/Play_Control/Playback',

        # 'Basic': 'Main_Zone/Basic_Status',
        # 'Input_Sel_Item': 'Main_Zone/Input/Input_Sel_Item',
        # 'SERVER/List_Control/Jump_Line' 1

    }

    def __init__(self, host):
        self._host = host

    def _post_xml(self, xml):
        return requests.post(self._host + self._host_path, xml).text

    def _request(self, path, text=None, mode=None):
        if mode is None:
            mode = 'get'
        if text is None and mode == 'get':
            text = 'GetParam'
        path = self._paths.get(path, path)
        if isinstance(path, tuple):
            path, output_path = path
        else:
            output_path = path
        xml = _build_xml(path, text, mode=mode)
        xml_out = self._post_xml(xml)
        out = _get_path_xml(xml_out, output_path)
        import time
        time.sleep(.1)
        if not out:
            return xml_out
        return out

    def get(self, path, text=None):
        return self._request(path, text, mode='get')

    def put(self, path, text=None):
        return self._request(path, text, mode='put')


if __name__ == '__main__':

    c = RemoteController('http://yamaha')
    if c.get('Input') != 'SERVER':
        c.put('Input', 'SERVER')
    # print(c.put('Select', 'Line_1'))
    c.put('Cursor', 'Return to Home')
    c.put('Select', 'Line_1')
    c.put('Select', 'Line_1')
    c.put('Select', 'Line_1')
    print(c.get('List_Info'))
    # print(c.get('List_Info'))
