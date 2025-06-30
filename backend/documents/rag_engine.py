import chromadb
from sentence_transformers import SentenceTransformer
import requests
import json
import os
from pathlib import Path

class RAGEngine:
    def __init__(self):
        try:
            # Using persistent client instead of in-memory client
            self.client = chromadb.PersistentClient(path="./chromadb_data")
            
            # Getting or creating collection
            try:
                self.collection = self.client.get_collection("documents")
                print("DEBUG: Retrieved existing ChromaDB collection")
            except:
                self.collection = self.client.create_collection("documents")
                print("DEBUG: Created new ChromaDB collection")
                
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            self.ollama_url = "http://localhost:11434/api/generate"
            
            initial_count = self.collection.count()
            print(f"DEBUG: RAG Engine initialized. Collection count: {initial_count}")
            
        except Exception as e:
            print(f"DEBUG: Error initializing RAG engine: {e}")
            import traceback
            traceback.print_exc()
            raise

        
    def chunk_text(self, text, chunk_size=500):
        """Smart chunking by character count with sentence preservation"""
        if not text or len(text) <= chunk_size:
            return [text] if text else []
            
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # If we're at the end, take the rest
            if end >= len(text):
                chunks.append(text[start:])
                break
                
            # Trying to find a sentence boundary near the chunk size
            chunk_text = text[start:end]
            
            # Looking for sentence endings
            for punct in ['. ', '! ', '? ', '\n\n']:
                last_punct = chunk_text.rfind(punct)
                if last_punct > chunk_size * 0.7:  # At least 70% of chunk size
                    end = start + last_punct + len(punct)
                    break
            
            chunks.append(text[start:end].strip())
            start = end
            
        return [chunk for chunk in chunks if chunk.strip()]
    
    def read_file_content(self, file_path):
        """Read content from uploaded file"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Handle different file types
            if file_path.suffix.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif file_path.suffix.lower() == '.pdf':
                # You can add PDF reading here if needed
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text() + "\n"
                        return text
                except ImportError:
                    return "PDF reading requires PyPDF2. Please install: pip install PyPDF2"
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                # You can add Word document reading here if needed
                try:
                    from docx import Document
                    doc = Document(file_path)
                    text = ""
                    for paragraph in doc.paragraphs:
                        text += paragraph.text + "\n"
                    return text
                except ImportError:
                    return "Word document reading requires python-docx. Please install: pip install python-docx"
            else:
                # Try to read as plain text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
                    
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def process_document(self, document_id, file_path):
        """Process and store document chunks from file path"""
        try:
            print(f"DEBUG: Processing document {document_id} from {file_path}")
            
            # Check file existence
            if not os.path.exists(file_path):
                error_msg = f"File not found: {file_path}"
                print(f"DEBUG: {error_msg}")
                return False, error_msg
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                print(f"DEBUG: Successfully read {len(text)} characters")
            except Exception as e:
                error_msg = f"Error reading file: {str(e)}"
                print(f"DEBUG: {error_msg}")
                return False, error_msg
            
            if not text.strip():
                return False, "File is empty"
            
            print(f"DEBUG: Content preview: {text[:200]}...")
            
            # Clean existing chunks
            try:
                existing_results = self.collection.query(
                    query_embeddings=self.encoder.encode(["dummy"]).tolist(),
                    n_results=1000,
                    where={"document_id": str(document_id)}
                )
                
                if existing_results.get('ids') and existing_results['ids'][0]:
                    self.collection.delete(ids=existing_results['ids'][0])
                    print(f"DEBUG: Deleted {len(existing_results['ids'][0])} existing chunks")
            except Exception as e:
                print(f"DEBUG: Error cleaning existing chunks: {e}")
            
            # Chunk text
            try:
                chunks = self.chunk_text(text)
                print(f"DEBUG: Created {len(chunks)} chunks")
                
                if not chunks:
                    return False, "No chunks created from text"
                    
                # Show sample chunks
                for i, chunk in enumerate(chunks[:2]):
                    print(f"DEBUG: Chunk {i}: {chunk[:100]}...")
                    
            except Exception as e:
                error_msg = f"Error chunking text: {str(e)}"
                print(f"DEBUG: {error_msg}")
                return False, error_msg
            
            # Generate embeddings
            try:
                embeddings = self.encoder.encode(chunks)
                print(f"DEBUG: Generated embeddings with shape: {embeddings.shape}")
            except Exception as e:
                error_msg = f"Error generating embeddings: {str(e)}"
                print(f"DEBUG: {error_msg}")
                return False, error_msg
            
            # Prepare data for ChromaDB
            try:
                chunk_ids = []
                chunk_documents = []
                chunk_embeddings = []
                chunk_metadatas = []
                
                for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    if not chunk.strip():  # Skip empty chunks
                        continue
                        
                    chunk_id = f"{document_id}_{i}"
                    chunk_ids.append(chunk_id)
                    chunk_documents.append(chunk)
                    chunk_embeddings.append(embedding.tolist())
                    chunk_metadatas.append({
                        "document_id": str(document_id),
                        "chunk_index": i,
                        "chunk_length": len(chunk)
                    })
                
                print(f"DEBUG: Prepared {len(chunk_ids)} items for ChromaDB storage")
                
                if not chunk_ids:
                    return False, "No valid chunks to store"
                    
            except Exception as e:
                error_msg = f"Error preparing data: {str(e)}"
                print(f"DEBUG: {error_msg}")
                return False, error_msg
            
            # Store in ChromaDB
            try:
                print("DEBUG: Attempting to add to ChromaDB...")
                
                self.collection.add(
                    ids=chunk_ids,
                    embeddings=chunk_embeddings,
                    documents=chunk_documents,
                    metadatas=chunk_metadatas
                )
                
                print("DEBUG: Successfully added to ChromaDB")
                
            except Exception as e:
                error_msg = f"Error storing in ChromaDB: {str(e)}"
                print(f"DEBUG: {error_msg}")
                import traceback
                traceback.print_exc()
                return False, error_msg
            
            # Verify storage
            try:
                final_count = self.collection.count()
                print(f"DEBUG: Collection now has {final_count} total items")
                
                # Test retrieval
                test_results = self.collection.query(
                    query_embeddings=self.encoder.encode(["test"]).tolist(),
                    n_results=1,
                    where={"document_id": str(document_id)}
                )
                
                retrieved_count = len(test_results['documents'][0]) if test_results['documents'][0] else 0
                print(f"DEBUG: Can retrieve {retrieved_count} chunks for document {document_id}")
                
            except Exception as e:
                print(f"DEBUG: Error verifying storage: {e}")
            
            return True, f"Successfully processed {len(chunk_ids)} chunks"
            
        except Exception as e:
            error_msg = f"Unexpected error in process_document: {str(e)}"
            print(f"DEBUG: {error_msg}")
            import traceback
            traceback.print_exc()
            return False, error_msg
    


    
    # def query_documents(self, question, document_id=None, n_results=3):
    #     """Query documents and generate answer"""
    #     try:
    #         if not question.strip():
    #             return "Please provide a valid question."
            
    #         # Generate question embedding
    #         question_embedding = self.encoder.encode([question])
            
    #         # Build where clause for filtering
    #         where_clause = {"document_id": str(document_id)} if document_id else None
            
    #         # Query ChromaDB
    #         results = self.collection.query(
    #             query_embeddings=question_embedding.tolist(),
    #             n_results=n_results,
    #             where=where_clause
    #         )
            
    #         # Check if we found any results
    #         if not results['documents'] or not results['documents'][0]:
    #             if document_id:
    #                 return f"No relevant content found in the selected document for your question: '{question}'"
    #             else:
    #                 return f"No relevant documents found to answer your question: '{question}'"
            
    #         # Combine context from retrieved chunks
    #         context_chunks = results['documents'][0]
    #         context = "\n\n".join(context_chunks)
            
    #         # Generate answer using the context
    #         return self.generate_answer(question, context)
            
    #     except Exception as e:
    #         return f"Error querying documents: {str(e)}"
    
    def generate_answer(self, question, context):
        """Generate answer using local Ollama model"""
        prompt = f"""Based on the following context from the document(s), provide a clear and accurate answer to the question. If the context doesn't contain enough information to answer the question, say so.

        Context:
        {context}

        Question: {question}

        Answer:"""

        try:
                    payload = {
                        "model": "llama2",
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "top_p": 0.9,
                            "num_tokens": 300
                        }
                    }
                    
                    response = requests.post(self.ollama_url, json=payload, timeout=60)
                    
                    if response.status_code == 200:
                        result = response.json()
                        answer = result.get('response', 'No response generated')
                        
                        # Clean up the answer
                        if answer:
                            return answer.strip()
                        else:
                            return "I couldn't generate a proper answer based on the provided context."
                    else:
                        return f"Error: Ollama returned status {response.status_code}. Make sure Ollama is running with llama2 model."
                        
        except requests.exceptions.ConnectionError:
                    return "Error: Cannot connect to Ollama. Make sure Ollama is running on localhost:11434"
        except requests.exceptions.Timeout:
                    return "Error: Request timed out. The model might be taking too long to respond."
        except Exception as e:
                    return f"Error generating answer: {str(e)}"

    def query_documents(self, question, document_id=None, n_results=3):
        """Query documents and generate answer with debugging"""
        try:
            if not question.strip():
                return "Please provide a valid question."
            
            # DEBUG: Check collection status
            try:
                collection_count = self.collection.count()
                print(f"DEBUG: Collection has {collection_count} items")
            except Exception as e:
                print(f"DEBUG: Error getting collection count: {e}")
                return "Error: Cannot access document collection"
            
            # If collection is empty, return early
            if collection_count == 0:
                return "No documents have been uploaded and processed yet. Please upload a document first."
            
            # Generate question embedding
            question_embedding = self.encoder.encode([question])
            print(f"DEBUG: Question embedding shape: {question_embedding.shape}")
            
            # Build where clause for filtering
            where_clause = {"document_id": str(document_id)} if document_id else None
            print(f"DEBUG: Where clause: {where_clause}")
            
            # DEBUG: Check if specific document exists in collection
            if document_id:
                try:
                    # Query for any chunks with this document_id
                    test_results = self.collection.query(
                        query_embeddings=question_embedding.tolist(),
                        n_results=1,
                        where={"document_id": str(document_id)}
                    )
                    if not test_results['documents'] or not test_results['documents'][0]:
                        return f"Document ID {document_id} not found in the collection. The document may not have been processed correctly."
                except Exception as e:
                    print(f"DEBUG: Error testing document existence: {e}")
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=question_embedding.tolist(),
                n_results=n_results,
                where=where_clause
            )
            
            # DEBUG: Print results structure
            print(f"DEBUG: Query results structure:")
            print(f"  - documents: {len(results.get('documents', [])) if results.get('documents') else 0}")
            print(f"  - metadatas: {len(results.get('metadatas', [])) if results.get('metadatas') else 0}")
            print(f"  - distances: {results.get('distances', [])}")
            
            # Check if we found any results
            if not results.get('documents') or not results['documents'][0]:
                # Try a broader search without document filter
                if document_id:
                    print("DEBUG: Trying search without document filter...")
                    broad_results = self.collection.query(
                        query_embeddings=question_embedding.tolist(),
                        n_results=n_results,
                        where=None  # Remove document filter
                    )
                    
                    if broad_results.get('documents') and broad_results['documents'][0]:
                        return f"No relevant content found in document ID {document_id}, but other documents contain relevant information. Try searching all documents instead."
                    else:
                        return "No relevant content found in any documents for your question."
                else:
                    return f"No relevant documents found to answer your question: '{question}'"
            
            # Combine context from retrieved chunks
            context_chunks = results['documents'][0]
            context = "\n\n".join(context_chunks)
            
            print(f"DEBUG: Found {len(context_chunks)} relevant chunks")
            print(f"DEBUG: Total context length: {len(context)} characters")
            
            # Generate answer using the context
            return self.generate_answer(question, context)
            
        except Exception as e:
            print(f"DEBUG: Error in query_documents: {str(e)}")
            return f"Error querying documents: {str(e)}"
