from db_module import PaymentDatabase
from memory_module import ConversationMemory
from llm_module import LLMProcessor
from typing import Dict, Any, Optional

class CustomerSupportAgent:
    """
    Integrates database, memory, and LLM components to handle customer support queries
    """
    def __init__(self, conversation_id=None):
        """
        Initialize the customer support agent
        
        Args:
            conversation_id (str, optional): Unique identifier for the conversation
        """
        self.db = PaymentDatabase()
        self.memory = ConversationMemory(conversation_id)
        self.llm = LLMProcessor()
        print(f"Customer Support Agent initialized with conversation ID: {self.memory.conversation_id}")
    
    def process_user_message(self, message: str) -> str:
        """
        Process a user message and generate an appropriate response
        
        Args:
            message (str): The user message
            
        Returns:
            str: The agent's response
        """
        # Start the tool calling process
        print("\n--- Processing user message ---")
        print(f"User message: {message}")
        
        # 1. Check if the message contains a payment ID
        payment_id = self.llm.extract_payment_id(message)
        payment_info = None
        
        # 2. If payment ID found, retrieve payment information from database
        if payment_id:
            print(f"Tool Call: Retrieving payment information for ID: {payment_id}")
            payment_info = self.db.get_payment_by_id(payment_id)
            
            if payment_info:
                print(f"Payment found: {payment_info['payment_id']} - Status: {payment_info['status']}")
            else:
                print(f"Payment not found for ID: {payment_id}")
        
        # 3. Get conversation history from memory module
        print("Tool Call: Retrieving conversation history from memory")
        conversation_history = self.memory.format_for_prompt()
        print(f"Retrieved {len(self.memory.get_conversation_history())} previous messages")
        
        # 4. Process with LLM to generate response
        print("Tool Call: Sending to Gemini for response generation")
        response = self.llm.process_message(
            user_message=message,
            conversation_history=conversation_history,
            payment_info=payment_info
        )
        print("Response generated successfully")
        
        # 5. Store conversation in memory
        print("Tool Call: Storing conversation in memory")
        self.memory.add_message("user", message)
        self.memory.add_message("assistant", response)
        
        print("--- Processing complete ---\n")
        return response
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.memory.clear_conversation()
    
    def close(self):
        """Close database connections"""
        self.db.close()

# Testing functionality
if __name__ == "__main__":
    # Initialize the agent
    agent = CustomerSupportAgent("test_session_001")
    
    # Initialize sample data for testing
    agent.db.initialize_sample_data()
    
    # Reset conversation to start fresh
    agent.reset_conversation()
    
    # Simulate a conversation
    test_conversation = [
        "Hi, I need help tracking my recent order",
        "My payment ID is PAY123456",
        "When will my headphones be delivered?",
        "Thank you for your help!"
    ]
    
    for message in test_conversation:
        print(f"\nUser: {message}")
        response = agent.process_user_message(message)
        print(f"Agent: {response}")
    
    # Close connections
    agent.close()