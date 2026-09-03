from osint_aggregator.modules.domain import is_valid_subdomain

def test_exact_domain_match():
    assert is_valid_subdomain("example.com", "example.com")

def test_real_subdomain():
    assert is_valid_subdomain("dev.example.com", "example.com")

def test_string_suffix_coincidence_rejected():
    # the real bug we found and fixed: testexample.com is NOT a subdomain of example.com
    assert not is_valid_subdomain("testexample.com", "example.com")
    assert not is_valid_subdomain("m.testexample.com", "example.com")

def test_email_address_rejected():
    assert not is_valid_subdomain("user@example.com", "example.com")

def test_entry_with_space_rejected():
    assert not is_valid_subdomain("as207960 test intermediate - example.com", "example.com")

def test_empty_rejected():
    assert not is_valid_subdomain("", "example.com")