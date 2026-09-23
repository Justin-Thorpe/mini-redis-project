# Mini Redis

A small Redis-inspired in-memory key-value database server built in Python.

This project was created as a learning exercise to better understand how database servers, TCP networking, serialization protocols, asynchronous functions, and client/server communication work.

The implementation uses Python's `asyncio` library to allow clients to communicate with the server over TCP and uses a Redis-inspired serialization protocol for transmitting commands and responses.

## Features

The current implementation supports:

* `PING` — check that the server is running
* `SET key value` — store a key-value pair
* `GET key` — retrieve a value
* `DEL key` — delete a key
* `FLUSH` — remove all stored values
* Asynchronous TCP communication using `asyncio`
* Redis-inspired request and response serialization
* Basic command and protocol error handling
* Multiple commands over the same client connection

Data is currently stored entirely in memory using a Python dictionary.

## Project Structure

```text
mini-redis-project/
├── main.py
├── demo.py
└── src/
    ├── server.py
    ├── client.py
    └── protocol.py
```

### `server.py`

Contains the Redis-like server.

The server:

1. Opens a TCP server
2. Accepts client connections
3. Reads serialized requests
4. Passes requests to the protocol handler
5. Executes the requested command
6. Sends the response back to the client

The key-value database is currently represented by an in-memory Python dictionary.

### `client.py`

Contains a simple asynchronous client for communicating with the server.

The client opens a TCP connection using:

```python
asyncio.open_connection()
```

It sends commands through the protocol handler and waits for responses from the server.

### `protocol.py`

Handles communication between the client and server.

The protocol handler is responsible for converting between Python values and bytes that can be sent over a TCP connection.

For example, a command such as:

```text
SET name your_name
```

is transmitted as an array containing three values:

```text
["SET", "name", "your_name"]
```

The protocol handler serializes those values before sending them and reconstructs them on the receiving side.

Supported protocol types include strings, integers, arrays, errors, null values, and several additional Redis-inspired data types.

## How It Works

A typical request follows this path:

```text
Client
  | SET name your_name
  v
Protocol Serializer
  | bytes
  v
TCP Connection
  v
Server
  v
Protocol Parser
  | ["SET", "name", "your_name"]
  v
Command Handler
  v
In-Memory Dictionary
  | response
  v
Protocol Serializer
  v
Client
```

The client and server share the same protocol implementation so they agree on how messages should be encoded and decoded.

## Running the Project

This project currently uses only the Python standard library using python 3.12.

Clone the repository:

```bash
git clone https://github.com/Justin-Thorpe/mini-redis-project.git
cd mini-redis-project
```

### Start the server

In one terminal:

```bash
python main.py
```

The server will begin listening on:

```text
127.0.0.1:6379
```

### Start the client

Open a second terminal and run:

```bash
python demo.py
```

You can then enter commands such as:

```text
> PING
PONG

> SET name your_name
1

> GET name
your_name

> DEL name
1

> GET name
None
```

Use:

```text
exit
```

to close the client.

## Current Limitations

This is intentionally a small educational implementation rather than a replacement for Redis.

The current version does not include:

* Persistent storage
* Key expiration
* Authentication
* Transactions
* Replication
* Clustering
* Redis data structures such as lists and sorted sets
* Full Redis protocol compatibility

Restarting the server currently clears all data.

## Possible Next Steps

Potential additions include:

* Key expiration
* Append-only persistence
* Additonal commands
* Server logging
* Performance benchmarking

## Purpose

The primary goal of this project is to learn the systems concepts behind tools such as Redis rather than simply use an existing Redis library.

The project provides hands-on experience with:

* TCP networking
* Asynchronous programming
* Client/server architecture
* Serialization and network protocols
* In-memory databases
* Command dispatch
* Error handling
* Python software design

## Inspiration

The initial version of this project was based on Charles Leifer's tutorial, **Building a Simple Redis Server with Python**, and was adapted to use Python's built-in `asyncio` networking tools.

The longer-term goal is to extend and redesign the implementation independently as additional database and systems concepts are learned.
