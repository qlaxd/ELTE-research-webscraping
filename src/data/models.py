import re
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator

HTML_TAG_PATTERN = re.compile(r'<[^>]+>')

class Speech(BaseModel):
    """Represents a single speech act in the parliament."""
    text: str = Field(..., min_length=1, description="The content of the speech.")
    speaker_name: str = Field(..., min_length=1, description="The name of the speaker.")
    chair: int = Field(..., ge=0, le=1, description="Binary flag indicating if the speaker is the chair (Marszałek).")
    agenda_item: Optional[str] = Field(None, description="The agenda item reference.")
    place_agenda: int = Field(..., ge=1, description="The position of the speech within the session's agenda.")
    date: datetime = Field(..., description="The date of the session.")
    session_id: str = Field(..., description="A unique identifier for the session.")

    @validator('text')
    def clean_text(cls, v):
        """Strips whitespace, removes HTML tags, and ensures text is not empty after cleaning."""
        # Replace non-breaking spaces and remove HTML tags
        cleaned_text = v.replace('&nbsp;', ' ')
        cleaned_text = HTML_TAG_PATTERN.sub('', cleaned_text)
        # Normalize whitespace
        cleaned_text = ' '.join(cleaned_text.split()).strip()
        if not cleaned_text:
            raise ValueError("Text cannot be empty after cleaning.")
        return cleaned_text

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d')
        }

class Session(BaseModel):
    """Represents a single parliamentary session."""
    session_id: str = Field(..., description="Unique identifier for the session, e.g., 'session_20100806'.")
    date: datetime = Field(..., description="The date of the session.")
    url: str = Field(..., description="The URL to the session's transcript.")
    speeches: List[Speech] = Field(default_factory=list, description="A list of speeches from the session.")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d')
        }
