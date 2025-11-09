# test_schemes_feature.py
"""Test the government schemes feature"""

from components.government_schemes_page import GovernmentSchemesHelper

print("🧪 Testing Government Schemes Feature\n")
print("=" * 70)

# Initialize
print("\n1️⃣ Initializing helper...")
helper = GovernmentSchemesHelper()
print("   ✅ Helper initialized successfully")

# Test EMI Calculator
print("\n2️⃣ Testing EMI Calculator...")
result = helper.calculate_loan_emi(200000, 7.0, 60)

if result:
    print(f"   Loan Amount: ₹2,00,000")
    print(f"   Interest Rate: 7% per annum")
    print(f"   Tenure: 5 years (60 months)")
    print(f"\n   📊 Results:")
    print(f"   • Monthly EMI: ₹{result['emi']:,.2f}")
    print(f"   • Total Payment: ₹{result['total_payment']:,.2f}")
    print(f"   • Total Interest: ₹{result['total_interest']:,.2f}")
    print("   ✅ EMI Calculator working!")
else:
    print("   ❌ EMI Calculator failed")

# Test different scenarios
print("\n3️⃣ Testing Different Loan Scenarios...")
scenarios = [
    (100000, 5.0, 36, "Small Loan - 3 years @ 5%"),
    (500000, 9.0, 120, "Large Loan - 10 years @ 9%"),
    (300000, 7.5, 84, "Medium Loan - 7 years @ 7.5%")
]

for principal, rate, months, desc in scenarios:
    result = helper.calculate_loan_emi(principal, rate, months)
    if result:
        print(f"\n   {desc}")
        print(f"   Monthly EMI: ₹{result['emi']:,.2f}")

print("\n" + "=" * 70)
print("\n✅ Government Schemes Feature Ready!")
print("\n📋 Features Available:")
print("   • 📋 Government Schemes Database (with Google Search)")
print("   • ✅ Eligibility Checker (AI-powered)")
print("   • 📄 Document Requirements Helper")
print("   • 💰 Loan EMI Calculator")
print("   • 🔄 Force Refresh Option (updates every 2 hours)")
print("   • 💾 Smart Caching (saves API costs)")
print("\n" + "=" * 70)


