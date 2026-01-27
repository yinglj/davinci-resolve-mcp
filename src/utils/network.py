#!/usr/bin/env python3
"""
Network utilities for DaVinci Resolve MCP Server
"""

import netifaces


def get_all_ip_addresses():
    """Retrieve all non-loopback IP addresses."""
    try:
        # Get all network interfaces
        interfaces = netifaces.interfaces()
        ip_list = []

        # Iterate over each interface
        for interface in interfaces:
            # Get address information for the interface
            addrs = netifaces.ifaddresses(interface)
            # Check if IPv4 address (AF_INET) exists
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr.get("addr")
                    if ip and ip != "127.0.0.1":  # Exclude local loopback address
                        ip_list.append((interface, ip))

        return ip_list if ip_list else []
    except Exception:
        # Return empty list on failure
        return []
