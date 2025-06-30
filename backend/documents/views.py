from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from .models import Document
from .rag_engine import RAGEngine
from django.views.decorators.csrf import csrf_exempt
import os
rag_engine = RAGEngine()

@csrf_exempt
@api_view(['GET'])
def get_documents(request):
    documents = Document.objects.all()
    data = [{
        'id': doc.pk,
        'title': doc.title,
        'file_type': doc.file_type,
        'created_at': doc.created_at
    } for doc in documents]
    return Response(data)

@api_view(['POST'])
def upload_document(request):
    """Upload and process document"""
    try:
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=400)
        
        print(f"DEBUG: Received file: {file.name}, size: {file.size}")
        
        # Save file
        file_path = default_storage.save(file.name, file)
        full_file_path = default_storage.path(file_path)
        
        print(f"DEBUG: Saved to: {full_file_path}")
        print(f"DEBUG: File exists: {os.path.exists(full_file_path)}")
        
        # Create document record
        document = Document.objects.create(
            title=file.name,
            file_path=file_path,
            file_type=file.name.split('.')[-1],
            file_size=file.size,
            processing_status='processing'
        )
        
        print(f"DEBUG: Created document record ID: {document.id}")
        
        # Process document
        success, message = rag_engine.process_document(document.id, full_file_path)
        
        print(f"DEBUG: Processing result - Success: {success}")
        print(f"DEBUG: Processing message: {message}")
        
        if success:
            document.processing_status = 'completed'
            document.save()
            
            # Double-check ChromaDB
            collection_count = rag_engine.collection.count()
            print(f"DEBUG: ChromaDB count after processing: {collection_count}")
            
            return Response({
                'id': document.id,
                'status': 'uploaded',
                'message': message,
                'chromadb_count': collection_count
            })
        else:
            # Mark as failed and return the actual error
            document.processing_status = 'failed'
            document.save()
            
            print(f"DEBUG: Processing failed: {message}")
            
            return Response({
                'error': f'Processing failed: {message}'
            }, status=500)
            
    except Exception as e:
        print(f"DEBUG: Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': f'Upload failed: {str(e)}'}, status=500)


@csrf_exempt
@api_view(['POST'])
def query_document(request):
    document_id = request.data.get('document_id')
    question = request.data.get('question')
    
    if not question:
        return Response({'error': 'Question required'}, status=400)
    
    answer = rag_engine.query_documents(question, document_id)
    print(f"Answer generated: {answer}")
    return Response({'answer': answer})

@csrf_exempt
@api_view(['GET'])
def debug_status(request):
    """Debug endpoint to check system status"""
    try:
        # Check database
        documents = Document.objects.all()
        db_count = documents.count()
        
        # Check ChromaDB
        collection_count = rag_engine.collection.count()
        
        # Get document details
        doc_details = []
        for doc in documents:
            doc_details.append({
                'id': doc.id,
                'title': doc.title,
                'status': doc.processing_status,
                'file_path': doc.file_path
            })
        
        return Response({
            'database_documents': db_count,
            'chromadb_items': collection_count,
            'documents': doc_details
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
def reprocess_document(request, document_id):
    """Reprocess a specific document"""
    try:
        document = Document.objects.get(id=document_id)
        full_file_path = default_storage.path(document.file_path)
        
        document.processing_status = 'processing'
        document.save()
        
        success, message = rag_engine.process_document(document.id, full_file_path)
        
        if success:
            document.processing_status = 'completed'
        else:
            document.processing_status = 'failed'
        
        document.save()
        
        return Response({
            'success': success,
            'message': message,
            'chromadb_count': rag_engine.collection.count()
        })
        
    except Document.DoesNotExist:
        return Response({'error': 'Document not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
