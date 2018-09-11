import sys
import pytest as pytest

from sokkandidater.repository import taxonomy
from sokkandidater.repository import kandidater
from sokkandidater import settings


def find(key, dictionary): #about yield: https://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                if isinstance(d, dict):
                    for result in find(key, d):
                        yield result

#TODO create a test after kandidater._parse_args() is refactored
#def test_parse_args():
#    print('============================', sys._getframe().f_code.co_name, '============================ ')
#    print(kandidater._parse_args())

@pytest.mark.parametrize("yrkesgrupper", ( [], [''] ))
@pytest.mark.parametrize("yrkesomraden", ( [], [''] ))
def test_find_secondary_yrkesroller(yrkesgrupper, yrkesomraden):
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    d = kandidater._find_secondary_yrkesroller(yrkesgrupper, yrkesomraden)
    print(d)
    if (yrkesgrupper == [] or yrkesgrupper == [''] ) and (yrkesomraden == [] or yrkesomraden == ['']) :
        assert d == []

@pytest.fixture()
def sek(yrkesgrupper, yrkesomraden): return kandidater._find_secondary_yrkesroller(yrkesgrupper, yrkesomraden)
# def sekundaryrken(request): return request.param
@pytest.mark.parametrize("yrkesroller", ( [], [''],["yrke1"], ["yrke1", "yrke2"], ["yrke3", ''] ))
@pytest.mark.parametrize("sekundaryrken", ( sek([], ['']) , sek([''],[''] ) , ["sek_y1", "sek_y2" ] , ["sel_y2"], ["sek_y3", ''] ))
def test_build_yrkes_query(yrkesroller, sekundaryrken ):
    print('============================',sys._getframe().f_code.co_name,'============================ ')
    d = kandidater._build_yrkes_query(yrkesroller, sekundaryrken)
    print(d)
    if d == None:
        assert yrkesroller == [] and sekundaryrken == []
        return
    set_values = set(find('value', d))
    assert set(yrkesroller).issubset(set_values)
    assert set(sekundaryrken).issubset(set_values)

# @pytest.mark.skip(reason="test is ready, run later")
@pytest.mark.parametrize("kommunkoder", ( [], ["", "1", "22", "333", "44 44", " ", "ejkod"], [""," "], ["0181"], ["ejkommunkod"],["   "] ))
@pytest.mark.parametrize("lanskoder", ( [], ["", "1", "01","333", " ", "ejkod"], [""," "], ["00"], ["ejlankod"], ["   "] ))
def test_build_plats_query(kommunkoder, lanskoder):
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    d = kandidater._build_plats_query(kommunkoder, lanskoder)
    # {'bool': {'should': [{'term': {'krav.kommun.id': {'value': '0181', 'boost': 5.0}}}, {'term': {'krav.lan.id': {'value': '', 'boost': 1.0}}}, {
    # 'bool': {'must': [{'term': {'krav.lan.id': {'value': '01'}}}], 'must_not': [{'exists': {'field': 'krav.kommun'}}], 'boost': 0.5}}]}}
    additional_lan = [kommunkod[0:2] for kommunkod in kommunkoder if len(kommunkod) > 2]  # two first char if len > 2
    if d == None:
        for kkod in kommunkoder: assert kkod == "" or kkod.isspace()
        assert kommunkoder == [] or additional_lan == []
        return
    set_values = set(find('value', d))
    assert set(kommunkoder).issubset(set_values)
    assert set(lanskoder).issubset(set_values)
    assert set(additional_lan).issubset(set_values)

@pytest.mark.parametrize("lista", ( [], ["1"], ["1", "2", "3"], ["", " "], ["", "1"], ["", "1", "2"] ))
def test_build_worktimeextent_should_query(lista):
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    d = kandidater._build_worktimeextent_should_query(lista)
    # {'bool': {'should': [{'term': {'krav.arbetstidsomfattning.kod': {'value': ''}}}, {'term': {'krav.arbetstidsomfattning.kod': {'value': '0'}}}]}}
    if d == None:
        assert lista in [ ["1"], [] ]
        return
    set_values = set(find('value', d))
    assert set(lista).difference(["1"]).issubset(set_values)

@pytest.mark.parametrize("key", [ "" , " ", "key", "k" ])
@pytest.mark.parametrize("itemlist", ( [], ["item"], ["item1", "item2"], [""] ))
def test_build_bool_should_query(key, itemlist):
    print('============================', sys._getframe().f_code.co_name, '============================ ')
    d = kandidater._build_bool_should_query(key, itemlist)
    # {'bool': {'should': [{'term': {'key': {'value': 'item'}}}]}}
    print (d)
    if d == None:
        assert itemlist == []
        return
    set_values = set(find('value', d))
    assert set(itemlist).issubset(set_values)
    assert key in str(list(find('term',d)))
