from rsidatasciencetools.datautils.clean import fix_lists, fix_percent, fix_reals

def test_fix():

    assert fix_reals('1.0') == 1.0
    assert fix_percent('90.5%') == 0.905
    
def test_fix_lists():
    s = '[1.0, 4.0, -1.9]'
    assert [fix_reals(el) for el in fix_lists(s)] == [1.0, 4.0, -1.9]