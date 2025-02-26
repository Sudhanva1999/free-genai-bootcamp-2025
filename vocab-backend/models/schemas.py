from typing import List, Dict, Optional
from pydantic import BaseModel, validator, Field

class Word(BaseModel):
    english: str
    marathi: str
    
    @validator('english')
    def english_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('English word must not be empty')
        return v
    
    @validator('marathi')
    def marathi_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Marathi word must not be empty')
        return v

class WordGroup(BaseModel):
    group_name: str
    words: List[Word]
    
    @validator('group_name')
    def group_name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Group name must not be empty')
        return v
    
    @validator('words')
    def words_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Words list must not be empty')
        return v