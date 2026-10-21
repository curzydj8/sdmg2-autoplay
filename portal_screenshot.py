#!/usr/bin/env python3
"""用 Portal Screenshot API 截屏（Wayland 可用）"""
import sys, random, os

def main():
    try:
        import gi
        gi.require_version('Gio', '2.0')
        from gi.repository import Gio, GLib
    except Exception as e:
        print(f"ERROR: gi 不可用: {e}")
        return 1

    out_path = sys.argv[1] if len(sys.argv) > 1 else '/tmp/portal-shot.png'
    
    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

    def await_response(req_path, timeout_s):
        out = {}
        loop = GLib.MainLoop()
        proxy = Gio.DBusProxy.new_sync(bus, Gio.DBusProxyFlags.NONE, None,
            'org.freedesktop.portal.Desktop', req_path,
            'org.freedesktop.portal.Request', None)
        def on_signal(p, sender, signal_name, params):
            if signal_name == 'Response':
                out['code'] = params[0]
                out['results'] = dict(params[1])
                loop.quit()
        proxy.connect('g-signal', on_signal)
        GLib.timeout_add_seconds(timeout_s, loop.quit)
        loop.run()
        return out.get('code'), out.get('results', {})

    portal = Gio.DBusProxy.new_sync(bus, Gio.DBusProxyFlags.NONE, None,
        'org.freedesktop.portal.Desktop', '/org/freedesktop/portal/desktop',
        'org.freedesktop.portal.Screenshot', None)

    token = f"shot{random.randint(1000,9999)}"
    print("正在截图...", flush=True)
    req = portal.Screenshot('(sa{sv})', '',
        {'handle_token': GLib.Variant('s', token),
         'interactive': GLib.Variant('b', False)})
    code, results = await_response(req, 30)
    if code == 0 and 'uri' in results:
        uri = results['uri']
        print(f"SUCCESS: {uri}")
        # uri 是 file:// 路径，复制到目标位置
        import urllib.parse
        src = urllib.parse.unquote(uri.replace('file://', ''))
        import shutil
        shutil.copy(src, out_path)
        print(f"已保存到: {out_path}")
        return 0
    print(f"ERROR: 截图失败 (code={code})")
    return 1

if __name__ == '__main__':
    sys.exit(main())
