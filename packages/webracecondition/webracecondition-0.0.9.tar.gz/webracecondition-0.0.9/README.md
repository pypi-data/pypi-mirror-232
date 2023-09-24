# webracecondition
> Tiny package to test webraceconditions

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
    engine.add_request(Request("GET", "/demo"))

for roundtrip in engine.last_frame_sync_attack():
    print(roundtrip)
```

## Dependant-Streams Attack
```python
from webracecondition import Engine, Request, LongRunningChain

engine = Engine("https://your-target.com")

for i in range(20):
    engine.add_request(Request("GET", "/demo")

chain = LongRunningChain(Request("GET", "/long"))
for i in range(10):
    chain.add_request(chain.root)

for roundtrip in engine.dependant_streams_attack(chain):
    print(roundtrip)
```

## License
[MIT](LICENSE)