from setuptools import setup, Extension

module = Extension("sharedmutexwin", sources=["sharedmutexwin.cpp"])

setup(
    name="sharedmutexwin",
    version="2.0.0",  # Replace with your desired version number
    description="InterlockedCompareExchange64 wrapper for windows",
    ext_modules=[module],    
)