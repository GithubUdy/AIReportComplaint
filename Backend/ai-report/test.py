import sys, site, os
print("🟢 sys.executable =", sys.executable)
try:
    print("🟢 site.getsitepackages() =", site.getsitepackages())
except Exception as e:
    print("⚠️ site.getsitepackages() error:", e)
print("🟢 sys.path:")
for p in sys.path:
    print("   ", p)
