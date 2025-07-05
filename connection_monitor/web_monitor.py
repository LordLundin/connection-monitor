#!/usr/bin/env python3
"""
Web-based connection monitor with accessible HTML interface
"""

import psutil
import json
import asyncio
import webbrowser
from datetime import datetime
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'connection-monitor-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

monitoring = False
monitor_thread = None


def get_process_name(pid):
    try:
        process = psutil.Process(pid)
        return process.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return "Unknown"


def get_connections():
    connections = []
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'NONE' or not conn.raddr:
                continue
                
            process_name = get_process_name(conn.pid) if conn.pid else "System"
            
            local_addr = f"{conn.laddr.ip}:{conn.laddr.port}"
            remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
            
            connections.append({
                'process': process_name,
                'pid': str(conn.pid) if conn.pid else "N/A",
                'local': local_addr,
                'remote': remote_addr,
                'status': conn.status,
                'timestamp': datetime.now().strftime('%H:%M:%S')
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
                        'status': conn.status,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue
                
    return connections


def monitor_connections():
    global monitoring
    while monitoring:
        connections = get_connections()
        socketio.emit('update_connections', {
            'connections': connections,
            'total': len(connections),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        time.sleep(2)


@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connection Monitor</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        .controls {
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            align-items: center;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            background: #007bff;
            color: white;
            transition: background 0.3s;
        }
        button:hover:not(:disabled) {
            background: #0056b3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        button:focus {
            outline: 2px solid #0056b3;
            outline-offset: 2px;
        }
        .status {
            padding: 10px;
            border-radius: 4px;
            font-weight: 500;
        }
        .status.active {
            background: #d4edda;
            color: #155724;
        }
        .status.inactive {
            background: #f8d7da;
            color: #721c24;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .summary {
            margin-top: 20px;
            padding: 15px;
            background: #e9ecef;
            border-radius: 4px;
            font-size: 14px;
        }
        .alert {
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 4px;
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeeba;
        }
        /* Accessibility improvements */
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            margin: -1px;
            padding: 0;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            table {
                font-size: 14px;
            }
            th, td {
                padding: 8px 4px;
            }
        }
    </style>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
</head>
<body>
    <div class="container">
        <h1>Connection Monitor</h1>
        
        <div class="alert" role="alert" id="permissionAlert" style="display: none;">
            <strong>Note:</strong> Running without elevated privileges. Some system connections may not be visible.
        </div>
        
        <div class="controls">
            <button id="startBtn" onclick="startMonitoring()" aria-label="Start monitoring network connections">
                Start Monitoring
            </button>
            <button id="stopBtn" onclick="stopMonitoring()" disabled aria-label="Stop monitoring network connections">
                Stop Monitoring
            </button>
            <div class="status inactive" id="status" role="status" aria-live="polite">
                Status: <span id="statusText">Stopped</span>
            </div>
        </div>
        
        <div id="connectionTable" role="region" aria-label="Network connections table">
            <table role="table">
                <caption class="sr-only">Active network connections</caption>
                <thead>
                    <tr role="row">
                        <th role="columnheader" scope="col">Process Name</th>
                        <th role="columnheader" scope="col">PID</th>
                        <th role="columnheader" scope="col">Local Address</th>
                        <th role="columnheader" scope="col">Remote Address</th>
                        <th role="columnheader" scope="col">Status</th>
                    </tr>
                </thead>
                <tbody id="connectionsBody" role="rowgroup">
                    <tr role="row">
                        <td role="cell" colspan="5" style="text-align: center; color: #666;">
                            Click "Start Monitoring" to begin
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="summary" id="summary" role="status" aria-live="polite">
            <div>Total connections: <span id="totalConnections">0</span></div>
            <div>Last updated: <span id="lastUpdated">Never</span></div>
        </div>
    </div>
    
    <script>
        const socket = io();
        let isMonitoring = false;
        
        socket.on('connect', function() {
            console.log('Connected to server');
        });
        
        socket.on('update_connections', function(data) {
            updateTable(data.connections);
            document.getElementById('totalConnections').textContent = data.total;
            document.getElementById('lastUpdated').textContent = data.timestamp;
            
            // Announce update to screen readers
            const announcement = `Updated: ${data.total} connections found`;
            announceToScreenReader(announcement);
        });
        
        socket.on('monitoring_started', function() {
            isMonitoring = true;
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            document.getElementById('status').className = 'status active';
            document.getElementById('statusText').textContent = 'Monitoring...';
            announceToScreenReader('Monitoring started');
        });
        
        socket.on('monitoring_stopped', function() {
            isMonitoring = false;
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('status').className = 'status inactive';
            document.getElementById('statusText').textContent = 'Stopped';
            announceToScreenReader('Monitoring stopped');
        });
        
        socket.on('permission_warning', function() {
            document.getElementById('permissionAlert').style.display = 'block';
        });
        
        function startMonitoring() {
            socket.emit('start_monitoring');
        }
        
        function stopMonitoring() {
            socket.emit('stop_monitoring');
        }
        
        function updateTable(connections) {
            const tbody = document.getElementById('connectionsBody');
            tbody.innerHTML = '';
            
            if (connections.length === 0) {
                tbody.innerHTML = '<tr role="row"><td role="cell" colspan="5" style="text-align: center; color: #666;">No active connections found</td></tr>';
                return;
            }
            
            connections.forEach(conn => {
                const row = document.createElement('tr');
                row.setAttribute('role', 'row');
                row.innerHTML = `
                    <td role="cell">${escapeHtml(conn.process)}</td>
                    <td role="cell">${escapeHtml(conn.pid)}</td>
                    <td role="cell">${escapeHtml(conn.local)}</td>
                    <td role="cell">${escapeHtml(conn.remote)}</td>
                    <td role="cell">${escapeHtml(conn.status)}</td>
                `;
                tbody.appendChild(row);
            });
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function announceToScreenReader(message) {
            const announcement = document.createElement('div');
            announcement.setAttribute('role', 'status');
            announcement.setAttribute('aria-live', 'polite');
            announcement.className = 'sr-only';
            announcement.textContent = message;
            document.body.appendChild(announcement);
            setTimeout(() => announcement.remove(), 1000);
        }
    </script>
</body>
</html>
    '''


@socketio.on('start_monitoring')
def handle_start_monitoring():
    global monitoring, monitor_thread
    if not monitoring:
        monitoring = True
        monitor_thread = threading.Thread(target=monitor_connections, daemon=True)
        monitor_thread.start()
        emit('monitoring_started', broadcast=True)
        
        # Check if running with limited permissions
        try:
            list(psutil.net_connections(kind='inet'))
        except (psutil.AccessDenied, PermissionError):
            emit('permission_warning')


@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    global monitoring
    monitoring = False
    emit('monitoring_stopped', broadcast=True)


def main():
    print("Connection Monitor - Web Interface")
    print("-" * 50)
    print(f"Starting web server on http://localhost:5000")
    
    # Check if running on WSL
    is_wsl = os.path.exists('/proc/sys/fs/binfmt_misc/WSLInterop')
    
    if is_wsl:
        print("\nRunning on WSL detected!")
        print("Open this URL in your Windows browser:")
        print("\n  http://localhost:5000\n")
    else:
        print("\nThe browser should open automatically.")
        print("If not, please open http://localhost:5000 in your browser.")
        # Try to open browser after a short delay
        def open_browser():
            time.sleep(1.5)
            webbrowser.open('http://localhost:5000')
        
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
    
    print("Press Ctrl+C to stop the server.")
    
    # Run the web server
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()