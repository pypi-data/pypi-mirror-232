from cisc_sections.sections import Sections
import pytest

@pytest.fixture(scope='module')
def sections():
    sections = Sections()
    yield sections
    del sections
    
def test_dunder_methods(sections):
    assert int(sections.W.W150x37.A.value) == 4750
    assert int(sections.W.W150x37.A.value * sections.W.W150x37.T.value) == 55100
    assert int(sections.W.W150x37.A * sections.W.W150x37.T) == 55100
    assert sections.L.L102x76x16.Iy < sections.L.L127x127x11.Iy
    assert sections.C.C100x7.D.description == 'Depth of section or height of vertical leg'