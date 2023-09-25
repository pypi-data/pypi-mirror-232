# webracecondition
![Build Status](https://github.com/hupe1980/webracecondition/workflows/Build/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 
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
The Last-Frame-Sync Attack leverages the capabilities of HTTP/2 to induce web race conditions by synchronizing the final frames of multiple requests within a single TCP packet. This technique enables the simultaneous arrival of approximately 20-30 requests at the server, with the exact number depending on the Maximum Segment Size (MSS), all while eliminating the impact of network jitter.
 
```python
from webracecondition import Engine, Request

engine = Engine("https://your-target.com")
for i in range(20):
    engine.add_request(Request("GET", "/race"))

for roundtrip in engine.last_frame_sync_attack():
    print(roundtrip)
```

## Dependent-Streams Attack
The Dependent-Streams Attack leverages HTTP/2's dependent streams feature to induce web race conditions by coordinating the concurrent execution of scheduled requests. It entails dispatching an extensive chain of requests, followed by numerous requests that depend on the final request in the chain.

```python
from webracecondition import Engine, Request, LongRunningChain

engine = Engine("https://your-target.com")

for i in range(20):
    engine.add_request(Request("GET", "/race")

chain = LongRunningChain(Request("GET", "/long"))
for i in range(10):
    chain.add_request(chain.root)

for roundtrip in engine.dependent_streams_attack(chain):
    print(roundtrip)
```

## License
[MIT](LICENSE)