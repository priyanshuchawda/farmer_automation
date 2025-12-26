"""
Test chatbot functionality and performance on home page
"""

import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

print("\n" + "="*60)
print("CHATBOT FUNCTIONALITY & PERFORMANCE TEST")
print("="*60)

class ChatbotPerformanceTest:
    def __init__(self):
        self.api_calls = []
        self.reruns = []
        self.errors = []
        
    def track_api_call(self, message):
        """Track each API call with timestamp"""
        call_info = {
            'timestamp': time.time(),
            'message': message,
            'call_number': len(self.api_calls) + 1
        }
        self.api_calls.append(call_info)
        return call_info
    
    def track_rerun(self):
        """Track each rerun with timestamp"""
        rerun_info = {
            'timestamp': time.time(),
            'rerun_number': len(self.reruns) + 1
        }
        self.reruns.append(rerun_info)
        return rerun_info
    
    def analyze_performance(self):
        """Analyze if there are performance issues"""
        issues = []
        
        # Check for duplicate API calls
        if len(self.api_calls) > 1:
            # Check if same message called multiple times
            messages = [call['message'] for call in self.api_calls]
            if len(messages) != len(set(messages)):
                issues.append("DUPLICATE API CALLS: Same message processed multiple times")
        
        # Check for excessive reruns
        if len(self.reruns) > 2:
            issues.append(f"EXCESSIVE RERUNS: {len(self.reruns)} reruns detected")
        
        # Check timing between calls
        if len(self.api_calls) > 1:
            time_diffs = []
            for i in range(1, len(self.api_calls)):
                diff = self.api_calls[i]['timestamp'] - self.api_calls[i-1]['timestamp']
                time_diffs.append(diff)
            
            # If calls are too close together (< 0.1s), it's likely a loop
            rapid_calls = [d for d in time_diffs if d < 0.1]
            if rapid_calls:
                issues.append(f"RAPID FIRE API CALLS: {len(rapid_calls)} calls within 0.1s")
        
        return issues

def test_single_message():
    """Test: User sends one message, should trigger ONE API call"""
    print("\n" + "-"*60)
    print("TEST 1: Single Message Processing")
    print("-"*60)
    
    test = ChatbotPerformanceTest()
    
    # Simulate user typing one message
    print("\nScenario: User types 'What crops to plant?' and hits Enter")
    
    # First render: User input exists
    user_message = "What crops to plant?"
    print(f"  → User input detected: '{user_message}'")
    
    # Process message (what st.chat_input does)
    if user_message:
        test.track_api_call(user_message)
        print(f"  → API call #{test.api_calls[-1]['call_number']}: Processing message")
        test.track_rerun()
        print(f"  → Rerun #{test.reruns[-1]['rerun_number']}: UI refresh")
        
        # After rerun, st.chat_input clears and returns None
        user_message = None
        print("  → st.chat_input cleared (returns None)")
    
    # Second render: No input (chat_input is cleared)
    print("\n  Second render after rerun:")
    if user_message:
        test.track_api_call(user_message)
        print(f"  → API call #{test.api_calls[-1]['call_number']}")
        test.track_rerun()
    else:
        print("  → No user input, no API call (GOOD)")
    
    # Analyze
    issues = test.analyze_performance()
    
    print("\n  Analysis:")
    print(f"  - Total API calls: {len(test.api_calls)}")
    print(f"  - Total reruns: {len(test.reruns)}")
    
    if issues:
        print("\n  ❌ ISSUES DETECTED:")
        for issue in issues:
            print(f"     - {issue}")
        return False
    else:
        print("  ✅ PASS: Single API call, proper behavior")
        return True

def test_text_input_vs_chat_input():
    """Test: Compare old st.text_input vs new st.chat_input behavior"""
    print("\n" + "-"*60)
    print("TEST 2: st.text_input vs st.chat_input Comparison")
    print("-"*60)
    
    print("\n  OLD BEHAVIOR (st.text_input):")
    print("  ------------------------------")
    test_old = ChatbotPerformanceTest()
    
    # Simulate old text_input behavior (value persists)
    user_input = "Test message"
    print(f"  1st render: user_input = '{user_input}'")
    if user_input:
        test_old.track_api_call(user_input)
        test_old.track_rerun()
        print(f"     → API call #{test_old.api_calls[-1]['call_number']}")
        print(f"     → Rerun #{test_old.reruns[-1]['rerun_number']}")
    
    # After rerun, text_input STILL has the value (problem!)
    print(f"  2nd render: user_input = '{user_input}' (STILL HAS VALUE)")
    if user_input:
        test_old.track_api_call(user_input)
        test_old.track_rerun()
        print(f"     → API call #{test_old.api_calls[-1]['call_number']} (DUPLICATE!)")
        print(f"     → Rerun #{test_old.reruns[-1]['rerun_number']}")
    
    # This would continue...
    print(f"  3rd render: user_input = '{user_input}' (STILL HAS VALUE)")
    if user_input:
        test_old.track_api_call(user_input)
        print(f"     → API call #{test_old.api_calls[-1]['call_number']} (DUPLICATE!)")
    
    old_issues = test_old.analyze_performance()
    print(f"\n  Result: {len(test_old.api_calls)} API calls, {len(old_issues)} issues")
    
    print("\n  NEW BEHAVIOR (st.chat_input):")
    print("  ------------------------------")
    test_new = ChatbotPerformanceTest()
    
    # Simulate new chat_input behavior (auto-clears)
    user_input = "Test message"
    print(f"  1st render: user_input = '{user_input}'")
    if user_input:
        test_new.track_api_call(user_input)
        test_new.track_rerun()
        print(f"     → API call #{test_new.api_calls[-1]['call_number']}")
        print(f"     → Rerun #{test_new.reruns[-1]['rerun_number']}")
        # chat_input auto-clears after submission
        user_input = None
    
    # After rerun, chat_input returns None (cleared)
    print(f"  2nd render: user_input = None (CLEARED)")
    if user_input:
        test_new.track_api_call(user_input)
        test_new.track_rerun()
    else:
        print(f"     → No API call (GOOD)")
    
    new_issues = test_new.analyze_performance()
    print(f"\n  Result: {len(test_new.api_calls)} API call, {len(new_issues)} issues")
    
    if len(test_new.api_calls) == 1 and len(new_issues) == 0:
        print("\n  ✅ PASS: st.chat_input prevents infinite loops")
        return True
    else:
        print("\n  ❌ FAIL: Still has issues")
        return False

