from setuptools import setup, find_packages
with open('requirements.txt') as f:
    install_requires = f.read().splitlines()
setup(
    name="CyberU",
    version="0.13.0",
    # packages=find_packages(),
    packages=['CyberU'],
    install_requires=install_requires,
    author="an-Underpriviliged-ZJUer",
    author_email="1737177378@qq.com",
    description="Your spider tool based on selenium and an even general platform based on Python.",
    long_description=open('Kaleidoscope.md','r').read(),
    long_description_content_type="text/markdown",


    url="https://github.com/an-Underpriviliged-ZJUer/Kaleidoscope_public",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        # ...
    ],
)
