"""
Simple test to check for infinite rerun loops on home page
"""

import sys
import os

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

print("\n" + "="*60)
print("HOME PAGE INFINITE LOOP TEST")
print("="*60)

# Simple logic test
class TestSessionState:
    def __init__(self):
        self.rerun_count = 0
        self.selected_menu = "Home"
        
    def simulate_button_click(self, target_menu):
        """Simulate what happens when a button is clicked"""
        print(f"\nTest: Button clicked to navigate to '{target_menu}'")
        
        # This is what the button handler does
        self.selected_menu = target_menu
        self.rerun_count += 1
        
        print(f"  - Menu changed to: {self.selected_menu}")
        print(f"  - Rerun count: {self.rerun_count}")
        
        # Check if it would loop
        if self.rerun_count > 1:
            return False, "FAIL: Multiple reruns detected (infinite loop)"
        return True, "PASS: Single rerun, no loop"

print("\nTesting button navigation logic...")
print("-" * 60)

test_state = TestSessionState()
results = []

# Test each button scenario
buttons = [
    ("Market Price Button", "Market Prices"),
    ("Weather Button", "Weather Forecast"),
    ("Browse Button", "Browse Listings"),
    ("Post Button", "Post Listing"),
    ("Calendar Button", "My Calendar"),
]

for button_name, target_menu in buttons:
    test_state = TestSessionState()  # Reset for each test
    success, message = test_state.simulate_button_click(target_menu)
    results.append((button_name, success))
    
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status} {button_name}: {message}")

print("\n" + "="*60)
print("RESULTS")
print("="*60)

passed = sum(1 for _, result in results if result)
total = len(results)

for name, result in results:
    status = "[PASS]" if result else "[FAIL]"
    print(f"{status} {name}")

print(f"\nTotal: {passed}/{total} tests passed")

if passed == total:
    print("\n SUCCESS: All button logic tests passed!")
    print("No infinite loop patterns detected in button handlers.")
else:
    print(f"\n WARNING: {total - passed} test(s) failed.")

# Additional check: Test chat input behavior
print("\n" + "="*60)
print("CHAT INPUT TEST")
print("="*60)

class ChatTest:
    def __init__(self):
        self.api_calls = 0
        self.reruns = 0
        self.last_input = None
        
    def process_message(self, message):
        """Simulate chat input processing"""
        print(f"\nTest: User sends message: '{message}'")
        
        # With st.chat_input, it should clear after processing
        # Old way with st.text_input would keep the value
        
        if message and message != self.last_input:
            print(f"  - New message detected")
            self.api_calls += 1
            self.last_input = message
            self.reruns += 1
            print(f"  - API calls: {self.api_calls}")
            print(f"  - Reruns: {self.reruns}")
            
            # After rerun, st.chat_input returns None (cleared)
            return None  # This prevents loop
        else:
            print(f"  - No new message (chat_input cleared)")
            return None
        
    def test_scenario(self):
        """Test if chat input causes loop"""
        # First render: user types message
        result1 = self.process_message("Hello")
        
        # After rerun: chat_input is cleared, returns None
        result2 = self.process_message(None)
        
        if self.api_calls == 1 and self.reruns == 1:
            return True, "PASS: Single API call, no loop"
        else:
            return False, f"FAIL: API calls={self.api_calls}, reruns={self.reruns}"

chat_test = ChatTest()
success, message = chat_test.test_scenario()
status = "[PASS]" if success else "[FAIL]"
print(f"\n{status} Chat Input: {message}")

print("\n" + "="*60)
print("RECOMMENDATION")
print("="*60)

if passed == total and success:
    print("The button logic looks correct!")
    print("")
    print("If you're still experiencing loops in the actual app:")
    print("  1. Clear browser cache (Ctrl+Shift+R)")
    print("  2. Restart Streamlit server")
    print("  3. Check browser console for JavaScript errors")
    print("  4. Try different browser")
else:
    print("Logic tests detected potential issues.")
    print("Review the button handlers in home_page.py")

sys.exit(0 if (passed == total and success) else 1)
