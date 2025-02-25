import chromadb
from chromadb.utils import embedding_functions
import json
import os
import boto3
from typing import Dict, List, Optional

class BedrockEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __init__(self, model_id="mistral.mixtral-8x7b-instruct-v0:1"):
        """Initialize Bedrock embedding function"""
        self.bedrock_client = boto3.client('bedrock-runtime', region_name="us-east-1")
        self.model_id = model_id

    def __call__(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using Bedrock"""
        embeddings = []
        for text in texts:
            try:
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps({
                        "inputText": text
                    })
                )
                response_body = json.loads(response['body'].read())
                embedding = response_body['embedding']
                embeddings.append(embedding)
            except Exception as e:
                print(f"Error generating embedding: {str(e)}")
                # Return a zero vector as fallback
                embeddings.append([0.0] * 1536)  # Titan model uses 1536 dimensions
        return embeddings

class QuestionVectorStore:
    def __init__(self, persist_directory: str = "backend/data/vectorstore"):
        """Initialize the vector store for Marathi listening questions"""
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Use Bedrock's Titan embedding model
        self.embedding_fn = BedrockEmbeddingFunction()
        
        # Create or get collections for each section type
        self.collections = {
            "section2": self.client.get_or_create_collection(
                name="section2_questions",
                embedding_function=self.embedding_fn,
                metadata={"description": "Marathi listening comprehension questions - Section 2"}
            ),
            "section3": self.client.get_or_create_collection(
                name="section3_questions",
                embedding_function=self.embedding_fn,
                metadata={"description": "Marathi phrase matching questions - Section 3"}
            )
        }

    def add_questions(self, section_num: int, questions: List[Dict], question_id: str):
        """Add questions to the vector store"""
        if section_num not in [2, 3]:
            raise ValueError("Only sections 2 and 3 are currently supported")
            
        collection = self.collections[f"section{section_num}"]
        
        ids = []
        documents = []
        metadatas = []
        
        for idx, question in enumerate(questions):
            # Create a unique ID for each question
            unique_id = f"{question_id}_{section_num}_{idx}"
            ids.append(unique_id)
            
            # Store the full question structure as metadata
            metadatas.append({
                "question_id": question_id,
                "section": section_num,
                "question_index": idx,
                "full_structure": json.dumps(question, ensure_ascii=False)
            })
            
            # Create a searchable document from the question content
            if section_num == 2:
                document = f"""
                Introduction: {question.get('Introduction', '')}
                Dialogue: {question.get('Conversation', '')}
                Question: {question.get('Question', '')}
                """
            else:  # section 3
                document = f"""
                Situation: {question.get('Situation', '')}
                Question: {question.get('Question', '')}
                """
            documents.append(document)
        
        # Add to collection
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def search_similar_questions(
        self, 
        section_num: int, 
        query: str, 
        n_results: int = 5
    ) -> List[Dict]:
        """Search for similar questions in the vector store"""
        if section_num not in [2, 3]:
            raise ValueError("Only sections 2 and 3 are currently supported")
            
        collection = self.collections[f"section{section_num}"]
        
        # If collection is empty, return empty list
        if collection.count() == 0:
            return []
            
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, collection.count())
        )
        
        # Convert results to more usable format
        questions = []
        for idx, metadata in enumerate(results.get('metadatas', [[]])[0]):
            if not metadata:
                continue
                
            try:
                question_data = json.loads(metadata['full_structure'])
                if results.get('distances') and len(results['distances']) > 0:
                    question_data['similarity_score'] = results['distances'][0][idx]
                questions.append(question_data)
            except Exception as e:
                print(f"Error parsing question data: {str(e)}")
            
        return questions

    def get_question_by_id(self, section_num: int, question_id: str) -> Optional[Dict]:
        """Retrieve a specific question by its ID"""
        if section_num not in [2, 3]:
            raise ValueError("Only sections 2 and 3 are currently supported")
            
        collection = self.collections[f"section{section_num}"]
        
        result = collection.get(
            ids=[question_id],
            include=['metadatas']
        )
        
        if result['metadatas']:
            return json.loads(result['metadatas'][0]['full_structure'])
        return None
        
    def add_question(self, section_num: int, question: Dict, question_id: str):
        """Add a single question to the vector store"""
        self.add_questions(section_num, [question], question_id)
        
    def clear_collection(self, section_num: int):
        """Clear all questions from a collection"""
        if section_num not in [2, 3]:
            raise ValueError("Only sections 2 and 3 are currently supported")
            
        collection = self.collections[f"section{section_num}"]
        collection.delete(where={})