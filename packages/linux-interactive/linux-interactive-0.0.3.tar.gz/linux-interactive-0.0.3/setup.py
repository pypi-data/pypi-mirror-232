from setuptools import setup

setup(
    name="linux-interactive",
    version="0.0.3",
    py_modules=["linux_interactive"],
    install_requires=[
        "openai>=0.28.0",
    ],
    entry_points={
        "console_scripts": [
            "li=linux_interactive:main",
        ],
    },
    url="https://github.com/ktamulonis/li",
    author="Kurt Tamulonis",
    author_email="kurttamulonis@gmail.com",
)

