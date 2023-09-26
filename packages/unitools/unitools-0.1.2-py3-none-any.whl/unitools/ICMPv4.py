import socket
import os
import struct
import select
import time
import sys
import platform
from unitools.utils.IPHelpers import checksum

ICMP_ECHO_REQUEST = 8

class Request:
    """
    ICMPv4 class provides methods for creating, sending, and receiving ICMPv4 echo requests.
    
    Attributes:
        address (str): The target IP address for the ICMP requests.
        timeout (int): The maximum waiting time (in seconds) for an ICMP response.
        os_name (str): The name of the current operating system.
    """

    def __init__(self, address=None, timeout=2):
        """
        Initializes the ICMPv4 object.
        
        Args:
            address (str): The target IP address. Defaults to None.
            timeout (int): The maximum waiting time for an ICMP response. Defaults to 2 seconds.
        """
        self.address = address
        self.timeout = timeout
        self.os_name = platform.system().lower()

    def ping(self):
        """
        Sends an ICMP echo request and waits for a response.
        
        Returns:
            ICMPResponse: An object containing details of the ICMP response or None if there's no response.
        """
        ip_socket = self.create_socket()
        start_time = time.time() # Seems to be the same for linux and windows...Wierd
        if self.send_on_socket(ip_socket):
            while True:
                ready = select.select([ip_socket], [], [], self.timeout)

                if ready[0]:
                    rec_packet, addr = ip_socket.recvfrom(1024)
                    if self.address == addr[0]:

                        icmp_header = rec_packet[20:28]

                        icmp_type, _, _, _, _ = struct.unpack("bbHHh", icmp_header)

                        if icmp_type == 0:
                            elapsed = (time.time() - start_time) * 1000
                            ip_socket.close()
                            return self.Response(address=addr[0], bytes=len(rec_packet), latency=int(elapsed), ttl=rec_packet[8])
                else:
                    ip_socket.close()
                    return self.Response()


    def send_on_socket(self, ip_socket):
        """
        Sends an ICMP packet using the provided socket.
        
        Args:
            ip_socket (socket.socket): The socket through which the ICMP packet will be sent.
        
        Returns:
            bool: True if the packet is sent successfully, otherwise raises an exception.
        """
        try:
            ip_socket.sendto(self.create_icmp_packet(), (self.address, 1))
            return True
        except Exception as e:
            raise e


    def create_socket(self):
        """
        Creates a raw socket suitable for ICMP communication.
        
        Returns:
            socket.socket: A socket object.
        
        Raises:
            Exception: If the socket creation fails.
        """
        try:
            ip_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
            return ip_socket
        except socket.error as e:
            raise e("Socket creation failed.")

    def create_icmp_packet(self):
        """
        Creates an ICMP echo request packet.
        
        Returns:
            bytes: A byte representation of the ICMP packet.
        """
        # Create a unique ID for our ICMP request
        id = os.getpid() & 0xFFFF

        # The ICMP header consists of type, code, checksum, id, and sequence number
        header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, id, 1)
        data = bytes([i%256 for i in range(32)])
        header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(checksum(header + data)), id, 1)

        packet = header + data
        return packet

    class Response:
        """
        A class representing an ICMP response.
        
        Attributes:
            address (str): The IP address from which the response was received.
            bytes (int): The size of the received ICMP packet in bytes.
            latency (int): The round-trip time for the ICMP request/response in milliseconds.
            ttl (int): The time-to-live value from the received ICMP packet.
        """


        def __init__(self, address=None, bytes=None, latency=None, ttl=None):
            """
            Initializes the ICMPResponse object.
            
            Args:
                address (str): The IP address from which the response was received. Defaults to None.
                bytes (int): The size of the received ICMP packet. Defaults to None.
                latency (int): The round-trip time in milliseconds. Defaults to None.
                ttl (int): The TTL value from the received ICMP packet. Defaults to None.
            """
            self.address = address
            self.bytes = bytes
            self.latency = latency
            self.ttl = ttl

        def __str__(self):
            """
            Returns a string representation of the ICMP response.
            
            Returns:
                str: A formatted string representing the ICMP response.
            """
            if self.is_reachable():
                return f"Reply from {self.address}: bytes={self.bytes} time={self.latency}ms TTL={self.ttl}"
            else:
                return "Request timed out."

        def is_reachable(self):
            """
            Determines if the target host is reachable based on the ICMP response.
            
            Returns:
                bool: True if the target host is reachable, otherwise False.
            """
            if self.latency is not None:
                return True
            else:
                return False


if __name__ == '__main__':
    icmp_response = Request(address="8.8.8.8").ping()
    print(icmp_response)