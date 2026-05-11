import pytest
from modules.search.fofa_api import FoFa
from modules.search.hunter_api import Hunter
from modules.search.quake_api import Quake
from modules.search.shodan_api import ShodanAPI
from modules.datasets.securitytrails_api import SecurityTrailsAPI
from modules.intelligence.virustotal_api import VirusTotalAPI
from common.module_status import ModuleRunStatus

def test_api_key_skip():
    fofa = FoFa('example.com')
    fofa.email = ''
    fofa.key = ''
    fofa.search()
    assert fofa.status == ModuleRunStatus.AUTH_FAILED
    
    hunter = Hunter('example.com')
    hunter.key = ''
    hunter.search()
    assert hunter.status == ModuleRunStatus.AUTH_FAILED
    
    quake = Quake('example.com')
    quake.key = ''
    quake.search()
    assert quake.status == ModuleRunStatus.AUTH_FAILED

    shodan = ShodanAPI('example.com')
    shodan.key = ''
    shodan.search()
    assert shodan.status == ModuleRunStatus.AUTH_FAILED

    st = SecurityTrailsAPI('example.com')
    st.api = ''
    st.query()
    assert st.status == ModuleRunStatus.AUTH_FAILED

    vt = VirusTotalAPI('example.com')
    vt.key = ''
    vt.query()
    assert vt.status == ModuleRunStatus.AUTH_FAILED
