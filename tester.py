import scanner
from parse import Parser
from names import Names
from network import Network
from monitors import Monitors
import devices
import sys

my_names=Names()
my_scanner=scanner.Scanner(sys.argv[1], my_names)
# my_scanner=scanner.Scanner("connectioninputconnected.txt", my_names)
my_devices=devices.Devices(my_names)
my_network=Network(my_names, my_devices)
my_monitors=Monitors(my_names, my_devices, my_network)
my_parser=Parser(my_names, my_devices, my_network, my_monitors, my_scanner)
print(my_parser.parse_network())