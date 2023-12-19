from setuptools import find_packages, setup

setup(
    name="re_gpt",
    version="2.8.10",
    author="Zai-Kun",
    description="ChatGPT web version in Python. Basically, you can use the ChatGPT API for free without any limitations, just as in the web version.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Zai-Kun/reverse-engineered-chatgpt",
    project_urls={
        "Bug Tracker": "https://github.com/Zai-Kun/reverse-engineered-chatgpt/issues",
    },
    packages=find_packages(),
    install_requires=[
        "curl_cffi==0.5.9",
        "pycryptodome",
        "cryptography",
    ],
)
