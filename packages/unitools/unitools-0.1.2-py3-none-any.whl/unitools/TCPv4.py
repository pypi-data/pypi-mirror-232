from socket import socket, AF_INET, SOCK_STREAM, error as socket_error
from time import time

class Request:
    """A utility class to perform TCP 'pings' to a given host and port."""

    def __init__(self, host=None, port=None, timeout=2):
        """
        Initialize the Request with target host, port, and optional timeout.
        
        :param host: Target hostname or IP address.
        :param port: Target port number.
        :param timeout: Timeout in seconds for the TCP connection attempt.
        """
        self.host = host
        self.port = port
        self.timeout = timeout

    def tcp_ping(self):
        """
        Perform a single TCP ping to the provided host and port.

        :return: A Response object with details of the ping.
        """
        ip_socket = socket(AF_INET, SOCK_STREAM)
        ip_socket.settimeout(self.timeout)

        try:
            start_time = time()
            ip_socket.connect((self.host, self.port))
            return self.Response(host=self.host, port=self.port, latency=calculate_latency(start_time), reachable=True)
        except socket_error:
            return self.Response()
        finally:
            ip_socket.close()

    def tcp_ping_extended(self, ping_count=20):
        """
        Perform multiple TCP pings to the provided host and port.

        :param ping_count: Number of pings to perform.
        :return: A Responses object aggregating details of all pings.
        """
        responses = []
        for a in range(ping_count):
            responses.append(self.tcp_ping())
        return self.Responses(responses=responses)

    class Responses:
        """A class to represent aggregated responses of multiple TCP pings."""

        def __init__(self, responses=None):
            """
            Initialize the aggregated Responses.

            :param responses: List of Response objects from individual pings.
            """
            self.responses = responses
            self.total_packets = len(responses)
            self.packet_loss = self.packet_loss()
            self.average_latency = self.average_latency()

        def packet_loss(self):
            """Calculate and return the percentage of lost pings."""
            lost_packets = 0
            for response in self.responses:
                if not response.reachable:
                    lost_packets += 1
            return round((lost_packets / self.total_packets) * 100)

        def average_latency(self):
            """Calculate and return the average latency of the successful pings."""
            total_latency = 0
            received_packets = 0
            for response in self.responses:
                if response.reachable:
                    total_latency += response.latency
                    received_packets += 1
            if received_packets > 0:
                return round(total_latency / received_packets)

            return None

    class Response:
        """A class to represent the response of a TCP ping."""

        def __init__(self, host=None, port=None, latency=None, reachable=False):
            """
            Initialize the Response.

            :param host: Host to which the ping was sent.
            :param port: Port to which the ping was sent.
            :param latency: Time taken for the ping in milliseconds.
            :param reachable: Boolean indicating whether the host:port was reachable.
            """
            self.host = host
            self.port = port
            self.latency = latency
            self.reachable = reachable

        def __str__(self):
            """Return a string representation of the response."""
            if self.reachable:
                return f"Reply from {self.host} on TCP/{self.port}: time={self.latency}ms"
            else:
                return "Request timed out."


def calculate_latency(start_time):
    """
    Calculate the elapsed time since start_time.

    :param start_time: Starting time reference.
    :return: Elapsed time in milliseconds rounded to nearest whole number.
    """
    elapsed_time = (time() - start_time) * 1000
    latency = round(elapsed_time)
    return latency


if __name__ == "__main__":
    host = 'example.com'
    port = 80
    request = Request(host=host, port=port)

    # Single TCP Ping
    response = request.tcp_ping()
    print(vars(response))

    # Multiple TCP Pings
    responses = request.tcp_ping_extended(ping_count=5)
    print(vars(responses))