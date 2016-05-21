#!/usr/bin/python3

import os

def Resize( text, length, adjustLeft=True ):
    text = str(text)
    if len(text) == length:
        return text

    if len(text) < length:
        if adjustLeft:
            return text.ljust( length )
        else:
            return text.rjust( length )

    if len(text) > length:
        if length > 3:
            return text[:length-3] + "..."
        else:
            return text[:length]

def GetTerminalHeight():
    return os.get_terminal_size()[1]
