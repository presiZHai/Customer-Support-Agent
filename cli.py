import os
import sys
import requests
import json
from typing import Dict, List, Any

class CustomerSupportCLI:
    """
    Simple command-line interface for testing the customer support agent
    """
    def __init__(self, api_url: str = "http://localhost:8000"):
        """
        Initialize the CLI
        
        Args:
            api_url (str): The URL of the customer support API
        """
        self.api_url = api_url
        self.conversation_id = None
        
    def start(self):
        """Start the CLI interface"""
        print("Customer Support CLI")
        print("Type 'exit' to quit, 'reset' to start a new conversation")
        print("-----------------------------------------------------")
        
        while True:
            # Get user input
            try:
                user_message = input("\nYou: ")
            except EOFError:
                break
            
            # Check for exit command
            if user_message.lower() == "exit":
                print("Goodbye!")
                break
            
            # Check for reset command
            if user_message.lower() == "reset":
                if self.conversation_id:
                    self._reset_conversation()
                else:
                    print("No active conversation to reset.")
                continue
            
            # Process the message
            try:
                response = self._send_message(user_message)
                print(f"\nAgent: {response}")
            except Exception as e:
                print(f"Error: {e}")
    
    def _send_message(self, message: str) -> str:
        """
        Send a message to the API
        
        Args:
            message (str): The user message
            
        Returns:
            str: The agent's response
        """
        data = {"message": message}
        if self.conversation_id:
            data["conversation_id"] = self.conversation_id
        
        response = requests.post(f"{self.api_url}/message", json=data)
        
        if response.status_code == 200:
            result = response.json()
            self.conversation_id = result["conversation_id"]
            return result["response"]
        else:
            raise Exception(f"API error: {response.status_code} - {response.text}")
    
    def _reset_conversation(self):
        """Reset the current conversation"""
        if not self.conversation_id:
            return
        
        response = requests.delete(f"{self.api_url}/conversation/{self.conversation_id}")
        
        if response.status_code == 200:
            print(f"Conversation reset successfully.")
        else:
            print(f"Error resetting conversation: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Use custom API URL if provided as an argument
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    cli = CustomerSupportCLI(api_url)
    cli.start()