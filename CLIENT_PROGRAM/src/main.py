# Created by Patrick Archer on 15 April 2019

"""
@file is the main script that the Client will run to query data from the Central Hub.
"""

################################## IMPORTS

import sys
from FirstResponder_struct import firstResponder

################################## MAIN()

def main():

    # display main menu contents and get user's desired cmd selection
    user_cmd = mainMenu()

    # execute corresponding functions depending on user's cmd selection
    mainMenuSelection(user_cmd)

################################## ADDITIONAL FUNCTIONS

# displays main menu content to user
def mainMenu():

    # # debug: create initial firstResponder object to test valid OOP configuration
    # fr1 = firstResponder('001', 'A1', 'F1')
    # print("[CONSOLE] Initial: ", fr1.uuid)
    # fr1.changeClosestAnchor('A2')
    # print("[CONSOLE] Change CA to A2: ", fr1.closest_anchor)
    # fr1.changeCurrentFloor('F3')
    # print("[CONSOLE] Change CF to F2: ", fr1.current_floor)

    print("\n\t~~ MAIN MENU ~~")
    userCMD = input("""
    Please enter a cmd and press return.
    0 - Quit Program
    1 - cmd1
    2 - cmd2
    3 - cmd3
    \n""")

    # # debug
    # print("[CONSOLE] Entered user cmd: ", userCMD)

    return userCMD

# handles what is to be executed depending on what cmd the user selected from the main menu
def mainMenuSelection(cmd):

    # # debug
    # print("mainMenuSelection.cmd = ", cmd)

    # if cmd == 0 (quit), terminate program
    if cmd == '0':
        sys.exit("\n[CONSOLE] Exit command registered. Terminating program now.")
    # if cmd == 1 (cmd1), begin protocol to carry out desired functionality
    elif cmd == '1':
        protocol_cmd1()
    # if cmd == 2 (cmd2), begin protocol to carry out desired functionality
    elif cmd == '2':
        protocol_cmd2()
    # if cmd == 3 (cmd3), begin protocol to carry out desired functionality
    elif cmd == '3':
        protocol_cmd3()
    # if cmd is unknown or invalid, catch error and re-execute main()
    else:
        print("\n[CONSOLE] Invalid command entered. Please try again.")
        main()

# handles mainMenu.cmd1 functionality
def protocol_cmd1():
    print("\n[CONSOLE] Begin execution of protocol_cmd1().")
    main()

# handles mainMenu.cmd2 functionality
def protocol_cmd2():
    print("\n[CONSOLE] Begin execution of protocol_cmd2().")
    main()

# handles mainMenu.cmd3 functionality
def protocol_cmd3():
    print("\n[CONSOLE] Begin execution of protocol_cmd3().")
    main()


################################## SCOPE

if __name__ == '__main__':
    main()

################################## _END_OF_FILE_
