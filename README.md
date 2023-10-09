# flame-ssd-api-server

# Install packages
```
$ sudo apt-get install python3-virtualenv redis-server
$ virtualenv venv --python=3.10
$ source ./venv/bin/activate
```

# Redis server Configuration (optional)
```
$ sudo nano /etc/redis/redis.conf

maxmemory 10g
maxmemory-policy allkey-lru
```

# Server start with Fastapi
```
$ uvicorn server:app --reload
```