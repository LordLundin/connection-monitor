#!/usr/bin/env python3
"""
Connection Monitor - A simple network connection monitoring tool
"""

import sys
import os


def main():
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--console':
            from connection_monitor.console_monitor import main as console_main
            console_main()
            return
    
    # Check what's available
    web_available = False
    wx_available = False
    
    try:
        import flask
        import flask_socketio
        web_available = True
    except ImportError:
        pass
    
    try:
        import wx
        wx_available = True
    except ImportError:
        pass
    
    print("Connection Monitor")
    print("-" * 50)
    print("\nAvailable interfaces:")
    print("1. Console interface (works everywhere)")
    
    options = ['console']
    
    if web_available:
        options.append('web')
        print("2. Web interface (accessible, works in browser)")
    
    if wx_available:
        options.append('wx')
        print(f"{len(options)}. wxPython interface (accessible with screen readers)")
    else:
        print("\nNote: wxPython not installed. To install:")
        print("  See INSTALL_WX.md for instructions")
    
    print(f"\nSelect interface (1-{len([o for o in options if o != 'console'])+1}): ", end='')
    
    try:
        choice = int(input())
    except (ValueError, KeyboardInterrupt):
        print("\nExiting...")
        sys.exit(0)
    
    if choice == 1:
        from connection_monitor.console_monitor import main as console_main
        console_main()
    elif choice == 2 and len(options) > 1:
        selected = options[1]
        if selected == 'web':
            try:
                from connection_monitor.web_monitor import main as web_main
                web_main()
            except Exception as e:
                print(f"\nError starting web interface: {e}")
                print("\nDetailed error information:")
                import traceback
                traceback.print_exc()
                print("\nPress Enter to continue to console interface...")
                input()
                from connection_monitor.console_monitor import main as console_main
                console_main()
        elif selected == 'wx':
            try:
                from connection_monitor.wx_monitor import main as wx_main
                wx_main()
            except Exception as e:
                print(f"\nError starting wxPython interface: {e}")
                print("Falling back to console interface...")
                from connection_monitor.console_monitor import main as console_main
                console_main()
    elif choice == 3 and len(options) > 2:
        # This would be wx if both web and wx are available
        try:
            from connection_monitor.wx_monitor import main as wx_main
            wx_main()
        except Exception as e:
            print(f"\nError starting wxPython interface: {e}")
            print("Falling back to console interface...")
            from connection_monitor.console_monitor import main as console_main
            console_main()
    else:
        print("\nInvalid choice. Starting console interface...")
        from connection_monitor.console_monitor import main as console_main
        console_main()


if __name__ == "__main__":
    main()