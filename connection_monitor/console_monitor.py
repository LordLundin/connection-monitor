#!/usr/bin/env python3
import psutil
import time
import os
import sys
from datetime import datetime
import threading
from collections import defaultdict


class ConsoleNetworkMonitor:
    def __init__(self):
        self.monitoring = False
        self.connections_data = []
        
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def get_process_name(self, pid):
        try:
            process = psutil.Process(pid)
            return process.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return "Unknown"
    
    def get_connections(self):
        connections = []
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'NONE' or not conn.raddr:
                    continue
                    
                process_name = self.get_process_name(conn.pid) if conn.pid else "System"
                
                local_addr = f"{conn.laddr.ip}:{conn.laddr.port}"
                remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                
                connections.append({
                    'process': process_name,
                    'pid': str(conn.pid) if conn.pid else "N/A",
                    'local': local_addr,
                    'remote': remote_addr,
                    'status': conn.status
                })
        except (psutil.AccessDenied, PermissionError) as e:
            # Try to get at least some connections without root
            print(f"\nNote: Running without root privileges. Some connections may not be visible.")
            print("For full access, run with: sudo python main.py\n")
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    for conn in proc.connections(kind='inet'):
                        if conn.status == 'NONE' or not conn.raddr:
                            continue
                            
                        local_addr = f"{conn.laddr.ip}:{conn.laddr.port}"
                        remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}"
                        
                        connections.append({
                            'process': proc.info['name'],
                            'pid': str(proc.info['pid']),
                            'local': local_addr,
                            'remote': remote_addr,
                            'status': conn.status
                        })
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue
                    
        return connections
    
    def display_connections(self):
        self.clear_screen()
        
        print("=" * 100)
        print(f"CONNECTION MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 100)
        print(f"{'Process':<25} {'PID':<8} {'Local Address':<22} {'Remote Address':<22} {'Status':<12}")
        print("-" * 100)
        
        connections = self.get_connections()
        self.connections_data = connections
        
        if not connections:
            print("\nNo active connections found.")
        else:
            for conn in connections:
                print(f"{conn['process']:<25} {conn['pid']:<8} {conn['local']:<22} {conn['remote']:<22} {conn['status']:<12}")
                
        print("-" * 100)
        print(f"Total connections: {len(connections)}")
        print("\nCommands: [R]efresh | [S]top monitoring | [Q]uit")
        
    def monitor_loop(self):
        while self.monitoring:
            self.display_connections()
            time.sleep(2)
            
    def start(self):
        self.monitoring = True
        
        # Start monitoring in a thread
        monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        monitor_thread.start()
        
        # Handle user input
        try:
            while self.monitoring:
                user_input = input().lower()
                if user_input == 'q':
                    break
                elif user_input == 's':
                    self.monitoring = False
                    print("\nMonitoring stopped. Press Enter to continue...")
                    input()
                    break
                elif user_input == 'r':
                    self.display_connections()
        except KeyboardInterrupt:
            pass
            
        self.monitoring = False
        print("\nExiting...")


def main():
    print("Connection Monitor")
    print("-" * 50)
    print("\nThis tool monitors network connections on your system.")
    print("\nCommands:")
    print("  - Press Enter to start monitoring")
    print("  - Press 'R' + Enter to refresh")
    print("  - Press 'S' + Enter to stop monitoring")
    print("  - Press 'Q' + Enter or Ctrl+C to quit")
    print("\nPress Enter to start...")
    
    input()
    
    monitor = ConsoleNetworkMonitor()
    monitor.start()


if __name__ == "__main__":
    main()