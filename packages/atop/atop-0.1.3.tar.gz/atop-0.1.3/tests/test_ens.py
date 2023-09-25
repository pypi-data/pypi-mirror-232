import pytest
from src.atop.atop import Ton_retriever
from src.atop.modules.telegramhelper import TelegramHelper

@pytest.fixture
def domains_ens_test():
    return ["vitalik.eth", "ahahahahahjdhassjkgsdajkhsdga.eth"]

def test_ipf2ens_ok(domains_ens_test):
    ipfs = Ton_retriever.ipf_ens(domains_ens_test[0])
    assert ipfs != ""

def test_ipf2ens_no(domains_ens_test):
    ipfs = Ton_retriever.ipf_ens(domains_ens_test[1])
    assert ipfs == ""

def test_web_client():
    result =  TelegramHelper.parse_html_page("https://t.me/aaarghhh")
    assert "user" == result["kind"]
    result = TelegramHelper.parse_html_page("https://t.me/testcanalebla")
    assert "channel" == result["kind"]
    result = TelegramHelper.parse_html_page("https://t.me/gruppotest01")
    assert "group" == result["kind"]




