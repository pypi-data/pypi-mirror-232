from setuptools import find_packages
from setuptools import setup

# Read requirements.txt, ignore comments
try:
    REQUIRES = list()
    f = open("requirements.txt", "rb")
    for line in f.read().decode("utf-8").split("\n"):
        line = line.strip()
        if "#" in line:
            line = line[: line.find("#")].strip()
        if line:
            REQUIRES.append(line)
except FileNotFoundError:
    print("'requirements.txt' not found!")
    REQUIRES = list()

setup(
    name='RL-ADN',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[

    ],
    author='Hou Shengren, Gao Shuyi, Pedro Vargara',
    author_email='houshengren97@gmail.com',
    description='RL-ADN: A Benchmark Framework for DRL-based Battery Energy Arbitrage in Distribution Networks',
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/power_network_rl",
    license='MIT',  # or any license you're using
    keywords='DRL energy arbitrage',
)
