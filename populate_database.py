"""
Populate database with realistic Maharashtra farmer data
Run this script to add sample farmers, tools, and crops
"""

import sqlite3
from datetime import datetime, timedelta
import random

DB_NAME = 'farmermarket.db'

# Maharashtra districts and villages/cities
MAHARASHTRA_LOCATIONS = [
    # Pune District
    "Pune", "Pimpri-Chinchwad", "Khadki", "Hadapsar", "Viman Nagar",
    "Baramati", "Indapur", "Malegaon (Pune)", "Junnar", "Shirur",
    "Daund", "Purandar", "Haveli", "Mulshi", "Bhor",
    
    # Nashik District
    "Nashik", "Malegaon", "Sinnar", "Igatpuri", "Dindori",
    "Niphad", "Yeola", "Peth", "Surgana", "Kalwan",
    
    # Ahmednagar District
    "Ahmednagar", "Shrirampur", "Kopargaon", "Sangamner", "Newasa",
    "Rahuri", "Parner", "Shevgaon", "Jamkhed", "Karjat",
    
    # Solapur District
    "Solapur", "Pandharpur", "Barshi", "Akkalkot", "Karmala",
    "Madha", "Malshiras", "Mangalvedhe", "Mohol", "Sangole",
    
    # Satara District
    "Satara", "Karad", "Wai", "Phaltan", "Koregaon",
    "Khandala", "Patan", "Mahabaleshwar", "Jaoli", "Khatav",
    
    # Kolhapur District
    "Kolhapur", "Ichalkaranji", "Kagal", "Gadhinglaj", "Panhala",
    "Shahuwadi", "Radhanagari", "Bhudargad", "Hatkanangle", "Shirol",
    
    # Aurangabad District
    "Aurangabad", "Jalna", "Paithan", "Gangapur", "Vaijapur",
    "Khultabad", "Sillod", "Kannad", "Phulambri", "Soyegaon"
]

# Maharashtra-specific crops
MAHARASHTRA_CROPS = [
    "Sugarcane", "Cotton", "Soybean", "Jowar", "Bajra",
    "Wheat", "Tur (Pigeon Pea)", "Onion", "Tomato", "Potato",
    "Grapes", "Pomegranate", "Banana", "Mango", "Orange",
    "Maize", "Groundnut", "Sunflower", "Safflower", "Chickpea",
    "Green Gram", "Black Gram", "Chilli", "Turmeric", "Ginger"
]

# Common farming tools
FARMING_TOOLS = [
    "Tractor", "Power Tiller", "Rotavator", "Cultivator", "Harrow",
    "Seed Drill", "Sprayer", "Harvester", "Thresher", "Water Pump",
    "Drip Irrigation System", "Plough", "Leveler", "Reaper", "Weeder",
    "Chaff Cutter", "Trailer", "Ridger", "Disc Harrow", "Subsoiler"
]

# Indian male farmer names
MALE_NAMES = [
    "Ramesh", "Suresh", "Ganesh", "Mahesh", "Rajesh",
    "Dinesh", "Santosh", "Prakash", "Ashok", "Vijay",
    "Anil", "Sunil", "Sanjay", "Ajay", "Manoj",
    "Ramdas", "Baban", "Dagadu", "Shankar", "Balasaheb",
    "Pandharinath", "Vitthal", "Sopan", "Dnyaneshwar", "Tukaram",
    "Kishor", "Subhash", "Dattatray", "Narayan", "Vasant",
    "Bharat", "Sharad", "Kiran", "Vikas", "Sachin",
    "Ravindra", "Devendra", "Jayant", "Shivaji", "Sambhaji"
]

# Indian surnames (Maharashtra specific)
SURNAMES = [
    "Patil", "Deshmukh", "Kulkarni", "Pawar", "Jadhav",
    "Shinde", "Kamble", "More", "Gaikwad", "Sawant",
    "Bhosale", "Salve", "Rathod", "Ingle", "Kale",
    "Chavan", "Thorat", "Nimbalkar", "Mohite", "Khot",
    "Shirke", "Kadam", "Mane", "Bhoir", "Sapkal",
    "Khandekar", "Suryawanshi", "Shelar", "Dhere", "Lokhande"
]

