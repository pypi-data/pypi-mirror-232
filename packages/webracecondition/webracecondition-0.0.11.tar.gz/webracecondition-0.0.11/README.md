# webracecondition
> Tiny package to test webraceconditions

Web race conditions, also known as web application race conditions or simply race conditions, refer to a class of software vulnerabilities that can occur in web applications when multiple users or processes attempt to access and modify shared resources or data concurrently. These vulnerabilities arise due to the unpredictable interleaving of execution threads or processes, and they can lead to unintended and potentially harmful consequences.

In a web race condition scenario, two or more actions that depend on each other's state may interfere with each other when executed concurrently. This interference can result in unexpected behavior, data corruption, or security breaches. Common examples of web race conditions include issues related to session management, data updates, file access, and database transactions.

Developers need to be aware of the potential for race conditions in web applications and implement proper synchronization mechanisms, such as locks, semaphores, or transactions, to ensure safe and consistent access to shared resources. Failing to address race conditions can leave web applications vulnerable to data inconsistency, security vulnerabilities, and unreliable behavior. Therefore, thorough testing and code review are essential to identify and mitigate web race conditions in web applications to maintain their reliability and security.

:warning: This is for educational purpose. Do not try on live servers without permission!

## Install
```bash
pip install webracecondition
```

## Last-Frame-Sync Attack
```python
from webracecondition import Engine, Request

engine = Engine("https://your-target.com")
for i in range(20):
    engine.add_request(Request("GET", "/race"))

for roundtrip in engine.last_frame_sync_attack():
    print(roundtrip)
```

## Dependant-Streams Attack
```python
from webracecondition import Engine, Request, LongRunningChain

engine = Engine("https://your-target.com")

for i in range(20):
    engine.add_request(Request("GET", "/race")

chain = LongRunningChain(Request("GET", "/long"))
for i in range(10):
    chain.add_request(chain.root)

for roundtrip in engine.dependant_streams_attack(chain):
    print(roundtrip)
```

## License
[MIT](LICENSE)