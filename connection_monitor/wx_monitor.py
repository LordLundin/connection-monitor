#!/usr/bin/env python3
"""
wxPython-based connection monitor with accessible interface
"""

import wx
import psutil
import threading
import time
from datetime import datetime


class ConnectionListCtrl(wx.ListCtrl):
    def __init__(self, parent):
        super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        
        # Create columns
        self.InsertColumn(0, "Process Name", width=200)
        self.InsertColumn(1, "PID", width=80)
        self.InsertColumn(2, "Local Address", width=150)
        self.InsertColumn(3, "Remote Address", width=200)
        self.InsertColumn(4, "Status", width=100)
        
    def UpdateConnections(self, connections):
        # Clear existing items
        self.DeleteAllItems()
        
        # Add new items
        for idx, conn in enumerate(connections):
            index = self.InsertItem(idx, conn['process'])
            self.SetItem(index, 1, conn['pid'])
            self.SetItem(index, 2, conn['local'])
            self.SetItem(index, 3, conn['remote'])
            self.SetItem(index, 4, conn['status'])


class NetworkMonitorFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Connection Monitor", size=(900, 600))
        
        self.monitoring = False
        self.monitor_thread = None
        
        self.InitUI()
        self.SetupAccelerators()
        self.Centre()
        
    def InitUI(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Control panel
        control_panel = wx.BoxSizer(wx.HORIZONTAL)
        
        self.start_btn = wx.Button(panel, label="&Start Monitoring")
        self.start_btn.Bind(wx.EVT_BUTTON, self.OnStart)
        control_panel.Add(self.start_btn, 0, wx.ALL, 5)
        
        self.stop_btn = wx.Button(panel, label="S&top Monitoring")
        self.stop_btn.Bind(wx.EVT_BUTTON, self.OnStop)
        self.stop_btn.Enable(False)
        control_panel.Add(self.stop_btn, 0, wx.ALL, 5)
        
        self.status_text = wx.StaticText(panel, label="Status: Stopped")
        control_panel.Add(self.status_text, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        # Add keyboard shortcut hint
        shortcut_text = wx.StaticText(panel, label="(Ctrl+P to toggle)")
        control_panel.Add(shortcut_text, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        vbox.Add(control_panel, 0, wx.ALL | wx.EXPAND, 10)
        
        # Connection list
        self.list_ctrl = ConnectionListCtrl(panel)
        vbox.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 10)
        
        # Summary panel
        self.summary_text = wx.StaticText(panel, label="Total connections: 0")
        vbox.Add(self.summary_text, 0, wx.ALL, 10)
        
        panel.SetSizer(vbox)
        
        # Status bar
        self.CreateStatusBar()
        self.SetStatusText("Ready - Press Ctrl+P to start/stop monitoring")
        
        # Bind close event
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        
    def SetupAccelerators(self):
        # Create accelerator for Ctrl+P
        accel_id = wx.NewIdRef()
        self.Bind(wx.EVT_MENU, self.OnToggleMonitoring, id=accel_id)
        
        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('P'), accel_id)
        ])
        self.SetAcceleratorTable(accel_tbl)
        
    def OnToggleMonitoring(self, event):
        """Toggle monitoring on/off with Ctrl+P"""
        if self.monitoring:
            self.OnStop(event)
        else:
            self.OnStart(event)
            
    def GetProcessName(self, pid):
        try:
            process = psutil.Process(pid)
            return process.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return "Unknown"
    
    def GetConnections(self):
        connections = []
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'NONE' or not conn.raddr:
                    continue
                    
                process_name = self.GetProcessName(conn.pid) if conn.pid else "System"
                
                local_addr = f"{conn.laddr.ip}:{conn.laddr.port}"
                remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                
                connections.append({
                    'process': process_name,
                    'pid': str(conn.pid) if conn.pid else "N/A",
                    'local': local_addr,
                    'remote': remote_addr,
                    'status': conn.status
                })
        except (psutil.AccessDenied, PermissionError):
            # Try per-process connections
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
    
    def MonitorLoop(self):
        while self.monitoring:
            connections = self.GetConnections()
            
            # Update UI in main thread
            wx.CallAfter(self.UpdateUI, connections)
            time.sleep(2)
    
    def UpdateUI(self, connections):
        self.list_ctrl.UpdateConnections(connections)
        self.summary_text.SetLabel(f"Total connections: {len(connections)}")
        self.SetStatusText(f"Last updated: {datetime.now().strftime('%H:%M:%S')} - Press Ctrl+P to stop")
        
    def OnStart(self, event):
        self.monitoring = True
        self.start_btn.Enable(False)
        self.stop_btn.Enable(True)
        self.status_text.SetLabel("Status: Monitoring...")
        self.SetStatusText("Monitoring active - Press Ctrl+P to stop")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.MonitorLoop, daemon=True)
        self.monitor_thread.start()
        
    def OnStop(self, event):
        self.monitoring = False
        self.start_btn.Enable(True)
        self.stop_btn.Enable(False)
        self.status_text.SetLabel("Status: Stopped")
        self.SetStatusText("Monitoring stopped - Press Ctrl+P to start")
        
    def OnClose(self, event):
        self.monitoring = False
        self.Destroy()


class NetworkMonitorApp(wx.App):
    def OnInit(self):
        frame = NetworkMonitorFrame()
        frame.Show()
        return True


def main():
    app = NetworkMonitorApp()
    app.MainLoop()


if __name__ == "__main__":
    main()