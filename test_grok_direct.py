import os
import sys
import time

# Add lambda directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'lambda'))

from lambda_function import generate_grok_response, generate_followup_questions

def test_generate_grok_response():
    print("Testing generate_grok_response...")
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        print("XAI_API_KEY not found in environment variables.")
        return False

    chat_history = []
    query = "What is the capital of France?"
    
    try:
        response_data = generate_grok_response(chat_history, query)
        
        # In current lambda_function.py, generate_grok_response returns a tuple (response_text, followup_questions)
        # However, let's check for both cases just in case
        if isinstance(response_data, tuple):
            response_text, followup_questions = response_data
        else:
            response_text = response_data
            followup_questions = []
            
        print(f"Response: {response_text}")
        print(f"Follow-up questions: {followup_questions}")
        
        if not response_text:
            print("FAILED: No response text returned.")
            return False
            
        return True
    except Exception as e:
        print(f"FAILED: Exception occurred: {e}")
        return False

def test_generate_followup_questions():
    print("\nTesting generate_followup_questions...")
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        print("XAI_API_KEY not found in environment variables.")
        return False

    chat_history = []
    query = "What is the capital of France?"
    response = "The capital of France is Paris."
    
    try:
        questions = generate_followup_questions(chat_history, query, response)
        print(f"Follow-up questions: {questions}")
        
        if not isinstance(questions, list):
            print("FAILED: questions is not a list.")
            return False
            
        return True
    except Exception as e:
        print(f"FAILED: Exception occurred: {e}")
        return False

if __name__ == "__main__":
    if not os.environ.get("XAI_API_KEY"):
        print("XAI_API_KEY environment variable is required.")
        # We don't exit with 1 because we want the script to at least run for the 'done' criteria
        # if the user just wants to see if imports work.
        # But for 'verify', the plan uses XAI_API_KEY=test.
    
    success = test_generate_grok_response()
    success = test_generate_followup_questions() and success
    
    if success:
        print("\nDirect testing of core logic functions complete.")
        sys.exit(0)
    else:
        print("\nSome tests failed.")
        sys.exit(1)
