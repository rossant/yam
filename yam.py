#!/usr/bin/env python
from __future__ import print_function

import sys
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


def _on_off(c):
    if isinstance(c, string_types):
        return c.title()
    else:
        return 'On' if c else 'Off'


def pause(dur=.5):
    sleep(dur)


class RemoteController(object):
    _host_path = '/YamahaRemoteControl/ctrl'

    def __init__(self, host):
        self._host = host

    # Internal methods
    # -------------------------------------------------------------------------

    def _post_xml(self, xml):
        return requests.post(self._host + self._host_path, xml).text

    def post(self, obj, text=None, out_path=None, mode='get'):
        if isinstance(obj, string_types):
            obj = _request(obj, text=text, mode=mode)
        assert isinstance(obj, dict)
        xml = xmltodict.unparse(obj, pretty=True)
        out = self._post_xml(xml)
        try:
            out = xmltodict.parse(out)
        except TypeError:
            msg = "An error occurred with the following request:\n"
            msg += xml
            raise ValueError(msg)
            return
        if out_path:
            return _get_item(out, out_path)
        return out

    def get(self, obj, text=None, out_path=None):
        return self.post(obj, text=text, out_path=out_path or obj, mode='get')

    def put(self, obj, text=None, out_path=None):
        return self.post(obj, text=text, out_path=out_path, mode='put')

    # General
    # -------------------------------------------------------------------------

    def volume(self, val=None):
        path = 'Main_Zone/Volume/Lvl'
        if val is None:
            return int(self.get(path, out_path=path + '/Val'))
        else:
            val = val.lower()
            if val == 'up':
                val = self.volume() + 5
            elif val == 'down':
                val = self.volume() - 5
            obj = _request(path, mode='put')
            child = _get_item(obj, path)
            child['Val'] = str(val)
            child['Exp'] = 0
            child['Unit'] = ''
            self.post(obj)

    def power(self, on=None):
        if on is None:
            return self.get('System/Power_Control/Power')
        self.put('System/Power_Control/Power', 'On' if on else 'Off')

    def mute(self, on=None):
        if on is None:
            return self.get('Main_Zone/Volume/Mute')
        self.put('Main_Zone/Volume/Mute', _on_off(on))

    def info(self):
        return self.get('System/Service/Info')

    def config(self):
        return self.get('System/Config')

    def status(self):
        return self.get('Main_Zone/Basic_Status')

    # Input
    # -------------------------------------------------------------------------

    def input(self, input=None):
        if input is None:
            return self.get('Main_Zone/Input/Input_Sel').lower()
        self.put('Main_Zone/Input/Input_Sel', input.upper())

    def server(self):
        if self.input() != 'server':
            self.input('server')

    def tuner(self):
        if self.input() != 'tuner':
            self.input('tuner')

    def preset(self, preset=None):
        if preset is None:
            return self.get('Tuner/Play_Control/Preset/Preset_Sel')
        self.put('Tuner/Play_Control/Preset/Preset_Sel', preset.title())

    def optical(self):
        if self.input() != 'optical':
            self.input('optical')

    # Navigation
    # -------------------------------------------------------------------------

    def current(self, input=''):
        input = input.upper()
        if not input:
            input = self.input()
        if input == 'TUNER':
            input = 'Tuner'
        return self.get('{}/Play_Info'.format(input))

    def show(self):
        current = self.current('Tuner')
        out = (current['Meta_Info']['Program_Service'] or '').strip() + ' - '
        out += (current['Meta_Info']['Radio_Text_A'] or ' ' +
                current['Meta_Info']['Radio_Text_B'] or '').strip()
        return out

    def is_playing(self):
        info = self.current()
        if info:
            return info['Playback_Info'] == 'Play'

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

    def list(self):
        k = 8
        items = self.get('SERVER/List_Info')
        items = [_get_item(items, 'Current_List/Line_{}/Txt'.format(i + 1))
                 for i in range(k)]
        return [item for item in items if item]

    def iter_pages(self):
        k = 8
        max_line = int(_get_item(self.get('SERVER/List_Info'),
                                 'Cursor_Position/Max_Line'))
        n_pages = math.ceil(max_line / float(k))
        for page in range(n_pages):
            yield self.list()
            self.page_down()
            self.wait_menu()

    def wait_menu(self):
        # Pause until the menu is ready.
        while True:
            if self.get('SERVER/List_Info')['Menu_Status'] != 'Ready':
                pause(.05)
            else:
                return

    def iter_items(self):
        for items in self.iter_pages():
            for i, item in enumerate(items):
                yield i, item

    def list_complete(self):
        l = []
        for items in self.iter_pages():
            l.extend(items)
        return l

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

    # Playback
    # -------------------------------------------------------------------------

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


def _match(item, dir):
    return dir.lower() in item.lower()


def navigate_server(c, *dirs):
    # Server home.
    c.stop()
    c.wait_menu()

    c.server()
    c.home()
    c.wait_menu()

    # Get to root.
    for _ in range(2):
        c.select()
        c.wait_menu()

    for dir in dirs:
        dir = dir.lower()
        no_match = True
        for i, item in c.iter_items():
            if _match(item, dir):
                print("Match for {}".format(item))
                c.select(i)
                c.wait_menu()
                no_match = False
                break
        if no_match:
            print("No match.")
            return

    # Navigate deeper until something is playing.
    for _ in range(10):
        if c.is_playing():
            return
        c.select()
        c.wait_menu()


def main():
    c = RemoteController('http://yamaha')

    if len(sys.argv) == 1:
        print('Yamaha ' + c.config()['Model_Name'])
        return

    cmd = sys.argv[1]
    if cmd in ('on', 'off'):
        print("Power {}.".format(cmd))
        c.power(cmd)
    elif hasattr(c, cmd):
        args = sys.argv[2:]
        args_s = ' '.join(args)
        if args_s:
            args_s = ' ' + args_s
        out = getattr(c, cmd)(*args)
        if isinstance(out, dict):
            pprint(out)
            return
        if out:
            print(str(out).strip())
    elif cmd == 'stop':
        c.stop()
    else:
        navigate_server(c, *sys.argv[1:])


if __name__ == '__main__':
    main()
