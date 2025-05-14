import chromadb
import uuid
import json
from typing import List, Dict, Any
from config import CHROMA_PERSIST_DIRECTORY, CHROMA_COLLECTION_NAME, MAX_MEMORY_ITEMS

class ConversationMemory:
    """
    Handles storing and retrieving conversation history using Chroma vector database
    """
    def __init__(self, conversation_id=None):
        """
        Initialize the conversation memory
        
        Args:
            conversation_id (str, optional): Unique identifier for the conversation
        """
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIRECTORY)
        
        # Create or get collection
        try:
            self.collection = self.client.get_collection(CHROMA_COLLECTION_NAME)
            print(f"Connected to existing Chroma collection: {CHROMA_COLLECTION_NAME}")
        except ValueError:
            # Collection doesn't exist yet, create it
            self.collection = self.client.create_collection(
                name=CHROMA_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"Created new Chroma collection: {CHROMA_COLLECTION_NAME}")
        
        # Generate a conversation ID if not provided
        self.conversation_id = conversation_id or str(uuid.uuid4())
        
    def add_message(self, role: str, content: str):
        """
        Add a message to the conversation history
        
        Args:
            role (str): The role of the message sender (user or assistant)
            content (str): The content of the message
        """
        # Create a unique ID for this message
        message_id = f"{self.conversation_id}_{uuid.uuid4()}"
        
        # Store the message
        self.collection.add(
            ids=[message_id],
            documents=[content],
            metadatas=[{
                "conversation_id": self.conversation_id,
                "role": role,
                "timestamp": str(uuid.uuid1())  # Using timestamp UUID for chronological ordering
            }]
        )
        
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Retrieve the conversation history for the current conversation ID
        
        Returns:
            List[Dict[str, Any]]: List of conversation messages with role and content
        """
        # Query the collection for messages from this conversation
        results = self.collection.get(
            where={"conversation_id": self.conversation_id},
            limit=MAX_MEMORY_ITEMS  # Limit to most recent messages
        )
        
        if not results or not results['ids']:
            return []
        
        # Sort messages by timestamp (from oldest to newest)
        messages = []
        for i in range(len(results['ids'])):
            messages.append({
                "id": results['ids'][i],
                "role": results['metadatas'][i]['role'],
                "content": results['documents'][i],
                "timestamp": results['metadatas'][i]['timestamp']
            })
        
        # Sort by timestamp and format for return
        messages.sort(key=lambda x: x['timestamp'])
        return [{"role": msg["role"], "content": msg["content"]} for msg in messages]
    
    def clear_conversation(self):
        """Clear all messages for the current conversation"""
        results = self.collection.get(
            where={"conversation_id": self.conversation_id}
        )
        
        if results and results['ids']:
            self.collection.delete(ids=results['ids'])
            print(f"Cleared conversation {self.conversation_id}")
    
    def format_for_prompt(self) -> str:
        """
        Format the conversation history for inclusion in an LLM prompt
        
        Returns:
            str: Formatted conversation history
        """
        history = self.get_conversation_history()
        if not history:
            return "No previous conversation."
        
        formatted = "Previous conversation:\n"
        for msg in history:
            role_display = "Customer" if msg["role"] == "user" else "Support Agent"
            formatted += f"{role_display}: {msg['content']}\n"
        
        return formatted

# Testing functionality
if __name__ == "__main__":
    # Create a memory instance
    memory = ConversationMemory("test_convo_123")
    
    # Clear any existing conversation data for this test
    memory.clear_conversation()
    
    # Add some sample messages
    memory.add_message("user", "Hi, I need help with my order.")
    memory.add_message("assistant", "I'd be happy to help! Could you provide your order or payment ID?")
    memory.add_message("user", "My payment ID is PAY123456")
    
    # Retrieve and display the conversation history
    print("\nConversation History:")
    history = memory.get_conversation_history()
    for msg in history:
        print(f"{msg['role']}: {msg['content']}")
    
    # Display formatted history as it would appear in a prompt
    print("\nFormatted for Prompt:")
    print(memory.format_for_prompt())