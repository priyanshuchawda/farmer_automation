# Testing Checklist for Optimized Gemini Prompts

Use this checklist to validate the prompt optimizations.

---

## ✅ Pre-Deployment Tests

### 1. Syntax Validation
- [x] All Python files compile without errors
- [x] No import errors
- [x] No indentation issues

**Status**: ✅ PASSED (all files validated)

---

## 🧪 Functional Testing

### 2. Marketplace Recommendations (`ai_matcher.py`)

**Test Case**: Farmer lists "Tractor" for rent in "Pune"

**Expected Output**:
- [ ] Exactly 3 recommendations
- [ ] Each starts with "- "
- [ ] Contains quantified benefits (e.g., "30% increase")
- [ ] Mentions specific tools or actions
- [ ] Practical and actionable

**Test Command**:
```python
from ai.ai_matcher import get_recommendations
context = {'farmer': 'Ramesh', 'location': 'Pune', 'item': 'Tractor', 'type': 'tool'}
result = get_recommendations(context)
print(result)
```

---

### 3. Price Prediction (`ai_price_predictor.py`)

**Test Case 1**: Predict wheat prices in Pune at ₹2500/quintal

**Expected Output**:
- [ ] Contains DAY_7_PRICE, DAY_15_PRICE, DAY_30_PRICE
- [ ] TREND is one of: UPWARD/DOWNWARD/STABLE
- [ ] CONFIDENCE is one of: HIGH/MEDIUM/LOW
- [ ] KEY_FACTORS has 5 bullet points
- [ ] RECOMMENDATION is specific with percentages

**Test Command**:
```python
from ai.price_predictor import PricePredictor
predictor = PricePredictor()
result = predictor.predict_future_prices("Wheat", 2500, "Pune")
print(result)
```

**Test Case 2**: Best selling time for rice

**Expected Output**:
- [ ] BEST_MONTH specified
- [ ] SELL_NOW_SCORE and WAIT_SCORE (0-10)
- [ ] EXPECTED_PEAK_PRICE with ₹ amount
- [ ] TIMELINE with specific dates
- [ ] 3 RISK_FACTORS listed

---

### 4. Farming Plan (`calender/ai_service.py`)

**Test Case**: "Create 10-day wheat planting schedule"

**Expected Output**:
- [ ] Valid JSON with 'heading' and 'plan' keys
- [ ] Each step has step_number, title, description
- [ ] Descriptions include timing (e.g., "7 AM", "Day 3")
- [ ] Quantities mentioned (e.g., "2 kg seeds per acre")
- [ ] Safety warnings present if applicable

**Test Command**:
```python
from calender.ai_service import AIService
service = AIService()
plan, error = service.generate_farming_plan("wheat planting 10 days", "English")
print(plan)
```

---

### 5. AI Chatbot (`components/ai_chatbot_page.py`)

**Test Case 1**: "Yellow spots on tomato leaves"

**Expected Output**:
- [ ] Direct answer (disease name)
- [ ] 2-3 numbered steps for treatment
- [ ] ₹ cost mentioned for solutions
- [ ] Safety warning about chemicals
- [ ] Tip at the end

**Test Case 2**: "Best time to plant wheat" (in Hindi)

**Expected Output**:
- [ ] Entire response in Hindi (no English mixed)
- [ ] Specific date range
- [ ] 3 preparation steps
- [ ] Weather check reference

---

### 6. Price Advisor (`components/simple_price_advisor.py`)

**Test Case**: Tomato at ₹20/kg, should I sell now?

**Expected Output**:
- [ ] RECOMMENDATION: SELL NOW or WAIT
- [ ] NEXT BEST DAY with specific date
- [ ] EXPECTED PRICE: ₹X/kg
- [ ] PRICE CHANGE: ↑/↓/→ with amount
- [ ] REASON in simple language
- [ ] PROFIT IMPACT for 100kg with ₹ amount
- [ ] RISK: LOW/MEDIUM/HIGH with explanation

**Test Command**:
```python
from components.simple_price_advisor import SimplePriceAdvisor
advisor = SimplePriceAdvisor()
market_days = [{'day': 'Monday', 'date': date(2025, 1, 15)}, ...]
result = advisor.get_simple_advice("Tomato", 20, "Nashik", market_days)
print(result)
```

---

### 7. Government Schemes (`components/government_schemes_page.py`)

**Test Case**: Search schemes for wheat farmers in Pune

**Expected Output**:
- [ ] 3-4 central schemes listed
- [ ] 2-3 state schemes for Maharashtra
- [ ] Each scheme has exact ₹ benefit amount
- [ ] Application steps (numbered 1, 2, 3...)
- [ ] Official website URLs
- [ ] Helpline phone numbers
- [ ] Documents checklist
- [ ] Pro tips section

---

### 8. Location Services (`components/location_manager.py`)

**Test Case 1**: Get coordinates for "Ahmednagar, Maharashtra"

**Expected Output**:
- [ ] Response contains "LAT: " line
- [ ] Response contains "LON: " line
- [ ] Coordinates are decimal numbers
- [ ] No extra text

**Test Case 2**: Reverse geocode (19.0948, 74.7480)

**Expected Output**:
- [ ] Full address provided
- [ ] City/Village name
- [ ] District name
- [ ] State name
- [ ] Country: India
- [ ] Postal code (if available)
- [ ] Nearby landmark

---

### 9. Farm Finance (`components/farm_finance_page.py`)

**Test Case 1**: Analyze profit/loss

**Expected Output**:
- [ ] 5 sections: Health, Patterns, Cost Reduction, Revenue, Planning
- [ ] Each pattern has specific % or ₹ amount
- [ ] 3 cost reduction actions with ₹ savings
- [ ] 3 revenue strategies with ₹ potential
- [ ] 3-month seasonal outlook

