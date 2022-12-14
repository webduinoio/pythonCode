import usocket as socket
import json, struct

class YeeLightException(Exception):
    pass

class EFFECT:
    SMOOTH = "smooth"
    SUDDEN = "sudden"

class MODE:
    NORMAL = 0
    CT_MODE = 1
    RGB_MODE = 2
    HSV_MODE = 3
    COLOR_FLOW_MODE = 4
    NIGHT_LIGHT_MODE = 5

class ACTION:
    LED_RECOVER_STATE = 0
    LED_STAY = 1
    LED_TURN_OFF = 2
 
class SCENE_CLASS:
    COLOR = "color"
    HSV = "hsv"
    CT = "ct"
    AUTO_DELAY_OFF = "auto_delay_off"

class SET_ADJUST_ACTION:
    INCREASE = "increase"
    DECREASE = "decrease"
    CIRCLE = "circle"


class SET_ADJUST_PROP:
    BRIGHT = "bright"
    CT = "ct"
    COLOR = "color"

""" API DOCS: https://www.yeelight.com/download/Yeelight_Inter-Operation_Spec.pdf """
class Bulb():
    def __init__(self, ip, port=55443, debug=False):
        self.cmd_id = 0
        self._ip = ip
        self._port = port
        self.debug = debug

    @property
    def get_ip(self):
        return self._ip

    @property
    def get_port(self):
        return self._port

    def turn_on(self, effect=EFFECT.SUDDEN, duration=30, mode=MODE.NORMAL):
        return self._handle_response(self._send_message("set_power",
                                                        ["on", effect, duration, mode]))

    def turn_off(self, effect=EFFECT.SUDDEN, duration=30, mode=MODE.NORMAL):
        return self._handle_response(self._send_message("set_power",
                                                        ["off", effect, duration, mode]))

    def toggle(self):
        return self._handle_response(self._send_message("toggle"))

    @property
    def is_on(self):
        result = self._handle_response(self._send_message("get_prop", ["power"]))
        return result[0] == "on"

    def change_color_temperature(self, color_temp_val, effect=EFFECT.SUDDEN, duration=30):
        return self._handle_response(self._send_message("set_ct_abx",
                                                        [color_temp_val, effect, duration]))

    def set_rgb(self, r, g, b, effect=EFFECT.SUDDEN, duration=30):
        rgb = (r * 65536) + (g * 256) + b
        return self._handle_response(self._send_message("set_rgb",
                                                        [rgb, effect, duration]))

    def set_hsv(self, hue, sat, effect=EFFECT.SUDDEN, duration=30):
        return self._handle_response(self._send_message("set_hsv",
                                                        [hue, sat, effect, duration]))

    def set_brightness(self, brightness, effect=EFFECT.SUDDEN, duration=30):
        return self._handle_response(self._send_message("set_bright",
                                                        [brightness, effect, duration]))

    def save_current_state(self):
        return self._handle_response(self._send_message("set_default"))

    def start_color_flow(self, count, flow_expression, action=ACTION.LED_RECOVER_STATE):
        return self._handle_response(self._send_message("start_cf",
                                                        [count, action, flow_expression]))

    def stop_color_flow(self):
        return self._handle_response(self._send_message("stop_cf"))

    def set_scene(self, val1, val2, val3, opt=SCENE_CLASS.COLOR):
        return self._handle_response(self._send_message("set_scene",
                                                        [opt, val1, val2, val3]))

    def sleep_timer(self, time_minutes, type=0):
        return self._handle_response(self._send_message("cron_add",
                                                        [type, time_minutes]))

    def get_background_job(self, type=0):
        return self._handle_response(self._send_message("cron_get",
                                                        [type]))

    def delete_background_job(self, type=0):
        return self._handle_response(self._send_message("cron_del",
                                                        [type]))

    def set_adjust(self, action=SET_ADJUST_ACTION.INCREASE, prop=SET_ADJUST_PROP.BRIGHT):
        return self._handle_response(self._send_message("set_adjust",
                                                        [action, prop]))

    def adjust_brightness(self, percentage, duration=30):
        return self._handle_response(self._send_message("adjust_bright",
                                                        [percentage, duration]))

    def adjust_color_temperature(self, percentage, duration=30):
        return self._handle_response(self._send_message("adjust_ct",
                                                        [percentage, duration]))

    def adjust_color(self, percentage, duration=30):
        return self._handle_response(self._send_message("adjust_color",
                                                        [percentage, duration]))

    def set_music(self, host, port, enable=True):
        return self._handle_response(self._send_message("set_music",
                                                        [1 if enable else 0, host, port]))

    def set_name(self, name):
        return self._handle_response(self._send_message("set_name",
                                                        [name]))

    def _send_message(self, method, params=None):
        if params is None:
            params = []

        self.cmd_id += 1

        message = '{{"id": {id}, "method": "{method}", "params": {params}}}\r\n'. \
            format(id=self.cmd_id, method=method, params=json.dumps(params))

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((self.get_ip, self.get_port))
            sock.send(message.encode())
            recv_data = sock.recv(1024)
        except socket.timeout:
            return ""
        finally:
            sock.close()

        return recv_data

    def search(timeout=2,debug=False):
        msg = "\r\n".join(["M-SEARCH * HTTP/1.1", "HOST: 239.255.255.250:1982", 'MAN: "ssdp:discover"', "ST: wifi_bulb"])
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', 1982))
        s.sendto(msg.encode(), ('239.255.255.250', 1982))
        s.settimeout(timeout)
        bulbs = {}
        while True:
            try:
                print("bulb search...")
                data, addr = s.recvfrom(1024)
                if(debug==True):
                    print("data:",data,",addr:",addr)
                capabilities = dict([x.strip("\r").split(": ") for x in data.decode().split("\n") if ":" in x])
                key = capabilities['Location'].split(':')[1][2:]
                bulbs[key] = capabilities
            except Exception as e:
                print("error!",e)
                break
        return bulbs

    def _handle_response(self, response):
        response = json.loads(response.decode('utf-8'))

        if self.debug:
            print(response)

        if "params" in response:
            return response["params"]
        elif "id" in response and not "error" in response:
            return response["result"]
        elif "error" in response:
            raise YeeLightException(response["error"])
        else:
            raise YeeLightException("Unknown Exception occurred.")
