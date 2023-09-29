from deepaix.common.secure_requests import SecureRequest


def test_secure_header():
    client = SecureRequest()

    header1 = client.get_headers_with_user_agent()
    assert header1["User-Agent"] in client.user_agents_list

    header2 = client.get_headers_with_user_agent()
    assert header2["User-Agent"] in client.user_agents_list

    header3 = client.get_headers_with_user_agent()
    assert header3["User-Agent"] in client.user_agents_list

    assert (
        header1["User-Agent"] != header2["User-Agent"]
        or header2["User-Agent"] != header3["User-Agent"]
    )