**Test Case 2**: Investment suggestions for ₹50,000 budget

**Expected Output**:
- [ ] 5 prioritized investments
- [ ] Each has Cost, ROI Timeline, Priority, Annual Benefit
- [ ] Costs are current 2024-25 Indian prices
- [ ] ROI timeline in months/years
- [ ] Justification with data

---

## 🔍 Quality Checks

### 10. Consistency Test

**Test**: Run same query 5 times, compare outputs

```python
results = []
for i in range(5):
    result = predictor.predict_future_prices("Wheat", 2500, "Pune")
    results.append(result)

# Check consistency
trends = [r['trend'] for r in results]
print(f"Trends: {trends}")
# Expected: Same trend in at least 4 out of 5 runs
```

**Pass Criteria**:
- [ ] Same TREND in 80%+ runs (with temp 0.2-0.3)
- [ ] Prices within ±5% range
- [ ] Same CONFIDENCE level

---

### 11. Format Validation

**Test**: Check output format matches specification

```python
def validate_price_prediction(result):
    required_keys = ['DAY_7_PRICE', 'DAY_15_PRICE', 'DAY_30_PRICE', 
                     'TREND', 'CONFIDENCE', 'KEY_FACTORS', 'RECOMMENDATION']
    
    for key in required_keys:
        assert key in str(result), f"Missing: {key}"
    
    assert result['TREND'] in ['UPWARD', 'DOWNWARD', 'STABLE']
    assert result['CONFIDENCE'] in ['HIGH', 'MEDIUM', 'LOW']
    assert len(result['KEY_FACTORS']) >= 4
    
    print("✅ Format validation passed")
```

---

### 12. Language Test

**Test**: Hindi/Marathi responses don't mix English

```python
from components.ai_chatbot_page import render_ai_chatbot_page

# Set language to Hindi
st.session_state['language'] = 'हिन्दी (Hindi)'

# Ask question in Hindi
response = get_chatbot_response("गेहूं की कीमत कब अच्छी मिलेगी")

# Validate
english_words = ["price", "wheat", "market", "sell"]
mixed_language = any(word in response.lower() for word in english_words)

assert not mixed_language, "Response contains English words!"
print("✅ Language purity validated")
```

---

### 13. Safety Check

**Test**: Pesticide/chemical advice includes warnings

```python
response = chatbot.respond("How to control pests on cotton?")

safety_keywords = ["safety", "mask", "gloves", "protective", "warning", "caution"]
has_safety = any(keyword in response.lower() for keyword in safety_keywords)

assert has_safety, "No safety warning for chemical use!"
print("✅ Safety warning present")
```

---

### 14. Quantification Check

**Test**: Responses include specific amounts

```python
def check_quantified(response):
    has_rupees = "₹" in response
    has_percent = "%" in response
    has_numbers = any(char.isdigit() for char in response)
    has_timeline = any(word in response.lower() for word in 
                       ["day", "week", "month", "days", "weeks", "months"])
    
    score = sum([has_rupees, has_percent, has_numbers, has_timeline])
    assert score >= 2, f"Not enough quantification (score: {score}/4)"
    print(f"✅ Quantification score: {score}/4")
```

---

### 15. Context Awareness

**Test**: Responses use provided context

```python
context = {
    'farmer': 'Ramesh Patil',
    'location': 'Ahmednagar',
    'crop': 'Sugarcane'
}

response = get_recommendations(context)

# Check if location is referenced
assert 'Ahmednagar' in response or 'Maharashtra' in response
# Check if crop is referenced  
assert 'Sugarcane' in response or 'sugarcane' in response

print("✅ Context properly utilized")
```

---

## 📊 Performance Benchmarks

### Response Time
- [ ] Market recommendations: < 3 seconds
- [ ] Price prediction: < 8 seconds (with weather/news fetch)
- [ ] Chatbot response: < 4 seconds
- [ ] Government schemes: < 10 seconds (with search grounding)

### Token Usage
- [ ] Simple queries: 500-1000 tokens
- [ ] Complex predictions: 2000-3000 tokens
- [ ] Scheme searches: 3000-5000 tokens

### Cache Hit Rate (after initial queries)
- [ ] Weather data: 80%+ (6 hour cache)
- [ ] Market prices: 70%+ (24 hour cache)
- [ ] Predictions: 50%+ (24 hour cache)

---

## 🔧 Troubleshooting

### If responses are inconsistent:
1. Check temperature setting - lower it by 0.1
2. Verify examples in prompt are clear
3. Add more constraints to output format
4. Increase few-shot examples to 3-4

### If parsing fails:
1. Check response prefix format
2. Add regex fallback for key fields
3. Log raw response for debugging
4. Verify output format specification is clear

### If quality is poor:
1. Review system instruction - is expertise clear?
2. Add more context to prompt
3. Increase example detail
4. Check if grounding (Google Search) is working

---

## ✅ Sign-off Checklist

Before marking as production-ready:

- [ ] All 8 files tested individually
- [ ] Consistency test passed (80%+ same outputs)
- [ ] Format validation passed for all outputs
- [ ] Language purity validated (Hindi/Marathi)
- [ ] Safety warnings present where needed
- [ ] Quantification check passed (2+/4 score)
- [ ] Context awareness verified
- [ ] Performance benchmarks met
- [ ] Documentation reviewed by team
- [ ] Error handling tested
- [ ] Edge cases covered

---

**Testing Status**: ⏳ Pending  
**Tested By**: _____________  
**Date**: _____________  
**Production Ready**: ☐ YES ☐ NO

**Notes**:
___________________________________________
___________________________________________
___________________________________________