def get_coordinates_for_location(location):
    """Get realistic coordinates for Maharashtra locations"""
    # Approximate coordinates for major cities (you can expand this)
    coords = {
        "Pune": (18.5204, 73.8567),
        "Nashik": (20.0059, 73.7897),
        "Ahmednagar": (19.0948, 74.7480),
        "Solapur": (17.6599, 75.9064),
        "Satara": (17.6805, 74.0183),
        "Kolhapur": (16.7050, 74.2433),
        "Aurangabad": (19.8762, 75.3433),
        "Baramati": (18.1516, 74.5770),
        "Malegaon": (20.5579, 74.5287),
        "Karad": (17.2888, 74.1818)
    }
    
    # If exact location found, return it
    if location in coords:
        return coords[location]
    
    # Otherwise, return nearby coordinates (slight variation from base city)
    base_lat, base_lon = 18.5204, 73.8567  # Default to Pune area
    variation_lat = random.uniform(-2, 2)
    variation_lon = random.uniform(-2, 2)
    return (base_lat + variation_lat, base_lon + variation_lon)

def create_farmers(count=50):
    """Create realistic farmer profiles"""
    farmers = []
    used_names = set()
    
    for i in range(count):
        # Generate unique name
        while True:
            first_name = random.choice(MALE_NAMES)
            surname = random.choice(SURNAMES)
            full_name = f"{first_name} {surname}"
            if full_name not in used_names:
                used_names.add(full_name)
                break
        
        location = random.choice(MAHARASHTRA_LOCATIONS)
        lat, lon = get_coordinates_for_location(location)
        
        # Realistic farm sizes (in acres)
        farm_size = random.choice([
            0.5, 1, 1.5, 2, 2.5, 3, 4, 5,  # Small farmers (most common)
            6, 7, 8, 10, 12, 15,  # Medium farmers
            20, 25, 30, 40, 50  # Large farmers (less common)
        ])
        
        # Contact numbers
        contact = f"+91-{random.randint(7000000000, 9999999999)}"
        
        farmers.append({
            'name': full_name,
            'location': location,
            'farm_size': farm_size,
            'farm_unit': 'acres',
            'contact': contact,
            'weather_location': location,
            'latitude': round(lat, 4),
            'longitude': round(lon, 4),
            'password': 'farmer123'
        })
    
    return farmers

def create_tools(farmers):
    """Create tool listings for farmers"""
    tools = []
    
    # Each farmer lists 1-3 tools
    for farmer in farmers:
        num_tools = random.randint(1, 3)
        farmer_tools = random.sample(FARMING_TOOLS, min(num_tools, len(FARMING_TOOLS)))
        
        for tool in farmer_tools:
            # Realistic rental rates (per day in INR)
            rates = {
                "Tractor": random.randint(800, 1500),
                "Power Tiller": random.randint(500, 800),
                "Rotavator": random.randint(300, 600),
                "Cultivator": random.randint(200, 400),
                "Harrow": random.randint(200, 350),
                "Seed Drill": random.randint(250, 450),
                "Sprayer": random.randint(150, 300),
                "Harvester": random.randint(1500, 2500),
                "Thresher": random.randint(600, 1000),
                "Water Pump": random.randint(200, 400),
                "Drip Irrigation System": random.randint(500, 1000),
                "Plough": random.randint(150, 250),
                "Leveler": random.randint(300, 500),
                "Reaper": random.randint(400, 700),
                "Weeder": random.randint(100, 200),
                "Chaff Cutter": random.randint(200, 350),
                "Trailer": random.randint(400, 700),
                "Ridger": random.randint(200, 400),
                "Disc Harrow": random.randint(300, 500),
                "Subsoiler": random.randint(350, 600)
            }
            
            rate = rates.get(tool, random.randint(200, 800))
            
            notes = random.choice([
                "Well maintained, fuel included",
                "Good condition, operator available",
                "Available immediately",
                "Recent service done",
                "Fuel extra",
                "Can deliver within 5km",
                "Minimum 4 hours booking",
                "Weekly rates available"
            ])
            
            tools.append({
                'Farmer': farmer['name'],
                'Location': farmer['location'],
                'Tool': tool,
                'Rate': rate,
                'Contact': farmer['contact'],
                'Notes': notes
            })
    
    return tools

