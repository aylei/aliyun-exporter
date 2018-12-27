from aliyun_exporter.utils import format_metric, format_period

def test_format_metric():
    assert format_metric("") == ""
    assert format_metric("a.b.c") == "a_b_c"
    assert format_metric("aBcD") == "aBcD"
    assert format_metric(".a.b.c.") == "_a_b_c_"


def test_format_period():
    assert format_period("") == ""
    assert format_period("3000") == "3000"
    assert format_period("5,10,25,50,100,300") == "5"
    assert format_period("300_00,500_00") == "300_00"
