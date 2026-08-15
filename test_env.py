import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
loaded = load_dotenv(dotenv_path=dotenv_path)
print(f".env path={os.path.abspath(dotenv_path)}, loaded={loaded}")

for name in ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']:
    value = os.getenv(name)
    if name == 'DB_PASSWORD':
        print(f"{name}={'SET' if value is not None else 'NOT SET'}")
    else:
        print(f"{name}={value!r}")
