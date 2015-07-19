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

        # 'Basic': 'Main_Zone/Basic_Status',
        # 'Input_Sel': 'Main_Zone/Input/Input_Sel',
        # 'Input_Sel_Item': 'Main_Zone/Input/Input_Sel_Item',
        # 'Config': 'SERVER/Config',
        # 'List_Info': 'SERVER/List_Info',
        # 'Play_Info': 'SERVER/Play_Info',
        # 'Config': 'System/Config',
        # 'Info': 'System/Service/Info',

        # 'Main_Zone/Input/Input_Sel' SERVER
        # 'SERVER/List_Control/Direct_Sel' Line_1
        # 'SERVER/List_Control/Jump_Line' 1
        # 'SERVER/Play_Control/Playback' Pause
        # 'SERVER/Play_Control/Playback' Play
        # 'SERVER/Play_Control/Playback' Skip Fwd
        # 'SERVER/Play_Control/Playback' Skip Rev
        # 'SERVER/Play_Control/Playback' Stop

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
        if not out:
            return xml_out
        return out

    def _get(self, path, text=None):
        return self._request(path, text, mode='get')

    def _put(self, path, text=None):
        return self._request(path, text, mode='put')


if __name__ == '__main__':

    # c = RemoteController('http://yamaha')
    # c._put('Main_Zone/Volume/Lvl/Val', '50')
    # print(c._get('Main_Zone/Volume/Lvl'))

    # for name in (
    #     'Basic',
    #     'Input_Sel',
    #     'Input_Sel_Item',
    #     'Config',
    #     'List_Info',
    #     'Play_Info',
    #     'Config',
    #     'Info',
    # ):

    #     print(name)
    #     print(c._get(name))
    #     print()
