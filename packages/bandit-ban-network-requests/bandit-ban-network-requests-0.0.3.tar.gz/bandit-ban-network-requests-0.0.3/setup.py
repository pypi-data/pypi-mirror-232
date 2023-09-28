from setuptools import find_packages, setup

setup(
    name="bandit-ban-network-requests",
    version="0.0.3",
    description="Ban all network requests.",
    long_description="A bandit plugin that will ban all network requests.",
    # url="....",
    packages=["bandit_plugins"],
    author="Asad Iqbal",
    install_requires=[
        "bandit",
    ],
    entry_points={
        "bandit.plugins": [
            "ban_network_requests = bandit_plugins.ban_network_requests:ban_network_requests"
        ],
    },
)
