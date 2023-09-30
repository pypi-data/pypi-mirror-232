from cisc_sections.default_section_class import SteelSection
import pandas as pd
from pathlib import Path

class Sections:
    def __init__(self) -> None:
        for key, value in {
            'C':C, 'HP':HP, 'L':L, 'M':M, 'MC':MC, 'S':S, 'SLB':SLB, 'W':W, 'WRF':WRF, 
            'WT':WT, 'WWF':WWF, 'WWT':WWT}.items():
            filename = key +".pkl"
            filepath = Path(__file__).parent / "sections" / filename
            df = pd.read_pickle(filepath)
            setattr(self, key, value(df))
        
class C:
    def __init__(self, section_list: pd.DataFrame) -> None:
        self.section_list = section_list
        for _, row in section_list.iterrows():
            section = SteelSection('WWT')
            section._set_section_properties(dict(row))
            setattr(self, row['Dsg'], section)
        
class HP:
    def __init__(self, section_list: pd.DataFrame) -> None:
        self.section_list = section_list
        for _, row in section_list.iterrows():
            section = SteelSection('WWT')
            section._set_section_properties(dict(row))
            setattr(self, row['Dsg'], section)
        
class L:
    def __init__(self, section_list: pd.DataFrame) -> None:
        self.section_list = section_list
        for _, row in section_list.iterrows():
            section = SteelSection('WWT')
            section._set_section_properties(dict(row))
            setattr(self, row['Dsg'], section)
        
class M:
    def __init__(self, section_list: pd.DataFrame) -> None:
        self.section_list = section_list
        for _, row in section_list.iterrows():
            section = SteelSection('WWT')
            section._set_section_properties(dict(row))
            setattr(self, row['Dsg'], section)

class MC:
    def __init__(self, section_list: pd.DataFrame) -> None:
        self.section_list = section_list
        for _, row in section_list.iterrows():
            section = SteelSection('WWT')
            section._set_section_properties(dict(row))
            setattr(self, row['Dsg'], section)
        
class S:
    def __init__(self, section_list: pd.DataFrame) -> None:
        self.section_list = section_list
        for _, row in section_list.iterrows():
            section = SteelSection('WWT')
            section._set_section_properties(dict(row))
            setattr(self, row['Dsg'], section)

class SLB:
    def __init__(self, section_list: pd.DataFrame) -> None:
        self.section_list = section_list
        for _, row in section_list.iterrows():
            section = SteelSection('WWT')
            section._set_section_properties(dict(row))
            setattr(self, row['Dsg'], section)

class W:
    def __init__(self, section_list: pd.DataFrame) -> None:
        self.section_list = section_list
        for _, row in section_list.iterrows():
            section = SteelSection('WWT')
            section._set_section_properties(dict(row))
            setattr(self, row['Dsg'], section)
        
class WRF:
    def __init__(self, section_list: pd.DataFrame) -> None:
        self.section_list = section_list
        for _, row in section_list.iterrows():
            section = SteelSection('WWT')
            section._set_section_properties(dict(row))
            setattr(self, row['Dsg'], section)

class WT:
    def __init__(self, section_list: pd.DataFrame) -> None:
        self.section_list = section_list
        for _, row in section_list.iterrows():
            section = SteelSection('WWT')
            section._set_section_properties(dict(row))
            setattr(self, row['Dsg'], section)
        
class WWF:
    def __init__(self, section_list: pd.DataFrame) -> None:
        self.section_list = section_list
        for _, row in section_list.iterrows():
            section = SteelSection('WWF')
            section._set_section_properties(dict(row))
            setattr(self, row['Dsg'], section)

class WWT:
    def __init__(self, section_list: pd.DataFrame) -> None:
        self.section_list = section_list
        for _, row in section_list.iterrows():
            section = SteelSection('WWT')
            section._set_section_properties(dict(row))
            setattr(self, row['Dsg'], section)
        
