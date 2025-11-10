#!/usr/bin/env python3
"""Script to populate labor board with realistic demo data."""

import sqlite3
from datetime import date, timedelta
import random

DB_NAME = 'farmermarket.db'

# Sample job postings
JOBS = [
    ("Ramesh Patil", "Wagholi", "Harvesting", 5, 3, 400, "+91-9876543210", "Tomato harvest, urgent! Food provided. Need experienced workers.", (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"), "Open"),
    ("Kiran Rathod", "Kharadi", "Planting", 3, 2, 350, "+91-9123456789", "Onion planting season. Prefer local workers.", (date.today() + timedelta(days=5)).strftime("%Y-%m-%d"), "Open"),
    ("Shankar Salve", "Pune", "Weeding", 2, 1, 300, "+91-8765432109", "Quick weeding job in wheat field. 1 acre.", (date.today() + timedelta(days=2)).strftime("%Y-%m-%d"), "Open"),
    ("Rajesh Patil", "Peth", "Spraying", 2, 1, 450, "+91-7539399108", "Pesticide spraying in cotton field. Safety equipment provided.", date.today().strftime("%Y-%m-%d"), "Open"),
    ("Vitthal Shelar", "Soyegaon", "Harvesting", 8, 5, 420, "+91-9812345678", "Rice harvest. Large farm. Need 8 workers for 5 days. Accommodation provided.", (date.today() + timedelta(days=3)).strftime("%Y-%m-%d"), "Open"),
    ("Mahesh Kale", "Akkalkot", "General Farm Work", 4, 4, 380, "+91-9223003339", "Mixed farm work - irrigation setup, cleaning, minor repairs.", (date.today() + timedelta(days=7)).strftime("%Y-%m-%d"), "Open"),
    ("Bharat Chavan", "Khatav", "Irrigation", 2, 2, 350, "+91-9808592783", "Setting up drip irrigation system. Need 2 helpers.", (date.today() + timedelta(days=4)).strftime("%Y-%m-%d"), "Open"),
    ("chandan", "Pune", "Harvesting", 4, 3, 450, "9876543210", "Wheat harvest in 10 acre field. Urgent requirement!", (date.today() + timedelta(days=1)).strftime("%Y-%m-%d"), "Open"),
]

# Sample worker availability
WORKERS = [
    ("Ramchandra Jadhav", "Wagholi", "Harvesting, Planting, Weeding", 350, "+91-9988776655", 5, "Available", "10 years experience in all types of farm work. Can work in any weather. Available immediately."),
    ("Suresh Kumar", "Kharadi", "Harvesting, General Farm Work", 300, "+91-8899001122", 3, "Available", "Experienced in tomato and onion harvest. Hard worker, punctual."),
    ("Ganesh More", "Pune", "Spraying, Weeding", 400, "+91-7766554433", 7, "Available", "Licensed for pesticide spraying. Own spraying equipment available."),
    ("Baban Deshmukh", "Wagholi", "Tractor Operation, Plowing", 550, "+91-9900112233", 12, "Available", "Experienced tractor driver. 12 years experience. Can operate all farm equipment."),
    ("Prakash Shinde", "Kharadi", "Harvesting, Planting, Irrigation", 380, "+91-8877665544", 6, "Available", "Specialist in drip irrigation installation. Available for long-term work."),
    ("Ashok Pawar", "Pune", "General Farm Work, Cattle Care", 320, "+91-7788996655", 4, "Available", "All-rounder. Can handle farm work and cattle care. Honest and reliable."),
    ("Vijay Thorat", "Peth", "Weeding, Planting", 280, "+91-9988774455", 2, "Available", "Young and energetic. Quick learner. Can work long hours."),
    ("Dnyaneshwar Mali", "Wagholi", "Harvesting", 400, "+91-8866553344", 8, "Available", "Expert in grape and sugarcane harvest. Team leader experience."),
]

def populate_labor_board():
    """Add sample labor jobs and worker availability."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    print("=" * 70)
    print("👷 POPULATING LABOR BOARD WITH DEMO DATA")
    print("=" * 70)
    print()
    
    # Add job postings
    print("📢 Adding Job Postings...\n")
    for job in JOBS:
        try:
            c.execute("""
                INSERT INTO labor_jobs 
                (posted_by, location, work_type, workers_needed, duration_days, wage_per_day, 
                 contact, description, start_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, job)
            print(f"  ✅ {job[0]} needs {job[3]} workers for {job[2]} in {job[1]} @ ₹{job[5]}/day")
        except Exception as e:
            print(f"  ⚠️ Job already exists or error: {e}")
    
    conn.commit()
    
    # Add worker availability
    print("\n👷 Adding Worker Profiles...\n")
    for worker in WORKERS:
        try:
            c.execute("""
                INSERT INTO worker_availability
                (worker_name, location, skills, wage_expected, contact, experience_years, 
                 availability_status, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, worker)
            print(f"  ✅ {worker[0]} from {worker[1]} - Skills: {worker[2][:30]}...")
        except Exception as e:
            print(f"  ⚠️ Worker already exists or error: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ LABOR BOARD POPULATED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\n📊 Stats:")
    print(f"   - {len(JOBS)} job postings added")
    print(f"   - {len(WORKERS)} workers registered")
    print(f"   - Ready to connect farmers and workers!")
    print(f"\n🎯 Go to: MARKETPLACE → 👷 Worker Board")
    print(f"\n💡 Login as 'chandan' to see his job posting!")

if __name__ == "__main__":
    populate_labor_board()
