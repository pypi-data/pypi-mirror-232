def checksum(data):
    """
    Compute and return the Internet Checksum of the given data.
    
    The Internet Checksum is used by the Internet Protocol (IP), Internet Control Message Protocol (ICMP),
    and the Transmission Control Protocol (TCP) of the TCP/IP protocol suite.

    Parameters:
    - data (bytes): The data over which the checksum is to be computed. 

    Returns:
    - int: The computed checksum.

    The function first pads the data if its length is odd. Then, it computes the sum of 16-bit words 
    of the data in a loop. After processing all the words, it adds the carry bits to the final sum.
    Finally, it returns the one's complement of the computed sum.

    Example:
    >>> checksum(b'Hello, World!')
    34425
    """
    s = 0
    n = len(data) % 2
    for i in range(0, len(data)-n, 2):
        s += (data[i] << 8) + (data[i + 1])
    if n:
        s += (data[i + 1] << 8)
    while (s >> 16):
        s = (s & 0xFFFF) + (s >> 16)
    s = ~s & 0xFFFF
    return s