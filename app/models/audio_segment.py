from pydantic import BaseModel
from datetime import datetime

class AudioSegmentBase(BaseModel):
    segment_index: int
    title: str
    s3_url: str

class AudioSegmentCreate(AudioSegmentBase):
    pass

class AudioSegment(AudioSegmentBase):
    id: int
    document_id: int
    created_at: datetime

    class Config:
        from_attributes = True