def create_crops(farmers):
    """Create crop listings for farmers"""
    crops = []
    
    # About 60% of farmers have crops to sell
    selling_farmers = random.sample(farmers, int(len(farmers) * 0.6))
    
    for farmer in selling_farmers:
        num_crops = random.randint(1, 2)
        farmer_crops = random.sample(MAHARASHTRA_CROPS, min(num_crops, len(MAHARASHTRA_CROPS)))
        
        for crop in farmer_crops:
            # Realistic quantities based on crop type (in quintals)
            quantities = {
                "Sugarcane": random.randint(50, 500),
                "Cotton": random.randint(10, 100),
                "Soybean": random.randint(5, 50),
                "Jowar": random.randint(10, 80),
                "Bajra": random.randint(10, 70),
                "Wheat": random.randint(15, 100),
                "Tur (Pigeon Pea)": random.randint(5, 40),
                "Onion": random.randint(20, 200),
                "Tomato": random.randint(10, 150),
                "Potato": random.randint(20, 180),
                "Grapes": random.randint(5, 50),
                "Pomegranate": random.randint(5, 40),
                "Banana": random.randint(10, 100),
                "Mango": random.randint(5, 50),
                "Orange": random.randint(10, 80)
            }
            
            quantity = quantities.get(crop, random.randint(10, 100))
            
            # Realistic prices (per quintal in INR)
            prices = {
                "Sugarcane": random.randint(280, 350),
                "Cotton": random.randint(5500, 7000),
                "Soybean": random.randint(4000, 5500),
                "Jowar": random.randint(2500, 3500),
                "Bajra": random.randint(2200, 3000),
                "Wheat": random.randint(2000, 2500),
                "Tur (Pigeon Pea)": random.randint(6000, 8000),
                "Onion": random.randint(800, 2500),
                "Tomato": random.randint(1000, 3000),
                "Potato": random.randint(800, 1500),
                "Grapes": random.randint(3000, 6000),
                "Pomegranate": random.randint(4000, 8000),
                "Banana": random.randint(1500, 2500),
                "Mango": random.randint(3000, 5000),
                "Orange": random.randint(2000, 4000)
            }
            
            expected_price = prices.get(crop, random.randint(2000, 5000))
            
            # Listing date (within last 30 days)
            days_ago = random.randint(0, 30)
            listing_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            
            crops.append({
                'Farmer': farmer['name'],
                'Location': farmer['location'],
                'Crop': crop,
                'Quantity': f"{quantity} quintals",
                'Expected_Price': expected_price,
                'Contact': farmer['contact'],
                'Listing_Date': listing_date
            })
    
    return crops

def create_calendar_events(farmers):
    """Create sample calendar events for farmers"""
    events = []
    
    activities = [
        "Ploughing", "Sowing", "Irrigation", "Fertilizer Application",
        "Pesticide Spray", "Weeding", "Harvesting", "Market Visit",
        "Soil Testing", "Equipment Maintenance", "Seed Purchase",
        "Farm Meeting", "Training Session", "Crop Inspection"
    ]
    
    # Create 3-5 events per farmer
    for farmer in farmers[:20]:  # Only first 20 farmers to keep it manageable
        num_events = random.randint(3, 5)
        
        for _ in range(num_events):
            # Random date within next 60 days
            days_ahead = random.randint(0, 60)
            event_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            event_time = f"{random.randint(6, 18):02d}:00"
            
            activity = random.choice(activities)
            
            descriptions = [
                f"Complete {activity.lower()} for main field",
                f"Schedule {activity.lower()} with laborers",
                f"Priority: {activity}",
                f"Reminder: {activity} - bring necessary equipment",
                f"Important: Complete {activity.lower()} before rain"
            ]
            
            events.append({
                'farmer_name': farmer['name'],
                'event_date': event_date,
                'event_time': event_time,
                'event_title': activity,
                'event_description': random.choice(descriptions),
                'weather_alert': ''
            })
    
    return events

