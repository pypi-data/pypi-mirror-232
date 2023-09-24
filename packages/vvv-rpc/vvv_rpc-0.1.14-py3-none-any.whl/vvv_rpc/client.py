import os
import re
import sys
import time
import json
import queue
import inspect
import traceback
import builtins
import subprocess
import threading
import requests
class client:
    def __init__(self, interface=None, win_index=None):
        if interface and (not interface.startswith('http')):
            interface = 'http://' + interface
        self.interface = (interface or 'http://127.0.0.1:18089').rstrip('/')
        self.config_url = self.interface + '/config'
        self.quick_start_url = self.interface + '/quick_start'
        self.win_index = win_index or 0
        self.run_script_url = self.interface + '/run_script'
        self.run_script_quick_url = self.interface + '/run_only_script'
        self.default_timeout = 5

    def make_post_data(self, data=None):
        data = data or {}
        if self.win_index: data["win_index"] = self.win_index
        return data

    def post_interface(self, url, data, timeout=10):
        try:
            s = requests.post(url, data=data, timeout=timeout)
            s = s.json()
        except Exception as e:
            raise Exception(str(e))
        if s['status'] == 'success':
            return s.get('message', None)
        else:
            try:
                raise Exception(s['message'])
            except:
                raise Exception(str(s))

    def try_json_load(self, jsondata):
        try:
            return json.loads(jsondata)
        except:
            return jsondata

    def quick_cpu_num(self):
        return self.try_json_load(self.post_interface(self.quick_start_url, self.make_post_data({"cpu_num": '1'})))

    def quick_close_all(self):
        return self.try_json_load(self.post_interface(self.quick_start_url, self.make_post_data({"is_close": '1'})))

    def quick_start(self, num=1, vvv=None, limittime=2):
        def is_start():
            try:
                s = self.try_json_load(self.post_interface(self.quick_start_url, self.make_post_data({}), timeout=1.5))
                return True
            except Exception as e:
                time.sleep(0.5)
                return False
        if not is_start():
            v_chrome_target = os.path.join(os.path.split(sys.executable)[0], 'Scripts', 'chrome-win32-x64')
            v_chrome_exec = os.path.join(v_chrome_target, 'chrome-win32-x64', 'v_chrome.exe')
            if not os.path.isfile(v_chrome_exec):
                raise Exception('v_chrome not install in python.')
            cmd = 'start cmd /k "{}"'.format(v_chrome_exec)
            os.system(cmd)
        while 1:
            if is_start():
                break
        for _ in range(10):
            try:
                cfg = {
                    "is_start": '1', 
                    "init_num": num
                }
                if vvv:
                    cfg['vvv'] = vvv
                self.try_json_load(self.post_interface(self.quick_start_url, self.make_post_data(cfg)))
                break
            except Exception as e:
                time.sleep(0.5)
        start = time.time()
        while 1:
            try:
                self.clear_catch()
                break
            except Exception as e:
                if time.time() - start > limittime and str(e) == "{'status': 'fail', 'message': 'no config.'}":
                    raise e
                time.sleep(0.3)
        return self

    def init(self, vvv):
        return self.post_interface(self.config_url, self.make_post_data({"vvv": vvv}))

    def go_url(self, url, proxy=None, userAgent=None):
        data = self.make_post_data({"url": url})
        if proxy: data['proxy'] = proxy
        if userAgent: data['userAgent'] = userAgent
        return self.post_interface(self.config_url, data)

    def debugger_script(self, script):
        return self.post_interface(self.config_url, self.make_post_data({"debugger_script": script}))

    def show(self, check_hidden=True):
        if check_hidden:
            if self.run_script('document.hidden'):
                return self.post_interface(self.config_url, self.make_post_data({"show": True}))
        else:
            return self.post_interface(self.config_url, self.make_post_data({"show": True}))

    def get_urls(self):
        return self.post_interface(self.config_url, self.make_post_data({"clear_catch": True}))

    def clear_catch(self):
        return self.post_interface(self.config_url, self.make_post_data({"clear_catch": True}))

    def get_match_list(self):
        return self.post_interface(self.config_url, self.make_post_data({"show_match_url_list": True}))

    def remove_match_url(self, match_url):
        return self.post_interface(self.config_url, self.make_post_data({"match_url": match_url, "is_remove": True}))

    def set_match_url(self, match_url, value=None, vtype:'None or "base64"'=None, res_headers=None, res_code=None):
        data = self.make_post_data({"match_url": match_url})
        if value: data['value'] = value
        if vtype: data['vtype'] = vtype
        if res_headers: data['res_headers'] = json.dumps(res_headers)
        if res_code: data['res_code'] = res_code
        return self.post_interface(self.config_url, data)

    def run_script_quick(self, script):
        return self.try_json_load(self.post_interface(self.run_script_quick_url, self.make_post_data({"script": script})))

    def run_script(self, scripts, wait_util_true=None, timeout=40000):
        # timeout 毫秒
        data = self.make_post_data({"scripts": scripts})
        if wait_util_true: data["wait_util_true"] = wait_util_true
        if timeout: data["timesout"] = int(timeout / 100)
        return self.try_json_load(self.post_interface(self.run_script_url, data, timeout=(timeout/1000)+10))

    def get_url_by_scripts(self, match_url, scripts, wait_util_true=None, timeout=40000):
        # timeout 毫秒
        data = self.make_post_data({"match_url": match_url, "scripts": scripts})
        if wait_util_true: data["wait_util_true"] = wait_util_true
        if timeout: data["timesout"] = int(timeout / 100)
        return self.try_json_load(self.post_interface(self.run_script_url, data, timeout=(timeout/1000)+10))

    def run_elements(self, elements, timeout=40000):
        # timeout 毫秒
        data = self.make_post_data({"elements": json.dumps(elements)})
        if timeout: data["timesout"] = int(timeout / 100)
        return self.try_json_load(self.post_interface(self.run_script_url, data, timeout=(timeout/1000)+10))

    def get_url_by_elements(self, match_url, elements, timeout=40000):
        # timeout 毫秒
        data = self.make_post_data({"match_url": match_url, "elements": json.dumps(elements)})
        if timeout: data["timesout"] = int(timeout / 100)
        return self.try_json_load(self.post_interface(self.run_script_url, data, timeout=(timeout/1000)+10))

    def clear_add_script(self):
        return self.post_interface(self.config_url, self.make_post_data({"clear_script": True}))

    def add_script_before_load_url(self, add_script, atype=None):
        data = self.make_post_data({"add_script": add_script})
        if atype: data['atype'] = atype
        return self.post_interface(self.config_url, data)

    def set_position(self, x, y):
        if not (type(x) == int and type(y) == int):
            raise TypeError('set_position type error. x:{},y:{}'.format(x, y))
        return self.post_interface(self.config_url, self.make_post_data({"position": "{},{}".format(x, y)}))

    def set_size(self, w, h):
        if not (type(w) == int and type(h) == int):
            raise TypeError('set_size type error. w:{},h:{}'.format(w, h))
        return self.post_interface(self.config_url, self.make_post_data({"size": "{},{}".format(w, h)}))

    def restart(self, is_keep_cache=True, auto_change_sec=None):
        data = self.make_post_data({"is_restart": True})
        if auto_change_sec: data['auto_change_sec'] = auto_change_sec
        if is_keep_cache: data['is_keep_cache'] = is_keep_cache
        return self.post_interface(self.config_url, data)

    def auto_change_finger(self, auto_change_sec):
        return self.post_interface(self.config_url, self.make_post_data({ "auto_change_sec": auto_change_sec }))

    def disabled_http_only(self, enable=True):
        return self.post_interface(self.config_url, self.make_post_data({ "disabled_http_only": enable }))

    def is_debugger(self, enable=True):
        return self.post_interface(self.config_url, self.make_post_data({ "is_debugger": enable }))

    def log_debugger(self, enable=True):
        return self.post_interface(self.config_url, self.make_post_data({ "log_debugger": enable }))

    def get_debugger(self, match_url=None):
        data = self.make_post_data({"get_debugger": True})
        if match_url: data['match_url'] = match_url
        return self.post_interface(self.config_url, data)

    def clear_debugger(self, enable=True):
        return self.post_interface(self.config_url, self.make_post_data({ "clear_debugger": enable }))

    def disabled_redirect(self, enable=True):
        return self.post_interface(self.config_url, self.make_post_data({ "disabled_redirect": enable }))

    def clear_storage_data(self, enable=True):
        return self.post_interface(self.config_url, self.make_post_data({ "clear_storage_data": enable }))

    def set_rtc_ip(self, ip):
        if not ip:
            return
        x = re.findall(r'\d+\.\d+\.\d+\.\d+', ip)
        if x:
            self.clear_add_script()
            return self.add_script('window.v_proxy = "%s"' % (x[0]))
        else:
            raise Exception('ip format error. input ip:{}'.format(ip))

    def close_http_only(self):
        return self.disabled_http_only(True)

    def clear_storage(self):
        return self.clear_storage_data(True)

    def add_script(self, add_script, atype=None):
        return self.add_script_before_load_url(add_script, atype)

