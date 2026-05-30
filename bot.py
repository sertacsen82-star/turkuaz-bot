

rare-blessing

production



30 days or $5.00 left


Agent




turkuaz-bot
Deployments
Variables
Metrics
Settings
Unexposed service
3.13.13python@3.13.13
US West
1 Replica




History

Hide Skipped


turkuaz-bot
/
21fc5c12
Completed

May 30, 2026, 7:03 PM GMT+3
Details
Build Logs
Deploy Logs
Network Flow Logs
Search build logs

You reached the start of the range
May 30, 2026, 6:58 PM
scheduling build on Metal builder "production-builderv3-us-west1-szjs"
unpacking archive
10 KB
uploading snapshot
312 B
using build driver railpack-v0.24.0
                   
╭─────────────────╮
│ Railpack 0.24.0 │
╰─────────────────╯
 
  ↳ Detected Python
  ↳ Using pip
            
  Packages  
  ──────────
  python  │  3.13.13  │  railpack default (3.13)
            
  Steps     
  ──────────
  ▸ install
    $ python -m venv /app/.venv
    $ pip install -r requirements.txt
            
  Deploy    
  ──────────
    $ python bot.py
 

load build definition from ./railpack-plan.json
0ms

install mise packages: python
2s
mise python@3.13.13 ✓ installed

python -m venv /app/.venv
3s

copy requirements.txt
133ms

pip install -r requirements.txt
4s
Successfully installed annotated-types-0.7.0 anthropic-0.105.2 anyio-4.13.0 certifi-2026.5.20 distro-1.9.0 docstring-parser-0.18.0 h11-0.16.0 httpcore-1.0.9 httpx-0.28.1 idna-3.17 jiter-0.15.0 pydantic-2.13.4 pydantic-core-2.46.4 python-telegram-bot-22.7 sniffio-1.3.1 typing-extensions-4.15.0 typing-inspection-0.4.2

copy / /app, /app/.venv
1s

copy /usr/local/bin/mise, /mise/installs, /mise/shims, /root/.local/state/mise, /etc/mise/config.toml, /app cached
64ms

exporting to docker image format
764ms
containerimage.digest: sha256:306ee7e4856b3e8dd9d8ef125cb2f6cb13d85ec4f74bda02c13282fbf8e378e6
containerimage.descriptor: eyJtZWRpYVR5cGUiOiJhcHBsaWNhdGlvbi92bmQub2NpLmltYWdlLm1hbmlmZXN0LnYxK2pzb24iLCJkaWdlc3QiOiJzaGEyNTY6MzA2ZWU3ZTQ4NTZiM2U4ZGQ5ZDhlZjEyNWNiMmY2Y2IxM2Q4NWVjNGY3NGJkYTAyYzEzMjgyZmJmOGUzNzhlNiIsInNpemUiOjIwMDUsImFubm90YXRpb25zIjp7Im9yZy5vcGVuY29udGFpbmVycy5pbWFnZS5jcmVhdGVkIjoiMjAyNi0wNS0zMFQxNjowMzoyN1oifSwicGxhdGZvcm0iOnsiYXJjaGl0ZWN0dXJlIjoiYW1kNjQiLCJvcyI6ImxpbnV4In19
containerimage.config.digest: sha256:e658209a67cb9a958fa735c0ce0b4e809f54125486e710141b779e4a513fead4
image push
106.1 MB
7.0s

