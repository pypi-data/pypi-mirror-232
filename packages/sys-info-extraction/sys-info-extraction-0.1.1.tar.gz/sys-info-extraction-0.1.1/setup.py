from setuptools import setup

setup(
    name="sys-info-extraction",
    version="0.1.1",
    author="mrl",
    author_email="insupport@163.com",
    url="https://github.com/support-yl/sys-info-extraction/blob/main/README.md",
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    description="system information extraction packages",
    packages=['extraction'],
    install_requires=[
        "psutil",
        "pyyaml"
    ]
)
