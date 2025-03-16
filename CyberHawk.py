from collections import deque
import requests
import argparse
import threading

# ASCII title
ascii_title = ("""
 
 ██████╗██╗   ██╗██████╗ ███████╗██████╗ ██╗  ██╗ █████╗ ██╗    ██╗██╗  ██╗    ██████╗ ██╗██████╗ ███████╗██████╗ ██╗   ██╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██║  ██║██╔══██╗██║    ██║██║ ██╔╝    ██╔══██╗██║██╔══██╗██╔════╝██╔══██╗╚██╗ ██╔╝
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝███████║███████║██║ █╗ ██║█████╔╝     ██║  ██║██║██████╔╝███████╗██████╔╝ ╚████╔╝ 
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██╔══██║██╔══██║██║███╗██║██╔═██╗     ██║  ██║██║██╔══██╗╚════██║██╔═══╝   ╚██╔╝  
╚██████╗   ██║   ██████╔╝███████╗██║  ██║██║  ██║██║  ██║╚███╔███╔╝██║  ██╗    ██████╔╝██║██║  ██║███████║██║        ██║   
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝    ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝╚═╝        ╚═╝   
                                                                                                                           
""")





# Function to check if a directory exists
def check_dir(base_url, directory, timeout, valid_dirs, lock):
    url = f"{base_url}/{directory}.html"
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code != 404:
            with lock:
                valid_dirs.append(url)  # Store the valid directory URL
            print(f"[+] Valid directory found: {url} (Status: {response.status_code})")
    except requests.exceptions.RequestException:
        pass  # Ignore timeout and other connection issues

# Worker function for threading
def worker(base_url, dirs, timeout, thread_id, valid_dirs, lock):
    print(f"[Thread {thread_id}] started") # Prints when thread starts
    while dirs:  # Check if dirs is not empty
        directory = dirs.pop()  # Get the next directory
        check_dir(base_url, directory, timeout, valid_dirs, lock)
    print(f"[Thread {thread_id}] finished") # Prints when thread finishes

# Main function to handle arguments and threading
def main():
    print(ascii_title)
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

    # Initialize the deque as a queue for directories
    dirs = deque(directories)
    valid_dirs = []  # List to store valid directories
    lock = threading.Lock()  # Lock for thread-safe operations

    print(f"[*] Scanning {args.target} with {args.threads} threads...")

    # Start threading
    threads = []
    for i in range(1, args.threads + 1):  # Thread IDs start from 1
        t = threading.Thread(target=worker, args=(args.target, dirs, args.timeout, i, valid_dirs, lock))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()  # Wait for all threads to finish

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
    main()
