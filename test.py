import os


try:
    os.mkdir("photos")
except Exception:
    pass
print("OK")