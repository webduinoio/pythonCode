import struct, socket
from uyeelight import *

# see yeelight app for IP
bulb = Bulb("192.168.0.95")

try:
    if not bulb.is_on:
        bulb.turn_on()
except YeeLightException as e:
    print(e)

bulb.set_rgb(255,0,255, effect=EFFECT.SUDDEN, duration=1)

def discover_bulbs(timeout=2, interface=False):
    """
    Discover all the bulbs in the local network.
    :param int timeout: How many seconds to wait for replies. Discovery will
                        always take exactly this long to run, as it can't know
                        when all the bulbs have finished responding.
    :param string interface: The interface that should be used for multicast packets.
                             Note: it *has* to have a valid IPv4 address. IPv6-only
                             interfaces are not supported (at the moment).
                             The default one will be used if this is not specified.
    :returns: A list of dictionaries, containing the ip, port and capabilities
              of each of the bulbs in the network.
    """
    msg = "\r\n".join(["M-SEARCH * HTTP/1.1", "HOST: 239.255.255.250:1982", 'MAN: "ssdp:discover"', "ST: wifi_bulb"])
    MCAST_GRP = "239.255.255.250"
    MCAST_PORT= 1982
    # Set up UDP socket
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((MCAST_GRP, MCAST_PORT))
    # '\xc0\xa8\x01\x01' socket.inet_aton(MCAST_GRP)
    mreq = struct.pack("4sl",'\xef\xff\xff\xfa' , socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    s.sendto(msg.encode(), (MCAST_GRP, MCAST_PORT))
    """
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 1982))
    s.sendto(msg.encode(), ('239.255.255.250', 1982))    
    
    bulbs = []
    bulb_ips = set()
    while True:
        data, addr = s.recvfrom(65507)

        capabilities = dict([x.strip("\r").split(": ") for x in data.decode().split("\n") if ":" in x])
        parsed_url = urlparse(capabilities["Location"])

        bulb_ip = (parsed_url.hostname, parsed_url.port)
        if bulb_ip in bulb_ips:
            continue

        capabilities = {key: value for key, value in capabilities.items() if key.islower()}
        bulbs.append({"ip": bulb_ip[0], "port": bulb_ip[1], "capabilities": capabilities})
        bulb_ips.add(bulb_ip)

    return bulbs

print(discover_bulbs())

