# components/labor_board.py
import streamlit as st
from database.db_functions import add_data, get_data
import pandas as pd
from datetime import date, timedelta
from components.translation_utils import t


def render_labor_board():
    """Main labor board page with tabs for jobs and workers."""
    st.markdown("""
    <style>
    .labor-card {
        background: #fff;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #FF9800;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .labor-card h3 {
        color: #F57C00;
        margin: 0 0 10px 0;
    }
    
    .labor-urgent {
        border-left-color: #F44336;
        background: #FFEBEE;
    }
    
    .worker-card {
        background: #fff;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #4CAF50;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .worker-card h3 {
        color: #2E8B57;
        margin: 0 0 10px 0;
    }
    
    @media (max-width: 768px) {
        .labor-card, .worker-card {
            padding: 15px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("👷 " + t("Worker & Labor Board"))
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%); 
                padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 2px solid #FF9800;'>
        <h3 style='color: #F57C00; margin: 0;'>🔥 {t("Most Important Feature for Farmers!")}</h3>
        <p style='margin: 10px 0 0 0; font-size: 16px;'>
            {t("Find workers for harvest, planting, spraying")} | {t("Workers can find jobs easily")}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs([
        "🔍 " + t("Find Workers"),
        "💼 " + t("Find Work"),
        "➕ " + t("Post Job/Availability")
    ])
    
    with tab1:
        render_job_postings()
    
    with tab2:
        render_worker_listings()
    
    with tab3:
        render_post_forms()


def render_job_postings():
    """Show all job postings where farmers need workers."""
    st.subheader(t("Jobs Available") + " - " + t("Farmers Need Workers"))
    
    # Load job postings
    try:
        conn = st.connection('database', type='sql')
        jobs_df = conn.query("SELECT rowid, * FROM labor_jobs ORDER BY created_date DESC")
    except:
        import sqlite3
        conn = sqlite3.connect('farmermarket.db')
        jobs_df = pd.read_sql_query("SELECT rowid, * FROM labor_jobs ORDER BY created_date DESC", conn)
        conn.close()
    
    if jobs_df.empty:
        st.info("📭 " + t("No jobs posted yet. Be the first to post!"))
        return
    
    # Filters
    st.markdown("#### 🔍 " + t("Filter Jobs"))
    filter_cols = st.columns(4)
    
    locations = ["All"] + sorted(jobs_df["location"].unique().tolist())
    work_types = ["All"] + sorted(jobs_df["work_type"].unique().tolist())
    
    with filter_cols[0]:
        selected_loc = st.selectbox(t("📍 Location"), locations, key="job_loc_filter")
    with filter_cols[1]:
        selected_work = st.selectbox(t("🌾 Work Type"), work_types, key="job_work_filter")
    with filter_cols[2]:
        status_filter = st.selectbox(t("📊 Status"), ["All", "Open", "Filled", "Closed"], key="job_status_filter")
    with filter_cols[3]:
        min_wage = st.number_input(t("💰 Min Wage/Day"), min_value=0, value=0, step=50, key="job_min_wage")
    
    # Apply filters
    filtered_jobs = jobs_df.copy()
    if selected_loc != "All":
        filtered_jobs = filtered_jobs[filtered_jobs["location"] == selected_loc]
    if selected_work != "All":
        filtered_jobs = filtered_jobs[filtered_jobs["work_type"] == selected_work]
    if status_filter != "All":
        filtered_jobs = filtered_jobs[filtered_jobs["status"] == status_filter]
    if min_wage > 0:
        filtered_jobs = filtered_jobs[filtered_jobs["wage_per_day"] >= min_wage]
    
    st.info(f"📋 {t('Showing')} {len(filtered_jobs)} {t('of')} {len(jobs_df)} {t('jobs')}")
    
    # Display jobs
    for idx, job in filtered_jobs.iterrows():
        is_urgent = (job.get('start_date') and 
                     pd.to_datetime(job['start_date']).date() <= date.today() + timedelta(days=3))
        
        card_class = "labor-card labor-urgent" if is_urgent else "labor-card"
        urgent_badge = "🔥 URGENT! " if is_urgent else ""
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"""
            <div class='{card_class}'>
                <h3>{urgent_badge}🚜 {job['work_type']}</h3>
                <p style='margin: 5px 0;'><strong>📍 {t("Location")}:</strong> {job['location']}</p>
                <p style='margin: 5px 0;'><strong>👥 {t("Workers Needed")}:</strong> {job['workers_needed']} {t("workers")}</p>
                <p style='margin: 5px 0;'><strong>📅 {t("Duration")}:</strong> {job['duration_days']} {t("days")}</p>
                <p style='margin: 5px 0;'><strong>💰 {t("Wage")}:</strong> ₹{job['wage_per_day']}/{t("day")}</p>
                <p style='margin: 5px 0;'><strong>📆 {t("Start Date")}:</strong> {job.get('start_date', 'Immediate')}</p>
                <p style='margin: 5px 0;'><strong>👤 {t("Posted by")}:</strong> {job['posted_by']}</p>
                <p style='margin: 5px 0;'><strong>📞 {t("Contact")}:</strong> {job['contact']}</p>
                <p style='margin: 10px 0 0 0; font-size: 14px; color: #666;'>{job.get('description', 'No additional details')}</p>
                <p style='margin: 10px 0 0 0;'><span style='background: {"#4CAF50" if job["status"] == "Open" else "#9E9E9E"}; 
                   color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px;'>{job['status']}</span></p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("<br>" * 2, unsafe_allow_html=True)
            if st.button(f"📞 {t('Call Now')}", key=f"job_call_{idx}", use_container_width=True):
                st.markdown(f"""
                <a href="tel:{job['contact']}" target="_blank" style="text-decoration: none;">
                    <button style="width: 100%; padding: 10px; background: #4CAF50; color: white; 
                            border: none; border-radius: 8px; font-size: 16px; cursor: pointer;">
                        📞 {job['contact']}
                    </button>
                </a>
                """, unsafe_allow_html=True)
            
            if st.button(f"💬 WhatsApp", key=f"job_wa_{idx}", use_container_width=True):
                message = f"Hi! I saw your job posting for {job['work_type']} work in {job['location']}. I'm interested!"
                wa_link = f"https://wa.me/91{job['contact'].replace('+91', '').replace('-', '')}?text={message}"
                st.markdown(f'<a href="{wa_link}" target="_blank">Open WhatsApp</a>', unsafe_allow_html=True)


def render_worker_listings():
    """Show all workers available for hire."""
    st.subheader(t("Available Workers") + " - " + t("Ready to Work"))
    
    # Load worker listings
    try:
        conn = st.connection('database', type='sql')
        workers_df = conn.query("SELECT rowid, * FROM worker_availability ORDER BY created_date DESC")
    except:
        import sqlite3
        conn = sqlite3.connect('farmermarket.db')
        workers_df = pd.read_sql_query("SELECT rowid, * FROM worker_availability ORDER BY created_date DESC", conn)
        conn.close()
    
    if workers_df.empty:
        st.info("📭 " + t("No workers registered yet."))
        return
    
    # Filters
    st.markdown("#### 🔍 " + t("Filter Workers"))
    filter_cols = st.columns(4)
    
    locations = ["All"] + sorted(workers_df["location"].unique().tolist())
    skills = ["All"] + sorted(workers_df["skills"].unique().tolist())
    
    with filter_cols[0]:
        selected_loc = st.selectbox(t("📍 Location"), locations, key="worker_loc_filter")
    with filter_cols[1]:
        selected_skill = st.selectbox(t("🛠️ Skills"), skills, key="worker_skill_filter")
    with filter_cols[2]:
        max_wage = st.number_input(t("💰 Max Wage/Day"), min_value=0, value=10000, step=50, key="worker_max_wage")
    with filter_cols[3]:
        min_exp = st.number_input(t("📚 Min Experience (years)"), min_value=0, value=0, step=1, key="worker_min_exp")
    
    # Apply filters
    filtered_workers = workers_df.copy()
    if selected_loc != "All":
        filtered_workers = filtered_workers[filtered_workers["location"] == selected_loc]
    if selected_skill != "All":
        filtered_workers = filtered_workers[filtered_workers["skills"].str.contains(selected_skill, case=False, na=False)]
    if max_wage < 10000:
        filtered_workers = filtered_workers[filtered_workers["wage_expected"] <= max_wage]
    if min_exp > 0:
        filtered_workers = filtered_workers[filtered_workers["experience_years"] >= min_exp]
    
    # Filter by availability
    filtered_workers = filtered_workers[filtered_workers["availability_status"] == "Available"]
    
    st.info(f"📋 {t('Showing')} {len(filtered_workers)} {t('of')} {len(workers_df)} {t('workers')}")
    
    # Display workers
    for idx, worker in filtered_workers.iterrows():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"""
            <div class='worker-card'>
                <h3>👷 {worker['worker_name']}</h3>
                <p style='margin: 5px 0;'><strong>📍 {t("Location")}:</strong> {worker['location']}</p>
                <p style='margin: 5px 0;'><strong>🛠️ {t("Skills")}:</strong> {worker['skills']}</p>
                <p style='margin: 5px 0;'><strong>💰 {t("Expected Wage")}:</strong> ₹{worker['wage_expected']}/{t("day")}</p>
                <p style='margin: 5px 0;'><strong>📚 {t("Experience")}:</strong> {worker.get('experience_years', 0)} {t("years")}</p>
                <p style='margin: 5px 0;'><strong>📞 {t("Contact")}:</strong> {worker['contact']}</p>
                <p style='margin: 10px 0 0 0; font-size: 14px; color: #666;'>{worker.get('description', 'No additional details')}</p>
                <p style='margin: 10px 0 0 0;'><span style='background: #4CAF50; color: white; 
                   padding: 5px 15px; border-radius: 20px; font-size: 12px;'>✅ {worker['availability_status']}</span></p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("<br>" * 2, unsafe_allow_html=True)
            if st.button(f"📞 {t('Call Now')}", key=f"worker_call_{idx}", use_container_width=True):
                st.markdown(f"""
                <a href="tel:{worker['contact']}" target="_blank" style="text-decoration: none;">
                    <button style="width: 100%; padding: 10px; background: #2E8B57; color: white; 
                            border: none; border-radius: 8px; font-size: 16px; cursor: pointer;">
                        📞 {worker['contact']}
                    </button>
                </a>
                """, unsafe_allow_html=True)
            
            if st.button(f"💬 WhatsApp", key=f"worker_wa_{idx}", use_container_width=True):
                message = f"Hi {worker['worker_name']}! I need workers for farm work in {worker['location']}. Are you available?"
                wa_link = f"https://wa.me/91{worker['contact'].replace('+91', '').replace('-', '')}?text={message}"
                st.markdown(f'<a href="{wa_link}" target="_blank">Open WhatsApp</a>', unsafe_allow_html=True)


def render_post_forms():
    """Forms to post job or worker availability."""
    farmer_name = st.session_state.get("farmer_name", "")
    profile = st.session_state.get("farmer_profile", {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_post_job_form(farmer_name, profile)
    
    with col2:
        render_post_worker_form(farmer_name, profile)


def render_post_job_form(farmer_name, profile):
    """Form for farmers to post job openings."""
    st.markdown("### 👨‍🌾 " + t("I Need Workers"))
    
    location_value = profile.get("location", "") if profile else ""
    contact_value = profile.get("contact", "") if profile else ""
    
    with st.form("post_job_form"):
        posted_by = st.text_input(t("Your Name"), value=farmer_name, key="job_poster_name")
        location = st.text_input(t("Location (Village)"), value=location_value, key="job_location")
        
        col1, col2 = st.columns(2)
        with col1:
            work_type = st.selectbox(
                t("Type of Work"),
                ["Harvesting", "Planting", "Weeding", "Spraying", "Irrigation", "General Farm Work", "Other"],
                key="job_work_type"
            )
            workers_needed = st.number_input(t("Workers Needed"), min_value=1, value=3, step=1, key="job_workers_count")
            duration_days = st.number_input(t("Duration (days)"), min_value=1, value=2, step=1, key="job_duration")
        
        with col2:
            wage_per_day = st.number_input(t("Wage per Day (₹)"), min_value=100, value=400, step=50, key="job_wage")
            start_date = st.date_input(t("Start Date"), value=date.today(), key="job_start_date")
            contact = st.text_input(t("Contact Number"), value=contact_value, key="job_contact")
        
        description = st.text_area(
            t("Additional Details"),
            placeholder=t("e.g., Tomato harvest, need experienced workers, food provided"),
            key="job_description"
        )
        
        submitted = st.form_submit_button(t("📢 Post Job"))
        
        if submitted:
            if posted_by and location and work_type and workers_needed > 0 and wage_per_day > 0 and contact:
                job_data = (
                    posted_by, location, work_type, workers_needed, duration_days,
                    wage_per_day, contact, description, start_date.strftime("%Y-%m-%d"), 'Open'
                )
                add_data("labor_jobs", job_data)
                st.success(f"✅ {t('Job posted successfully!')} {workers_needed} {t('workers needed for')} {work_type}!")
                st.rerun()
            else:
                st.error(t("Please fill in all required fields."))


def render_post_worker_form(farmer_name, profile):
    """Form for workers to post availability."""
    st.markdown("### 👷 " + t("I'm Available for Work"))
    
    location_value = profile.get("location", "") if profile else ""
    contact_value = profile.get("contact", "") if profile else ""
    
    with st.form("post_worker_form"):
        worker_name = st.text_input(t("Your Name"), key="worker_name")
        location = st.text_input(t("Location (Village)"), value=location_value, key="worker_location")
        
        col1, col2 = st.columns(2)
        with col1:
            skills = st.multiselect(
                t("Skills / Work Types"),
                ["Harvesting", "Planting", "Weeding", "Spraying", "Irrigation", "Tractor Operation", 
                 "Cattle Care", "General Farm Work", "Other"],
                key="worker_skills"
            )
            wage_expected = st.number_input(t("Expected Wage per Day (₹)"), min_value=100, value=350, step=50, key="worker_wage")
        
        with col2:
            experience_years = st.number_input(t("Years of Experience"), min_value=0, value=2, step=1, key="worker_exp")
            contact = st.text_input(t("Contact Number"), value=contact_value, key="worker_contact")
        
        description = st.text_area(
            t("About You"),
            placeholder=t("e.g., Experienced in tomato/onion harvest, can work in any weather, available immediately"),
            key="worker_description"
        )
        
        submitted = st.form_submit_button(t("📢 Post Availability"))
        
        if submitted:
            if worker_name and location and skills and wage_expected > 0 and contact:
                skills_str = ", ".join(skills)
                worker_data = (
                    worker_name, location, skills_str, wage_expected, contact,
                    experience_years, 'Available', description
                )
                add_data("worker_availability", worker_data)
                st.success(f"✅ {t('Profile posted successfully!')} {t('Farmers can now contact you')}!")
                st.rerun()
            else:
                st.error(t("Please fill in all required fields."))
