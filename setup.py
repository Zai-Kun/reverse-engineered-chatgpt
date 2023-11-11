from setuptools import find_packages, setup

if __name__ == "__main__":
    setup(
        name="re_gpt",
        author='Zai-Kun'
        packages=find_packages(),
        install_requires=["curl_cffi==0.5.9", "pycryptodome", "cryptography"],
    )
