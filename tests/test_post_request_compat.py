from unittest.mock import MagicMock

from common.module import Module


def test_post_accepts_ignore_flag(mocker):
    module = Module()
    fake_session = MagicMock()
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_session.post.return_value = fake_response
    mocker.patch("requests.Session", return_value=fake_session)

    response = module.post("https://example.com", json={"ok": True}, check=False, ignore=True)

    assert response is fake_response
