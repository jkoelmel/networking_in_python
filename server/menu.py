#######################################################################################
# File:             menu.py
# Purpose:          CSC645 Assigment #1 TCP socket programming
# Description:      Template Menu class. You are free to modify this
#                   file to meet your own needs. Additionally, you are
#                   free to drop this Menu class, and use a version of yours instead.
# IMPORTANT:        This file can only resides on the server side.
# Usage :           menu = Menu() # creates object
#
########################################################################################
import json


class Menu:

    @staticmethod
    def get():

        menu = {
            'titles': ['****** TCP/UDP Network ******', '------------------------------------', 'Options Available:'],
            'options': {'1': 'Get Users List', '2': 'Send A Message', '3': 'Get My Messages',
                        '4': 'Send A Direct Message via UDP',
                        '5': 'Broadcast A Message With CDMA', '6': 'Create A Secure Channel To Chat Using PGP',
                        '7': 'Join An Existing Channel', '8': 'Create A Bot To Manage A Future Channel',
                        '9': 'Map The Network', '10': 'Get the Routing Table of This Client with LSP',
                        '11': 'Get the Routing Table of This Network with DVP', '12': 'Turn Web Proxy Server On (WIP)',
                        '13': 'Disconnect From Server'
                        }

            }

        menu_json = json.dumps(menu)
        return menu_json

    @staticmethod
    def option():
        """
        :return: an integer representing the option chosen by the user from the menu
        """
        option = int(input("\n\nOption <Enter a number>: "))
        while option not in range(1, 14):
            option = int(input("\nInvalid entry, choose another option:"))

        return option
