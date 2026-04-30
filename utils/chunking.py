class TextChunker:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def create_chunks(self, content: list, max_length=800) -> list:
        """Create overlapping text chunks with metadata"""
        chunks = []
        current_text = ""
        
        for item in content:
            text = item['text']
            
            # Split long text blocks
            while len(text) > max_length:
                chunk = text[:max_length]
                chunks.append({
                    'text': chunk,
                    'metadata': item
                })
                text = text[max_length - self.chunk_overlap:]
            
            # Add to current chunk
            if len(current_text) + len(text) > self.chunk_size:
                if current_text:
                    chunks.append({
                        'text': current_text.strip(),
                        'metadata': {'source': 'combined'}
                    })
                current_text = text
            else:
                current_text += " " + text
        
        # Add final chunk
        if current_text:
            chunks.append({
                'text': current_text.strip(),
                'metadata': {'source': 'combined'}
            })
        
        return chunks