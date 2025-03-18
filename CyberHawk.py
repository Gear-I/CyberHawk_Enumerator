from collections import deque
import requests
import argparse
import threading
import urllib.parse

# ASCII title
ascii_title = ("""
 
 ██████╗██╗   ██╗██████╗ ███████╗██████╗ ██╗  ██╗ █████╗ ██╗    ██╗██╗  ██╗    ██████╗ ██╗██████╗ ███████╗██████╗ ██╗   ██╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██║  ██║██╔══██╗██║    ██║██║ ██╔╝    ██╔══██╗██║██╔══██╗██╔════╝██╔══██╗╚██╗ ██╔╝
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝███████║███████║██║ █╗ ██║█████╔╝     ██║  ██║██║██████╔╝███████╗██████╔╝ ╚████╔╝ 
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██╔══██║██╔══██║██║███╗██║██╔═██╗     ██║  ██║██║██╔══██╗╚════██║██╔═══╝   ╚██╔╝  
╚██████╗   ██║   ██████╔╝███████╗██║  ██║██║  ██║██║  ██║╚███╔███╔╝██║  ██╗    ██████╔╝██║██║  ██║███████║██║        ██║   
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝  ╚═╝    ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝╚═╝        ╚═╝   
                                                                                                                           
""")


# Function to validate URL Scheme to support HTTPS
def validate_url(target):
    parsed_url = urllib.parse.urlparse(target)
    if not parsed_url.scheme:
        print("[*] No scheme detected in target. Defaulting to HTTPS.")
        return "https://" + target # Default to HTTPS if no scheme provided
    return target


# Function to chunk a list into balanced sublists
def chunk_list(lst, num_chunks):
    if num_chunks <= 0:
        raise ValueError("Number of chunks must be greater than zero.")

    if not lst:  # Handle empty list case
        return [[] for _ in range(num_chunks)]

    chunk_size = max(1, len(lst) // num_chunks)  # Ensure at least one item per chunk
    chunks = [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

    return chunks


# Function to check if a directory exists
def check_dir(base_url, directory, timeout, valid_dirs, lock):
    url = f"{base_url.rstrip('/')}/{directory}.html" # Proper formatting

    try:

        response = requests.get(url, timeout=timeout)
        if response.status_code != 404:
                valid_dirs.append(url)  # Store the valid directory URL
                print(f"[+] Valid directory found: {url} (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"[-] Error checking {url}: {e}") # Display errors instead of ignoring them


# Worker function for threading
def worker(base_url, dirs, timeout, thread_id, valid_dirs):
    print(f"[Thread {thread_id}] started")
    while dirs:  # Check if there's work left
        try:
            directory = dirs.pop()
        except IndexError:
            break  # Exit thread if queue is empty

        check_dir(base_url, directory, timeout, valid_dirs)

    print(f"[Thread {thread_id}] finished")


# Main function
def main():
    print(ascii_title)
    parser = argparse.ArgumentParser(description="Multi-Threaded Web Directory Enumerator")

    # CLI arguments
    parser.add_argument("target", help="Target IP address or website URL (e.g., http://192.168.1.1)")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to the wordlist file")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads (default: 10)")
    parser.add_argument("-to", "--timeout", type=int, default=5, help="Request timeout in seconds (default: 5)")

    args = parser.parse_args()

    # Normalize URL to include HTTP and HTTPS

    target_url = validate_url(args.target)
    # Read wordlist and create a queue
    try:
        with open(args.wordlist, "r") as file:
            directories = file.read().splitlines()
    except FileNotFoundError:
        print("[-] Error: Wordlist file not found.")
        return

    # Chunk wordlist for thread distribution
    chunks = chunk_list(directories, args.threads)
    valid_dirs = []  # List to store valid directories
    lock = threading.Lock()

    print(f"[*] Scanning {target_url} with {args.threads} threads...")

    # Start threading
    threads = []
    for i in range(1, args.threads + 1):
        if i - 1 >= len(chunks):  # Ensure valid chunk index
            print(f"[-] Skipping thread {i}: No more chunks available.")
            continue

        dirs = deque(chunks[i - 1])  # Convert chunk to a deque for thread-safe pop()
        t = threading.Thread(target=worker, args=(target_url, dirs, args.timeout, valid_dirs))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    # Print valid directories found
    if valid_dirs:
        print("[*] Valid directories found:")
        for valid_dir in valid_dirs:
            print(valid_dir)
    else:
        print("[*] No valid directories found.")

    print("[*] Scan completed.")


if __name__ == "__main__":
    main()