class server:
    def __init__(self, taskerlist, tasklimit=None):
        self.taskerlist = taskerlist
        self.tasklist = queue.Queue(tasklimit or len(self.taskerlist))
        for idx, tasker in enumerate(self.taskerlist):
            # tasker.taskerlist = self.taskerlist
            td = threading.Thread(target=self.looper, args=(tasker,))
            td.vvv_tasker = tasker
            td.start()
        lock = threading.RLock()

        _org_print = print
        def _new_print(*arg,**kw):
            lock.acquire()
            td = threading.current_thread()
            vvv_tasker = getattr(td, 'vvv_tasker', None)
            if vvv_tasker:
                name = '{} :: {}'.format(vvv_tasker.interface, vvv_tasker.win_index)
                name = "[{}]".format(name.center(34))
                _org_print(name,*arg,**kw)
            else:
                _org_print(*arg,**kw)
            lock.release()
        builtins.print = _new_print

    def put(self, task):
        try:
            self.tasklist.put_nowait(task)
        except:
            raise Exception('over tasklist limit num:{}'.format(len(self.taskerlist)))

    def looper(self, tasker):
        while(1):
            task = self.tasklist.get()
            try:
                task[0](tasker, *task[1], **task[2])
            except:
                print(traceback.format_exc())
                time.sleep(2)

    def __call__(self, func):
        def _(*a, **kw):
            self.put([func, a, kw])
        _.taskerlist = self.taskerlist
        return _

if __name__ == '__main__':

    # @server([
    #     client('http://127.0.0.1:18089',0),
    #     client('http://127.0.0.1:18089',1),
    # ])
    # def some(vvv, url):
    #     print(vvv, url)
    #     asdfasdf

    # for i in range(10):
    #     try:
    #         some('123')
    #     except:
    #         pass

    # time.sleep(1)
    # some('123')
    # some('123')
    vvv = client().quick_start()
    vvv.go_url('http://baidu.com')