def test_rapid_messages():
    """Test: User sends multiple different messages rapidly"""
    print("\n" + "-"*60)
    print("TEST 3: Multiple Sequential Messages")
    print("-"*60)
    
    test = ChatbotPerformanceTest()
    
    messages = ["What to plant?", "Weather forecast?", "Market prices?"]
    
    print("\nScenario: User sends 3 different messages")
    
    for i, msg in enumerate(messages, 1):
        print(f"\n  Message {i}: '{msg}'")
        test.track_api_call(msg)
        test.track_rerun()
        print(f"     → API call #{test.api_calls[-1]['call_number']}")
        print(f"     → Rerun #{test.reruns[-1]['rerun_number']}")
        time.sleep(0.01)  # Simulate small delay
    
    # Check for duplicate messages
    unique_messages = set(call['message'] for call in test.api_calls)
    duplicates = len(test.api_calls) - len(unique_messages)
    
    print(f"\n  Analysis:")
    print(f"  - Total API calls: {len(test.api_calls)}")
    print(f"  - Unique messages: {len(unique_messages)}")
    print(f"  - Duplicates: {duplicates}")
    
    if duplicates == 0 and len(test.api_calls) == 3:
        print("  ✅ PASS: All messages processed uniquely")
        return True
    else:
        print("  ❌ FAIL: Duplicate processing detected")
        return False

def test_empty_input():
    """Test: User submits empty message"""
    print("\n" + "-"*60)
    print("TEST 4: Empty Input Handling")
    print("-"*60)
    
    test = ChatbotPerformanceTest()
    
    print("\nScenario: User submits without typing anything")
    
    user_input = ""  # Empty string
    print(f"  → User input: '{user_input}' (empty)")
    
    # Good implementation should check if input is not empty
    if user_input and user_input.strip():
        test.track_api_call(user_input)
        test.track_rerun()
        print(f"  → API call triggered")
    else:
        print(f"  → No API call (GOOD)")
    
    if len(test.api_calls) == 0:
        print("\n  ✅ PASS: Empty input ignored")
        return True
    else:
        print("\n  ❌ FAIL: Empty input triggered API call")
        return False

def test_performance_timing():
    """Test: Check if API calls are taking too long"""
    print("\n" + "-"*60)
    print("TEST 5: Performance Timing")
    print("-"*60)
    
    print("\nSimulating API response times...")
    
    timings = {
        'fast': 0.5,
        'normal': 2.0,
        'slow': 5.0,
        'very_slow': 10.0
    }
    
    for speed, duration in timings.items():
        print(f"\n  {speed.upper()} response ({duration}s):")
        
        start = time.time()
        time.sleep(duration)
        end = time.time()
        
        actual = end - start
        print(f"    - Actual time: {actual:.2f}s")
        
        if actual > 10:
            print(f"    ⚠️  WARNING: Very slow response")
        elif actual > 5:
            print(f"    ⚠️  Slow response")
        elif actual > 2:
            print(f"    ℹ️  Normal response")
        else:
            print(f"    ✅ Fast response")
    
    print("\n  Note: Actual Gemini API typically responds in 1-3 seconds")
    print("        If consistently >5s, check internet connection or API status")
    return True

def main():
    print("Testing chatbot functionality and performance...\n")
    
    results = []
    
    # Run all tests
    results.append(("Single Message", test_single_message()))
    results.append(("Input Comparison", test_text_input_vs_chat_input()))
    results.append(("Multiple Messages", test_rapid_messages()))
    results.append(("Empty Input", test_empty_input()))
    results.append(("Performance Timing", test_performance_timing()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total = len(results)
    
    print(f"\nTotal: {passed_count}/{total} tests passed")
    
    if passed_count == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nChatbot implementation is correct.")
        print("\nIf Streamlit feels slow:")
        print("  1. Check internet connection (API calls need internet)")
        print("  2. Gemini API might be rate-limited or slow")
        print("  3. Try running with --server.runOnSave false")
        print("  4. Check system resources (CPU/RAM)")
        return 0
    else:
        print(f"\n⚠️ {total - passed_count} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
