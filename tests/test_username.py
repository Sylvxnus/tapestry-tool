from osint_aggregator.modules.username import determine_exists

def test_status_method_exists():
    assert determine_exists({"method": "status"}, 200, "") is True

def test_status_method_not_found():
    assert determine_exists({"method": "status"}, 404, "") is False

def test_message_method_exists():
    site = {"method": "message", "not_found": "could not be found"}
    assert determine_exists(site, 200, "here is a real profile page") is True

def test_message_method_not_found():
    site = {"method": "message", "not_found": "could not be found"}
    assert determine_exists(site, 200, "The specified profile could not be found.") is False

def test_message_method_ignores_non_200():
    # the real HackerNews rate-limit bug: a 429 shouldn't be trusted even without the phrase
    site = {"method": "message", "not_found": "No such user"}
    assert determine_exists(site, 429, "Sorry.") is False