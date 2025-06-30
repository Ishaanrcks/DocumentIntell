from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_type = models.CharField(max_length=10)
    file_size = models.IntegerField()
    processing_status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DocumentChunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    chunk_text = models.TextField()
    chunk_index = models.IntegerField()
    embedding_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
