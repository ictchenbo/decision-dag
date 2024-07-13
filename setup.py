# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="decision-dag",
    version="1.0",
    description="提供基于DAG流程图的决策推理服务",
    license="Apache",
    author="chenbo",
    author_email="chenbo01@ict.ac.cn",
    packages=find_packages(),
    install_requires=open("requirements.txt", encoding="utf8").readline(),
    long_description=open("README.md", encoding="utf8").read(),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
    ]
)
