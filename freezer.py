#!/usr/bin/python3

from StorageHandler import StorageHandler
from FreezerTUI import FreezerTUI

version = '0.1'

if __name__ == "__main__":
    print( "Freezer - ein Kühlschrank-Manager (v" + version + ")" )
    print( "-----------------------------------------\n" )
    with StorageHandler( "./freezer.db" ) as db:
        tui = FreezerTUI( db )
        tui.Run()                
