import bandit
from bandit.core import issue
from bandit.core import test_properties as test


@test.checks("Call")
@test.test_id("TBT001")
def ban_network_requests(context):
    # Define a list of modules that make network requests
    network_modules = [
        "http.client",
        "http.client.HTTPConnection",
        "http.client.HTTPSConnection",
        "http.client.HTTPResponse",
        "urllib",
        "urllib.request",
        "requests",
    ]

    for module in network_modules:
        if context.is_module_imported_like(module):
            return bandit.Issue(
                severity=bandit.HIGH,
                confidence=bandit.HIGH,
                text="Network requests are not allowed.",
            )
