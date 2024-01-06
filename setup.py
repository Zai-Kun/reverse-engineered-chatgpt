from setuptools import find_packages, setup

setup(
    name="re_gpt",
    version="3.0.1",
    author="Zai-Kun",
    description="Unofficial reverse-engineered ChatGPT API in Python.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Zai-Kun/reverse-engineered-chatgpt",
    project_urls={
        "Bug Tracker": "https://github.com/Zai-Kun/reverse-engineered-chatgpt/issues",
    },
    packages=find_packages(),
    install_requires=["curl_cffi==0.5.9"],
)
