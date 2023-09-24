# webracecondition
> Tiny package to test webraceconditions

:warning: This is for educational purpose. Do not try on live servers without permission!

## Install
```bash
pip install webracecondition
```

## How to use
```python
from webracecondition import Engine, Request

engine = Engine("https://your-target.com")
for i in range(20):
    engine.add_request(Request("GET", "/demo"))

for roundtrip in engine.last_frame_sync_attack():
    print(roundtrip)
```

## License
[MIT](LICENSE)