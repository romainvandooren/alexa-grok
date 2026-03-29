#!/usr/bin/env python3
"""
Test script for the Alexa Grok lambda function with session support
"""
import os
import sys
import json
import re
import argparse
from unittest.mock import MagicMock

# Add lambda directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lambda'))

# Check for API Key
if 'XAI_API_KEY' not in os.environ:
    print("⚠️  Warning: XAI_API_KEY not found in environment variables.")

# Import the lambda handler
from lambda_function import lambda_handler

def create_alexa_request(query, session_attributes=None):
    """Create a mock Alexa request for testing"""
    if session_attributes is None:
        session_attributes = {}
        
    return {
        "version": "1.0",
        "session": {
            "new": not bool(session_attributes),
            "sessionId": "test-session-id",
            "application": {
                "applicationId": "test-app-id"
            },
            "attributes": session_attributes,
            "user": {
                "userId": "test-user-id"
            }
        },
        "context": {
            "System": {
                "application": {
                    "applicationId": "test-app-id"
                },
                "user": {
                    "userId": "test-user-id"
                },
                "device": {
                    "deviceId": "test-device-id",
                    "supportedInterfaces": {}
                }
            }
        },
        "request": {
            "type": "IntentRequest",
            "requestId": "test-request-id",
            "timestamp": "2025-12-10T10:00:00Z",
            "locale": "en-US",
            "intent": {
                "name": "GptQueryIntent",
                "confirmationStatus": "NONE",
                "slots": {
                    "query": {
                        "name": "query",
                        "value": query,
                        "confirmationStatus": "NONE"
                    }
                }
            }
        }
    }

def create_launch_request():
    """Create a mock Alexa LaunchRequest"""
    return {
        "version": "1.0",
        "session": {
            "new": True,
            "sessionId": "test-session-id",
            "application": {
                "applicationId": "test-app-id"
            },
            "attributes": {},
            "user": {
                "userId": "test-user-id"
            }
        },
        "context": {
            "System": {
                "application": {
                    "applicationId": "test-app-id"
                },
                "user": {
                    "userId": "test-user-id"
                }
            }
        },
        "request": {
            "type": "LaunchRequest",
            "requestId": "test-request-id",
            "timestamp": "2025-12-10T10:00:00Z",
            "locale": "en-US"
        }
    }

def clean_ssml(ssml):
    """Remove SSML tags for cleaner output"""
    return re.sub(r'<[^>]+>', '', ssml)

def verify_response(response, query=None):
    """Detailed verification of the Lambda response"""
    if not response or 'response' not in response:
        print("❌ Invalid response object")
        return False

    success = True
    alexa_res = response['response']
    
    # 1. Output Speech Verification
    if 'outputSpeech' in alexa_res:
        ssml = alexa_res['outputSpeech'].get('ssml', '')
        clean_text = clean_ssml(ssml)
        print(f"\n✅ Response: {clean_text}")
        
        # Check for Grok branding if it's the first turn or LaunchRequest
        if query is None or "who are you" in query.lower():
            if "Grok" in clean_text:
                print("   [OK] Grok branding found.")
            else:
                print("   [WARN] Grok branding NOT found in response.")

        # 2. Follow-up extraction and verification
        if "You could ask:" in clean_text:
            print("   [OK] 'You could ask:' pattern found in speech.")
            
            # Extract questions from speech using regex
            # Pattern: 'Question 1', 'Question 2', or 'Question 3'
            suggestions_match = re.search(r"You could ask: (.*)\? What would you like to know\?", clean_text)
            if suggestions_match:
                extracted_part = suggestions_match.group(1)
                print(f"   [INFO] Extracted suggestions from speech: {extracted_part}")
        
        # 3. Session Attributes Verification
        if 'sessionAttributes' in response:
            attrs = response['sessionAttributes']
            if 'followup_questions' in attrs:
                questions = attrs['followup_questions']
                print(f"   [OK] Session contains {len(questions)} follow-up questions: {questions}")
                
                # Cross-verify with speech
                for q in questions:
                    if q.lower() in clean_text.lower():
                        print(f"   [OK] Follow-up '{q}' found in speech output.")
                    else:
                        print(f"   [FAIL] Follow-up '{q}' NOT found in speech output.")
                        success = False
            
            if 'chat_history' in attrs:
                print(f"   [OK] Chat history length: {len(attrs['chat_history'])}")
    
    # 4. Reprompt Verification
    if 'reprompt' in alexa_res:
        reprompt_ssml = alexa_res['reprompt'].get('outputSpeech', {}).get('ssml', '')
        clean_reprompt = clean_ssml(reprompt_ssml)
        print(f"   [OK] Reprompt: {clean_reprompt}")
        if "next" in clean_reprompt and response.get('sessionAttributes', {}).get('followup_questions'):
             print("   [OK] Reprompt correctly mentions 'next' for more suggestions.")
    
    return success

def test_query(query, session_attributes=None):
    """Test the lambda function with a specific query"""
    print(f"\n{'='*60}")
    print(f"Testing query: '{query}'")
    print('='*60)
    
    event = create_alexa_request(query, session_attributes)
    try:
        response = lambda_handler(event, {})
        verify_response(response, query)
        return response
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_launch():
    """Test the launch request"""
    print(f"\n{'='*60}")
    print("Testing LaunchRequest")
    print('='*60)
    event = create_launch_request()
    try:
        response = lambda_handler(event, {})
        verify_response(response)
        return response
    except Exception as e:
        print(f"❌ Launch Error: {str(e)}")
        return None

def test_multi_turn_session(queries):
    """Test a sequence of queries maintaining session state"""
    print(f"\n{'#'*60}")
    print(f"STARTING MULTI-TURN SESSION TEST ({len(queries)} turns)")
    print(f"{'#'*60}")
    
    # Start with Launch
    res = test_launch()
    session_attributes = res.get('sessionAttributes', {}) if res else {}
    
    for i, query in enumerate(queries):
        print(f"\n>>> TURN {i+1}")
        response = test_query(query, session_attributes)
        if response:
            session_attributes = response.get('sessionAttributes', {})
        else:
            print("Aborting session test due to error.")
            break
            
    print(f"\n{'#'*60}")
    print("MULTI-TURN SESSION TEST COMPLETED")
    print(f"{'#'*60}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Alexa Lambda function')
    parser.add_argument('query', nargs='?', help='A single query to test')
    parser.add_argument('--session', action='store_true', help='Run a multi-turn session test')
    parser.add_argument('--launch', action='store_true', help='Test only LaunchRequest')
    
    args = parser.parse_args()
    
    if args.session:
        # Multi-turn test sequence simulating context persistence
        test_queries = [
            "who is the CEO of xAI?",
            "what is his favorite social media platform?",
            "does he own it?"
        ]
        test_multi_turn_session(test_queries)
    elif args.launch:
        test_launch()
    elif args.query:
        test_query(args.query)
    else:
        # Default behavior: Launch then one query
        res = test_launch()
        attrs = res.get('sessionAttributes', {}) if res else {}
        test_query("who are you?", attrs)
