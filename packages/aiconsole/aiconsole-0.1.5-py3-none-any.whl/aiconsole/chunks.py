

class TextChunk:
    def __init__(self, role: str, message: str):
        self.role = role
        self.message = message
    
    def __repr__(self):
        return f"<TextChunk role={self.role!r} message={self.message!r}>"