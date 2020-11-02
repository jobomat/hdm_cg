__author__ = 'Aksel'
import pymel.core as pmc
import flexiplaneutils as flx

SETTINGS_DEFAULT = {
    'prefix': 'char',
    'num': 1
}


def build_flexiplane(settings=SETTINGS_DEFAULT):
    """
    builds flexiplane safely
    :param settings: dictionary that holds prefix and number values
    :return:flexiplane global control curve node
    """
    pmc.select(cl=True)
    check = flx.number_check(settings=settings)
    settings = dict(
        settings,
        num=int(check)
    )
    flex = flx.flexiplane(settings)
    return flex


def _py_test():
    test_check = build_flexiplane()
    pmc.select(cl=True)
    test_check2 = build_flexiplane()
    print test_check
    print test_check2
    pmc.delete('char_flexiPlane_curveInfo_1')
    pmc.delete('char_flexiPlane_curveInfo_2')
    pmc.delete([test_check, test_check2])
