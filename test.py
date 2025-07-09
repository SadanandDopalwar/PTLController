import subprocess

def ping_ip(ip_address, count=4):
    try:
        # Use the `ping` command with a specified count of packets
        output = subprocess.run(
            ["ping", "-c", str(count), ip_address],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if output.returncode == 0:
            print(f"Ping to {ip_address} successful!")
            print(output.stdout)
        else:
            print(f"Ping to {ip_address} failed.")
            print(output.stderr)
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
ping_ip("8.8.8.8")
