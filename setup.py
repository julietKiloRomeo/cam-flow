from setuptools import setup, find_packages

reqs = [
    "kivy",
    "pyperclip",
]

setup(
    name="cam-flow",
    description="Manage testing of flow cells",
    author="jkr",
    author_email="jimmy.kjaersgaard@gmail.com",
    url="",
    install_requires=reqs,
    packages=find_packages(),
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    entry_points={"console_scripts": ["cam-flow = cam_flow:main",],},
)
