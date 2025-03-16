from termcolor import colored
import pyfiglet
import time
import requests
import argparse
import threading
import queue
import os


ascii_title = pyfiglet.figlet_format("""
 
 ██████╗██╗   ██╗██████╗ ███████╗██████╗ ██╗  ██╗ █████╗ ██╗    ██╗██╗  ██╗    ██████╗ ██╗██████╗ ███████╗██████╗ ██╗   ██╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██║  ██║██╔══██╗██║    ██║██║ ██╔╝    ██╔══██╗██║██╔══██╗██╔════╝██╔══██╗╚██╗ ██╔╝
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝███████║███████║██║ █╗ ██║█████╔╝     ██║  ██║██║██████╔╝███████╗██████╔╝ ╚████╔╝ 
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██╔══██║██╔══██║██║███╗██║██╔═██╗     ██║  ██║██║██╔══██╗╚════██║██╔═══╝   ╚██╔╝  
╚██████╗   ██║   ██████╔╝███████╗██║  ██║██║  ██║██║  ██║╚███╔███╔╝██║  ██╗    ██████╔╝██║██║  ██║███████║██║        ██║   
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝    ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝╚═╝        ╚═╝   
                                                                                                                           
""")

colored_title = colored(ascii_title, "green") # Color of the ascii title

print(colored_title)

while True:
    print(colored(ascii_title, "green"))
    time.sleep(0.5) #Blink speed
    print("\033c", end="") # clears screen
    time.sleep(0.5)

# Enumerator Program Below

def check_dir(base_url, directory, timeout):
    url =f"{base_url}/{directory}.html"
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code != 404:
            print(f"[+] Valid directory found: {url} (Status: {response.status_code})")
    except requests.exceptions.RequestException:
        pass  # Ignore timeout and other connection issues

    # Worker function for threading

    def worker(base_url, q, timeout):
        while not q.empty():
            directory = q.get()
            check_directory(base_url, directory, timeout)
            q.task_done()