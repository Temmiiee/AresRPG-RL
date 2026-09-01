from rl.bridge import AresBridge
b=AresBridge()
try: print(b.request({"op":"ping"}))
finally: b.close()
