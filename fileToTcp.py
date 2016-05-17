import os
import socket
from collections import namedtuple

CFG_FILE = 'config'
RECV_SIZE_LIST = 'recvs'
INPUT_DIR = 'send'
OUTPUT_DIR = 'recv'

Config = namedtuple('Config', ['host', 'port', 'size'])

def load_config():
    # Rudimentary config file
    data = []
    with open(CFG_FILE) as f:
        for line in f.readlines():
            # Strip comments
            if '#' in line:
                line = line.split('#')[0]

            line = line.strip()

            try:
                data.append(int(line))
                print(line)
            except ValueError:
                if len(line) > 0:
                    data.append(line)
                    print(line)

    # Pad the config with -1's for fields that do not exist
    data += [-1] * (len(Config._fields) - len(data))
    return Config(*data)

def load_sizes(config):
    #
    while config.size == -1:
        yield -1

    # Otherwise read varying sizes from a list
    with open(RECV_SIZE_LIST) as f:
        for size in f.readlines():
            yield size

def tcp_client():
    # Load configuration
    config = load_config()

    # Create connection
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((config.host, config.port))

    # Loop over input data and send
    sizes = load_sizes(config)

    for i, fname in enumerate(os.listdir(INPUT_DIR)):
        with open(os.path.join(INPUT_DIR, fname), 'rb') as f:
            data = f.read()

        client.send(data)
        size = sizes.__next__()
        
        if size == -1:
            continue

        response = client.recv(size)
        with open(os.path.join(OUTPUT_DIR, str(i)), 'wb') as f:
            f.write(response)

if __name__ == '__main__':
    tcp_client()
