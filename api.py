import requests
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.etree import ElementTree as ET


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


def _get_path_xml(xml, path):
    node = ET.fromstring(xml)
    for child_name in path.split('/'):
        node = node.find(child_name)
    return node.text


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
        out = self._post_xml(xml)
        if output_path:
            return _get_path_xml(out, output_path)
        return out

    def _get(self, path, text=None):
        return self._request(path, text, mode='get')

    def _put(self, path, text=None):
        return self._request(path, text, mode='put')


"""Responses.


<YAMAHA_AV rsp="GET" RC="0"><System><Power_Control><Power>On</Power></Power_Control></System></YAMAHA_AV>

<YAMAHA_AV rsp="GET" RC="0"><Main_Zone><Volume><Lvl><Val>46</Val><Exp>0</Exp><Unit></Unit></Lvl></Volume></Main_Zone></YAMAHA_AV>

"""


if __name__ == '__main__':
    c = RemoteController('http://yamaha')
    print(c._get('Volume'))

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
