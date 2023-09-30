from dataclasses import dataclass
from functools import cached_property
from typing import Literal, Union
import json
from pathlib import Path
import forallpeople as si
si.environment('default', top_level=False)

SectionPropertyValue = Union[si.Physical, float, str]

class SectionProperty:
    def __init__(self, notation: str, value: SectionPropertyValue, 
                    title: str,description: str, alternate_notation: str) -> None:
        self.notation: str = notation
        self.value: SectionPropertyValue = value
        self.title: str = title
        self.description: str = description
        self.alternate_notation: str = alternate_notation
        
    def __str__(self) -> str:
        return (f'SectionProperty(notation={self.notation}, value={self.value}, '
                f'title={self.title}, description={self.description}, '
                f'alternate_notation={self.alternate_notation})')
        
    def __repr__(self) -> str:
        return self.__str__()
    
    def __lt__(self, other) -> bool:
        if isinstance(self.value, float) or isinstance(self.value, si.Physical): 
            if isinstance(other, SectionProperty):
                return self.value < other.value
            elif isinstance(other, type(self.value)):
                return self.value < other.value
        raise Exception(f'Cannot compare instance of {type(other)}({other}) with {type(self.value)}({self.value})')
    
    def __gt__(self, other) -> bool:
        if isinstance(self.value, float) or isinstance(self.value, si.Physical): 
            if isinstance(other, SectionProperty):
                return self.value > other.value
            elif isinstance(other, type(self.value)):
                return self.value > other.value
        raise Exception(f'Cannot compare instance of {type(other)}({other}) with {type(self.value)}({self.value})')

    def __le__(self, other) -> bool:
        if isinstance(self.value, float) or isinstance(self.value, si.Physical): 
            if isinstance(other, SectionProperty):
                return self.value <= other.value
            elif isinstance(other, type(self.value)):
                return self.value <= other.value
        raise Exception(f'Cannot compare instance of {type(other)}({other}) with {type(self.value)}({self.value})')
    
    def __ge__(self, other) -> bool:
        if isinstance(self.value, float) or isinstance(self.value, si.Physical): 
            if isinstance(other, SectionProperty):
                return self.value >= other.value
            elif isinstance(other, type(self.value)):
                return self.value >= other.value
        raise Exception(f'Cannot compare instance of {type(other)}({other}) with {type(self.value)}({self.value})')

    def __eq__(self, other) -> bool:
        if isinstance(self.value, float) or isinstance(self.value, si.Physical): 
            if isinstance(other, SectionProperty):
                return self.value == other.value
            elif isinstance(other, type(self.value)):
                return self.value == other.value
        raise Exception(f'Cannot compare instance of {type(other)}({other}) with {type(self.value)}({self.value})')

    def __add__(self, other) -> float|si.Physical:
        if isinstance(self.value, float) or isinstance(self.value, si.Physical): 
            if isinstance(other, SectionProperty):
                return self.value + other.value
            elif isinstance(other, type(self.value)):
                return self.value + other.value
        raise Exception(f'Cannot Add instance of {type(other)}({other}) with {type(self.value)}({self.value})')
    
    def __sub__(self, other) -> float|si.Physical:
        if isinstance(self.value, float) or isinstance(self.value, si.Physical): 
            if isinstance(other, SectionProperty):
                return self.value - other.value
            elif isinstance(other, type(self.value)):
                return self.value - other.value
        raise Exception(f'Cannot Subtract instance of {type(other)}({other}) with {type(self.value)}({self.value})')
    
    def __mul__(self, other) -> float|si.Physical:
        if isinstance(self.value, float) or isinstance(self.value, si.Physical): 
            if isinstance(other, SectionProperty):
                return self.value * other.value
            elif isinstance(other, type(self.value)):
                return self.value * other.value
        raise Exception(f'Cannot Multiply instance of {type(other)}({other}) with {type(self.value)}({self.value})')
    
    def __pow__(self, other) -> float|si.Physical:
        if isinstance(self.value, float) or isinstance(self.value, si.Physical): 
            if isinstance(other, SectionProperty):
                return self.value ** other.value
            elif isinstance(other, type(self.value)):
                return self.value ** other.value
        raise Exception(f'Cannot pow instance of {type(other)}({other}) with {type(self.value)}({self.value})')
    
    
    def __neg__(self) -> float|si.Physical:
        if isinstance(self.value, float) or isinstance(self.value, si.Physical): 
            return -1 * self.value
        raise Exception()
    
    def __pos__(self) -> float|si.Physical:
        if isinstance(self.value, float) or isinstance(self.value, si.Physical): 
            return 1 * self.value
        raise Exception()
    
    def __abs__(self) -> float|si.Physical:
        if isinstance(self.value, float) or isinstance(self.value, si.Physical): 
            return abs(self.value)
        raise Exception()
    
class SteelSection:
    def __init__(self, 
                section_type: Literal['W', '2L', 'C', 'HP', 'HSS', 'L', 'M', 'MC', 'S',
                                        'SLB', 'WRF', 'WT', 'WWF', 'WWT']) -> None:
        self.type = section_type
        return
    
    def __str__(self) -> str:
        return f'Instance of SteelSection class for {self.Dsg.value} section'
    
    def __repr__(self) -> str:
        return f'SteelSection({self.Dsg.value}) for {self.type} section'

    @cached_property
    def descriptions(self) -> dict:
        title_json_path: Path = Path(__file__).parent / "sections" / 'title.json'
        with open(title_json_path, 'r') as f:
            return json.load(f)
        
    def section_property(self, notation: str, value: SectionPropertyValue) -> SectionProperty:
        data: dict = self.descriptions.get(notation, None)
        assert data is not None, f'{notation} is not a valid property header'
        return SectionProperty(
            notation = notation, value=value, title= data.get('title', ''), 
            description=data.get('description', data.get('title')), 
            alternate_notation=data.get('alternate', notation)
        )
        
    def _set_section_properties(self, properties: dict[str, SectionPropertyValue]) -> None:
        for prop_name, value in properties.items():
            setattr(self,prop_name,self.section_property(prop_name, value))
        