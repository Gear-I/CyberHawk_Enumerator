from termcolor import colored
import pyfiglet
import time
import requests
import argparse
import threading
import queue


# ASCII title
ascii_title = pyfiglet.figlet_format("""
 
 ██████╗██╗   ██╗██████╗ ███████╗██████╗ ██╗  ██╗ █████╗ ██╗    ██╗██╗  ██╗    ██████╗ ██╗██████╗ ███████╗██████╗ ██╗   ██╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██║  ██║██╔══██╗██║    ██║██║ ██╔╝    ██╔══██╗██║██╔══██╗██╔════╝██╔══██╗╚██╗ ██╔╝
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝███████║███████║██║ █╗ ██║█████╔╝     ██║  ██║██║██████╔╝███████╗██████╔╝ ╚████╔╝ 
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██╔══██║██╔══██║██║███╗██║██╔═██╗     ██║  ██║██║██╔══██╗╚════██║██╔═══╝   ╚██╔╝  
╚██████╗   ██║   ██████╔╝███████╗██║  ██║██║  ██║██║  ██║╚███╔███╔╝██║  ██╗    ██████╔╝██║██║  ██║███████║██║        ██║   
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝    ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝╚═╝        ╚═╝   
                                                                                                                           
""")

colored_title = colored(ascii_title, "green")  # Color of the ASCII title

# Print ASCII title continuously in a separate thread
def print_blinking_title():
    while True:
        print(colored(ascii_title, "green"))
        time.sleep(0.5)  # Blinking speed
        print("\033c", end="")  # Clears screen
        time.sleep(0.5)

# Function to check if a directory exists
def check_dir(base_url, directory, timeout):
    url = f"{base_url}/{directory}.html"
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code != 404:
            valid_dirs.append(url)  # Store the valid directory URL
            print(f"[+] Valid directory found: {url} (Status: {response.status_code})")
    except requests.exceptions.RequestException:
        pass  # Ignore timeout and other connection issues

# Worker function for threading
def worker(base_url, q, timeout, thread_id,valid_dirs):
    print(f"[Thread {thread_id}] started") # Prints when thread starts
    while not q.empty():
        directory = q.get()
        check_dir(base_url, directory, timeout, valid_dirs)
        q.task_done()
        print(f"[Thread {thread_id}] finished") # Prints when thread finishes

# Main function to handle arguments and threading
def main():
    parser = argparse.ArgumentParser(description="Multi-Threaded Web Directory Enumerator")

    # CLI arguments
    parser.add_argument("target", help="Target IP address or website URL (e.g., http://192.168.1.1 or http://example.com)")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to the wordlist file")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads (default: 10)")
    parser.add_argument("-to", "--timeout", type=int, default=5, help="Request timeout in seconds (default: 5)")

    args = parser.parse_args()

    # Read wordlist and create a queue
    try:
        with open(args.wordlist, "r") as file:
            directories = file.read().splitlines()
    except FileNotFoundError:
        print("[-] Error: Wordlist file not found.")
        return

    q = queue.Queue()
    for directory in directories:
        q.put(directory)

        valid_dirs = [] # List to store valid directories

    print(f"[*] Scanning {args.target} with {args.threads} threads...")

    # Start threading
    threads = []
    for i in range(1, args.threads + 1):  # Thread IDs start from 1
        t = threading.Thread(target=worker, args=(i, args.target, q, args.timeout, valid_dirs))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


    for t in threads:
        t.join()

# After all threads complete, print valid directories
    if valid_dirs:
        print("[*] Valid directories found:")
        for valid_dir in valid_dirs:
            print(valid_dir)
    else:
        print("[*] No valid directories found.")
    
    print("[*] Scan completed.")

# Run the script
if __name__ == "__main__":
    # Start the blinking title in a separate thread
    title_thread = threading.Thread(target=print_blinking_title)
    title_thread.daemon = True  # Allow the thread to exit when the main program ends
    title_thread.start()

    # Run the main logic
    main()
