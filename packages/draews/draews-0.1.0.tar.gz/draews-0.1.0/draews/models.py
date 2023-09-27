from pydantic import BaseModel

class BasicModel(BaseModel):
    description: str
    abbreviation: str

class WordClass(BasicModel):
    pass

class UseFrequency(BasicModel):
    pass

class Meaning(BaseModel):
    word_class : WordClass
    use_frequency : list[UseFrequency]
    meaning : str
    
class MeaningList(BaseModel):
    meanings : list[Meaning]