def populate_database():
    """Main function to populate the database"""
    print("🌾 Starting Maharashtra Farmer Database Population...")
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Create farmers
    print("\n👨‍🌾 Creating farmer profiles...")
    farmers = create_farmers(50)
    
    for farmer in farmers:
        try:
            c.execute("""INSERT OR IGNORE INTO farmers 
                        (name, location, farm_size, farm_unit, contact, weather_location, latitude, longitude, password)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                     (farmer['name'], farmer['location'], farmer['farm_size'], 
                      farmer['farm_unit'], farmer['contact'], farmer['weather_location'],
                      farmer['latitude'], farmer['longitude'], farmer['password']))
        except Exception as e:
            print(f"Error inserting farmer {farmer['name']}: {e}")
    
    conn.commit()
    print(f"✅ Added {len(farmers)} farmers")
    
    # Create tools
    print("\n🔧 Creating tool listings...")
    tools = create_tools(farmers)
    
    for tool in tools:
        try:
            c.execute("""INSERT INTO tools 
                        (Farmer, Location, Tool, Rate, Contact, Notes)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                     (tool['Farmer'], tool['Location'], tool['Tool'],
                      tool['Rate'], tool['Contact'], tool['Notes']))
        except Exception as e:
            print(f"Error inserting tool: {e}")
    
    conn.commit()
    print(f"✅ Added {len(tools)} tool listings")
    
    # Create crops
    print("\n🌾 Creating crop listings...")
    crops = create_crops(farmers)
    
    for crop in crops:
        try:
            c.execute("""INSERT INTO crops 
                        (Farmer, Location, Crop, Quantity, Expected_Price, Contact, Listing_Date)
                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                     (crop['Farmer'], crop['Location'], crop['Crop'],
                      crop['Quantity'], crop['Expected_Price'], crop['Contact'], crop['Listing_Date']))
        except Exception as e:
            print(f"Error inserting crop: {e}")
    
    conn.commit()
    print(f"✅ Added {len(crops)} crop listings")
    
    # Create calendar events
    print("\n📅 Creating calendar events...")
    events = create_calendar_events(farmers)
    
    for event in events:
        try:
            c.execute("""INSERT INTO calendar_events 
                        (farmer_name, event_date, event_time, event_title, event_description, weather_alert)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                     (event['farmer_name'], event['event_date'], event['event_time'],
                      event['event_title'], event['event_description'], event['weather_alert']))
        except Exception as e:
            print(f"Error inserting event: {e}")
    
    conn.commit()
    print(f"✅ Added {len(events)} calendar events")
    
    # Print summary
    print("\n" + "="*60)
    print("📊 DATABASE POPULATION SUMMARY")
    print("="*60)
    
    c.execute("SELECT COUNT(*) FROM farmers")
    farmer_count = c.fetchone()[0]
    print(f"👨‍🌾 Total Farmers: {farmer_count}")
    
    c.execute("SELECT COUNT(*) FROM tools")
    tool_count = c.fetchone()[0]
    print(f"🔧 Total Tools: {tool_count}")
    
    c.execute("SELECT COUNT(*) FROM crops")
    crop_count = c.fetchone()[0]
    print(f"🌾 Total Crops: {crop_count}")
    
    c.execute("SELECT COUNT(*) FROM calendar_events")
    event_count = c.fetchone()[0]
    print(f"📅 Total Events: {event_count}")
    
    print("\n📍 Sample Farmers by Location:")
    c.execute("SELECT location, COUNT(*) as count FROM farmers GROUP BY location ORDER BY count DESC LIMIT 10")
    for row in c.fetchall():
        print(f"   • {row[0]}: {row[1]} farmers")
    
    print("\n🔧 Most Listed Tools:")
    c.execute("SELECT Tool, COUNT(*) as count FROM tools GROUP BY Tool ORDER BY count DESC LIMIT 5")
    for row in c.fetchall():
        print(f"   • {row[0]}: {row[1]} listings")
    
    print("\n🌾 Most Listed Crops:")
    c.execute("SELECT Crop, COUNT(*) as count FROM crops GROUP BY Crop ORDER BY count DESC LIMIT 5")
    for row in c.fetchall():
        print(f"   • {row[0]}: {row[1]} listings")
    
    print("\n" + "="*60)
    print("✅ Database population completed successfully!")
    print("="*60)
    print("\n💡 You can now login with any farmer name and password: farmer123")
    print("📌 Example: Login as 'Ramesh Patil' with password 'farmer123'")
    
    conn.close()

if __name__ == "__main__":
    populate_database()
