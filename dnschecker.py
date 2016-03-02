#!/usr/bin/env python
# DNS reverse and forward checker utility

import argparse
import logging
import logging.config
import socket
import sys
import dns
import dns.resolver
import dns.reversename
import dnscheckersettings


# Logging Initialization
logging.config.dictConfig(dnscheckersettings.DNS_CHECKER_LOGGING)
logger = logging.getLogger("root")

# Variables

node_names = ['provo', 'sandy', 'orem', 'ogden', 'layton',
              'logan', 'lehi', 'murray', 'boston', 'chicago',
              'houston', 'phoenix', 'dallas', 'detroit', 'columbus',
              'austin', 'memphis', 'seattle', 'denver', 'porland',
              'tucson', 'atlanta', 'fresno', 'mesa', 'omaha',
              'oakland', 'miami', 'tulsa', 'honolulu', 'wichita',
              'raleigh', 'anaheim', 'tampa', 'toledo', 'aurora',
              'stockton', 'buffalo', 'newark', 'glendale', 'lincoln',
              'norfolk', 'chandler', 'madison', 'orlando', 'garland',
              'akron', 'reno', 'laredo']

node_list = []


# Functions

def execute_forward_dns():
    """
    Executes the forward DNS checks
    :return: nothing
    """
    print(" ")
    print("Starting Forward DNS Check:")
    print(" ")

    for node in node_list:
        logger.info("Node: {}".format(node.print_node()))

        try:
            ip_check = dns.resolver.query(node.node_fqdn, 'A')
            # dns_record = dns.resolver.query("google.com", 'A')
            for ip in ip_check:
                logger.info("Node:{0} Resolved IP: {1} | Required IP: {2}".format(node.node_fqdn, ip, node.ip_address))
                if ip == node.ip_address:
                    print "IP address match"
                else:
                    print "IP address does not match"

        except dns.resolver.NXDOMAIN:
            print 'Error: NXDOMAIN'
        except dns.resolver.Timeout:
            print 'Error: Timeout'
        except dns.resolver.NoAnswer:
            print 'Error: No Answer'

    print("Execute forward DNS.")


def create_node_information(ip, number_nodes, color, domain):
    """
    Prints the node information
    :param ip: Starting IP address
    :param number_nodes: Number of Nodes
    :param color: Rack Color
    :param domain: Domain
    :return: nothing
    """
    print("List of Nodes:")
    print(" ")
    print("{0}\t{1}\t\t{2}\t\t\t{3}\t{4}".format("Number", "Name", "FQDN", "IP Address", "PTR"))
    # print("--------------------------------------------------------------------------------")
    for node in range(0, number_nodes):
        # logger.info("Node: {}".format(node))
        node_number = node + 1
        node_name = node_names[node]
        node_fqdn = "{0}-{1}.{2}".format(node_name, color, domain)
        new_ip = calculate_ip(ip, node_number)
        node_prt = calculate_prt(new_ip)
        node = Racknode(node_number, node_name, node_fqdn, new_ip, node_prt)
        node.print_node()
        # Adding Nodes to the Node List
        node_list.append(node)
    logger.info("Nodes in list: {}".format(len(node_list)))


def calculate_ip(ip, node_number):
    """
    Calculates the Node's new IP address based on the node number
    :param ip: Initial IP
    :param node_number: Node Number
    :return: returns new IP address for the node
    """
    octets = ip.split(".")
    last_octet = int(octets[3])
    updated_octet = last_octet + node_number

    new_ip = "{0}.{1}.{2}.{3}".format(octets[0], octets[1], octets[2], updated_octet)
    return new_ip


def calculate_prt(new_ip):
    """
    Calculates the node PRT
    :param new_ip: IP address
    :return: returns the PRT based on the IP address
    """
    octets = new_ip.split(".")
    node_prt = "{0}.{1}.{2}.{3}.in-addr.arpa".format(octets[3], octets[2], octets[1], octets[0])
    return node_prt


def execute_backward_dns(ip, number_nodes, color):
    print("Execute reverse DNS.")

    n = dns.reversename.from_address("127.0.0.1")
    print n
    print dns.reversename.to_address(n)


def populate_node_dns_list(ip, number_nodes, color, domain):
    """
    Populates the node list with the proper DNS Entries
    :param ip: Starting IP address
    :param number_nodes: Number of Nodes
    :param color: Rack Color
    :return: nothing
    """


def valid_ip(address):
    """
    Functions that checks for valid IPs
    :param address: IP Address
    :return: True or False
    """
    try:
        socket.inet_aton(address)
        return True
    except:
        return False


def main():
    # if os.getuid() != 0:
    #    print("You need to run it as root.")
    #    sys.exit(1)

    parser = argparse.ArgumentParser(description='EMC\'s Forward and Reverse DNS Checker utility.')
    parser.add_argument('-ip', nargs='+', help='Starting IP for the Nodes. Example: 10.1.0.4', required=True)
    parser.add_argument('-nodes', nargs='+', help='Number of Nodes in the Rack. Example: 12', required=True)
    parser.add_argument('-color', dest='color', nargs='+', help='Starting color. Example: green.', required=True)
    parser.add_argument('-domain', nargs='+', help='Domain Name. Example: emc.com.', required=True)

    parser.set_defaults(color="green")
    args = parser.parse_args()

    # Parameter Validation ------------------------------------------------------------

    # Check for Valid IP Addresses
    for ip in args.ip:
        if not valid_ip(ip):
            print "Please check the --ip value. The IP '%s' is not valid" % ip
            sys.exit(2)

    # Execution Steps  ----------------------------------------------------------------
    logger.info("Starting DNS Checks:")

    ip = args.ip[0]
    number_nodes = int(args.nodes[0])
    color = args.color[0]
    domain = args.domain[0]

    logger.info("Starting IP Address:{}".format(ip))
    logger.info("Number of Nodes: IP Address:{}".format(number_nodes))
    logger.info("Rack Color:{}".format(color))
    logger.info("Domain Name::{}".format(domain))

    create_node_information(ip, number_nodes, color, domain)
    execute_forward_dns()
    # execute_backward_dns(ip, number_nodes, color, domain)

    logger.info("DNS Checks Completed.")


# Inner Classes
class Racknode():
    """Node object"""

    def __init__(self, node_number, node_name, fqdn, ip_address, prt):
        """ Initialize node attributes
        :param node_number: Node's number
        :param node_name: Node's name
        :param fqdn: Node's fully qualified domain name
        :param ip_address: Node's IP address
        :param prt: Node's PRT
        :return: nothing
        """
        self.node_number = node_number
        self.node_name = node_name
        self.node_fqdn = fqdn
        self.node_ip = ip_address
        self.node_prt = prt

    def print_node(self):
        """ Prints the Node Information
        :return: nothing
        """
        print(
            "{0}\t{1}\t\t{2}\t{3}\t{4}".format(self.node_number, self.node_name, self.node_fqdn, self.node_ip, self.node_prt))



if __name__ == "__main__":
    # sys.exit - will not exit interactive interpreter when main finishes
    sys.exit(main())
