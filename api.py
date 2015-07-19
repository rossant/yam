import requests
import xmltodict
# from time import sleep
from six import string_types


def _root(mode):
    return {'YAMAHA_AV': {'@cmd': mode.upper()}}


def _request(path, text=None, mode='get'):
    if mode == 'get' and text is None:
        text = 'GetParam'
    req = _root(mode)
    node = req['YAMAHA_AV']
    for el in path.split('/'):
        node[el] = {}
        node = node[el]
    if text:
        node['#text'] = text
    return req


def _get_item(mydict, path):
    mydict = mydict['YAMAHA_AV']
    for node in path.split('/'):
        mydict = mydict[node]
    return mydict


class RemoteController(object):
    _host_path = '/YamahaRemoteControl/ctrl'

    def __init__(self, host):
        self._host = host

    def _post_xml(self, xml):
        return requests.post(self._host + self._host_path, xml).text

    def post(self, obj, out_path=None, text=None, mode='get'):
        if isinstance(obj, string_types):
            obj = _request(obj, text=text, mode=mode)
        assert isinstance(obj, dict)
        xml = xmltodict.unparse(obj, pretty=True)
        print(xml)
        out = self._post_xml(xml)
        out = xmltodict.parse(out)
        if out_path:
            return _get_item(out, out_path)
        return out

    def volume(self, val=None):
        path = 'Main_Zone/Volume/Lvl'
        if val is None:
            return self.post(path, path + '/Val')
        else:
            obj = _request(path, mode='put')
            child = _get_item(obj, path)
            child['Val'] = str(val)
            child['Exp'] = '1'
            child['Unit'] = 'dB'
            return self.post(obj)

    def power(self, on=True):
        self.post('System/Power_Control/Power', text='On' if on else 'Off',
                  mode='put')

    def mute(self, on=True):
        self.post('Main_Zone/Volume/Mute', text='On' if on else 'Off',
                  mode='put')


if __name__ == '__main__':

    c = RemoteController('http://yamaha')

    # req = _root('get')

    # if c.get('Input') != 'SERVER':
        # c.put('Input', 'SERVER')

    # c.put('Cursor', 'Return to Home')
    # c.put('Select', 'Line_1')
    # c.put('Select', 'Line_1')
    # c.put('Select', 'Line_1')
    # print(c.get('List_Info'))


    # 'Info': 'System/Service/Info',
    # 'Input': 'Main_Zone/Input/Input_Sel',  # SERVER

    # 'Config': 'System/Config',
    # 'List_Info': 'SERVER/List_Info',
    # 'Play_Info': 'SERVER/Play_Info',
    # 'Select': 'SERVER/List_Control/Direct_Sel',
    # 'Cursor': 'SERVER/List_Control/Cursor',

    # # 'Play/Pause/Stop/Skip Fwd/Skip Rev'
    # 'Playback': 'SERVER/Play_Control/Playback',

    # 'Basic': 'Main_Zone/Basic_Status',
    # 'Input_Sel_Item': 'Main_Zone/Input/Input_Sel_Item',
    # 'SERVER/List_Control/Jump_Line' 1
