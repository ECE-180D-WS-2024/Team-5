import socket
import random
import time

# Function to send a UDP packet
def send_udp_packet():
    # Choose 1 or 2 randomly
    player_no = random.choice([1, 2])
    # Generate a random integer from 0 to 10
    move_num = random.randint(0, 10)
    # Construct the message
    message = f"p{player_no}-Move{move_num}"
    # Select the port based on the value of dollar
    port = 5000 if player_no == 1 else 6000
    
    # IP address you want to send the UDP packet to
    ip_address = "127.0.0.1"  # Using localhost for demonstration; replace with your target IP
    
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Send the message
    sock.sendto(message.encode(), (ip_address, port))
    print(f"Sent message '{message}' to {ip_address}:{port}")
    
    # Close the socket
    sock.close()

# Example usage
while True:
    send_udp_packet()
    time.sleep(1)
