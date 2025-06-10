#!/usr/bin/env python3
"""
Restart Flask Application
"""

import subprocess
import sys
import time
import psutil
import os

def kill_flask_processes():
    """Kill any existing Flask processes on port 5001"""
    print("Checking for existing Flask processes...")
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if it's a Python process running our Flask app
            if (proc.info['name'] and 'python' in proc.info['name'].lower() and 
                proc.info['cmdline'] and any('app.py' in arg for arg in proc.info['cmdline'])):
                print(f"Found Flask process: PID {proc.info['pid']}")
                proc.kill()
                print(f"Killed process {proc.info['pid']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Also check for processes using port 5001
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            if proc.info['connections']:
                for conn in proc.info['connections']:
                    if conn.laddr.port == 5001:
                        print(f"Found process using port 5001: PID {proc.info['pid']}")
                        proc.kill()
                        print(f"Killed process {proc.info['pid']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError):
            pass

def start_flask():
    """Start the Flask application"""
    print("\nStarting Flask application...")
    os.chdir(r"c:\Users\prana\Downloads\chatbot_cloud")
    
    # Start Flask in a new process
    process = subprocess.Popen([sys.executable, "app.py"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              text=True)
    
    # Wait a moment and check if it started successfully
    time.sleep(3)
    
    if process.poll() is None:
        print("✅ Flask application started successfully!")
        print("🌐 Admin Panel: http://127.0.0.1:5001/admin")
        print("🔑 Login: admin@supportcenter.com / admin123")
        print("\nPress Ctrl+C to stop the server")
        
        # Keep the process running and show output
        try:
            while True:
                output = process.stdout.readline()
                if output:
                    print(output.strip())
                elif process.poll() is not None:
                    break
        except KeyboardInterrupt:
            print("\nStopping Flask application...")
            process.terminate()
            
    else:
        stdout, stderr = process.communicate()
        print("❌ Flask application failed to start")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)

def main():
    print("=== Flask Application Restart ===")
    
    # Kill existing processes
    kill_flask_processes()
    
    # Wait a moment for processes to die
    time.sleep(2)
    
    # Start Flask
    start_flask()

if __name__ == "__main__":
    main()
