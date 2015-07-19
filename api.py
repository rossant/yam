import requests
import xmltodict
import math
from pprint import pprint
from time import sleep
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
        node['#text'] = str(text)
    return req


def _get_item(mydict, path):
    mydict = mydict.get('YAMAHA_AV', mydict)
    for node in path.split('/'):
        mydict = mydict[node]
    return mydict


def pause():
    sleep(.25)


class RemoteController(object):
    _host_path = '/YamahaRemoteControl/ctrl'

    def __init__(self, host):
        self._host = host

    def _post_xml(self, xml):
        return requests.post(self._host + self._host_path, xml).text

    def post(self, obj, text=None, out_path=None, mode='get'):
        if isinstance(obj, string_types):
            obj = _request(obj, text=text, mode=mode)
        assert isinstance(obj, dict)
        xml = xmltodict.unparse(obj, pretty=True)
        out = self._post_xml(xml)
        out = xmltodict.parse(out)
        if out_path:
            return _get_item(out, out_path)
        return out

    def get(self, obj, text=None, out_path=None):
        return self.post(obj, text=text, out_path=out_path or obj, mode='get')

    def put(self, obj, text=None, out_path=None):
        return self.post(obj, text=text, out_path=out_path, mode='put')

    def volume(self, val=None):
        path = 'Main_Zone/Volume/Lvl'
        if val is None:
            return self.get(path, out_path=path + '/Val')
        else:
            obj = _request(path, mode='put')
            child = _get_item(obj, path)
            child['Val'] = str(val)
            child['Exp'] = '1'
            child['Unit'] = 'dB'
            return self.post(obj)

    def power(self, on=None):
        if on is None:
            return self.get('System/Power_Control/Power')
        self.put('System/Power_Control/Power', 'On' if on else 'Off')

    def mute(self, on=None):
        if on is None:
            return self.get('Main_Zone/Volume/Mute')
        self.put('Main_Zone/Volume/Mute', 'On' if on else 'Off')

    def input(self, input=None):
        if input is None:
            return self.get('Main_Zone/Input/Input_Sel').lower()
        self.put('Main_Zone/Input/Input_Sel', input.upper())

    def server(self):
        if c.input() != 'server':
            c.input('server')

    def optical(self):
        if c.input() != 'optical':
            c.input('optical')

    def current(self):
        return self.get('SERVER/Play_Info')

    def select(self, idx=0):
        self.put('SERVER/List_Control/Direct_Sel', 'Line_{}'.format(idx + 1))

    def jump(self, idx=0):
        self.put('SERVER/List_Control/Jump_Line', 'Line_{}'.format(idx + 1))

    def cursor(self, cursor):
        self.put('SERVER/List_Control/Cursor', cursor)

    def page(self, dir):
        self.put('SERVER/List_Control/Page', dir.title())

    def page_up(self):
        self.page('up')

    def page_down(self):
        self.page('down')

    def _list(self):
        items = self.get('SERVER/List_Info')
        pause()
        return items

    def list(self):
        k = 8
        items = self._list()
        max_line = int(_get_item(items, 'Cursor_Position/Max_Line'))
        n_pages = math.ceil(max_line / float(k))
        l = []
        for page in range(n_pages):
            if page >= 1:
                self.page_down()
                pause()
                items = self._list()
            for i in range(k):
                l.append(_get_item(items,
                                   'Current_List/Line_{}/Txt'.format(i + 1)))
        return [item for item in l if item]

    def home(self):
        self.cursor('Return to Home')

    def back(self):
        self.cursor('Return')

    def up(self):
        self.cursor('Up')

    def down(self):
        self.cursor('Down')

    def left(self):
        self.cursor('Left')

    def right(self):
        self.cursor('Right')

    def playback(self, cmd):
        self.put('SERVER/Play_Control/Playback', cmd)

    def play(self):
        self.playback('Play')

    def stop(self):
        self.playback('Stop')

    def pause(self):
        self.playback('Pause')

    def next(self):
        self.playback('Skip Fwd')

    def previous(self):
        self.playback('Skip Rev')


if __name__ == '__main__':

    c = RemoteController('http://yamaha')
    c.server()
    c.home()

    for _ in range(2):
        c.select()
        pause()

    pprint(c.list())


    # 'Info': 'System/Service/Info',
    # 'Input': 'Main_Zone/Input/Input_Sel',  # SERVER
    # 'Config': 'System/Config',
    # 'Basic': 'Main_Zone/Basic_Status',
    # 'Input_Sel_Item': 'Main_Zone/Input/Input_Sel_Item',
