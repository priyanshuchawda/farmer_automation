import streamlit as st
import streamlit.components.v1 as components
from weather.ai_client import AIClient

def get_browser_location():
    """Get location from browser GPS"""
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 20px;
                background: #f5f5f5;
            }
            .location-container {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            button {
                background: #2E8B57;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                width: 100%;
                margin-bottom: 10px;
            }
            button:hover {
                background: #3CB371;
            }
            .status {
                margin-top: 15px;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
            }
            .success {
                background: #E8F5E9;
                color: #2E8B57;
                border-left: 4px solid #4CAF50;
            }
            .error {
                background: #FFEBEE;
                color: #C62828;
                border-left: 4px solid #F44336;
            }
            .info {
                background: #E3F2FD;
                color: #1976D2;
                border-left: 4px solid #2196F3;
            }
            .loading {
                background: #FFF9C4;
                color: #F57F17;
                border-left: 4px solid #FFC107;
            }
        </style>
    </head>
    <body>
        <div class="location-container">
            <h3>📍 GPS Location Verification</h3>
            <button onclick="getLocation()">🛰️ Get My GPS Location</button>
            <div id="status"></div>
        </div>

        <script>
            function getLocation() {
                const statusDiv = document.getElementById('status');
                
                if (!navigator.geolocation) {
                    statusDiv.className = 'status error';
                    statusDiv.innerHTML = '❌ Geolocation is not supported by your browser';
                    return;
                }

                statusDiv.className = 'status loading';
                statusDiv.innerHTML = '🔄 Getting your location...';

                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        const accuracy = position.coords.accuracy;
                        
                        statusDiv.className = 'status success';
                        statusDiv.innerHTML = `
                            ✅ <strong>GPS Location Found!</strong><br>
                            📍 Latitude: ${lat.toFixed(6)}<br>
                            📍 Longitude: ${lon.toFixed(6)}<br>
                            🎯 Accuracy: ±${Math.round(accuracy)} meters
                        `;
                        
                        // Send data to Streamlit
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            value: {
                                latitude: lat,
                                longitude: lon,
                                accuracy: accuracy,
                                timestamp: new Date().toISOString()
                            }
                        }, '*');
                    },
                    function(error) {
                        let message = '';
                        switch(error.code) {
                            case error.PERMISSION_DENIED:
                                message = '❌ Location access denied. Please allow location access in your browser settings.';
                                break;
                            case error.POSITION_UNAVAILABLE:
                                message = '❌ Location information is unavailable.';
                                break;
                            case error.TIMEOUT:
                                message = '❌ Location request timed out.';
                                break;
                            default:
                                message = '❌ An unknown error occurred.';
                        }
                        statusDiv.className = 'status error';
                        statusDiv.innerHTML = message;
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 10000,
                        maximumAge: 0
                    }
                );
            }
        </script>
    </body>
    </html>
    """
    
    location_data = components.html(html_code, height=250)
    return location_data

def verify_location_with_AI(latitude, longitude):
    """Verify location using AI API to get address"""
    try:
        ai_client = AIClient()
        location_info = ai_client.get_location_from_coordinates(latitude, longitude)
        return location_info
    except Exception as e:
        st.error(f"Error verifying location with AI: {str(e)}")
        return None

def render_location_verification_widget():
    """Render the location verification widget"""
    st.markdown("### 🌍 Location Verification System")
    st.markdown("Verify your location using both GPS and AI to ensure accuracy")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🛰️ GPS Verification")
        st.caption("Most accurate - uses your device GPS")
        
        # Option to use browser GPS or manual entry
        gps_method = st.radio("GPS Input Method:", ["Browser GPS", "Manual GPS Entry"], key="gps_method")
        
        if gps_method == "Browser GPS":
            # Get GPS location from browser
            gps_data = get_browser_location()
            
            if gps_data and isinstance(gps_data, dict):
                st.success("✅ GPS location captured!")
                
                # Store in session state
                st.session_state.gps_latitude = gps_data.get('latitude')
                st.session_state.gps_longitude = gps_data.get('longitude')
                st.session_state.gps_accuracy = gps_data.get('accuracy')
                
                # Display GPS coordinates
                st.metric("Latitude", f"{gps_data.get('latitude', 0):.6f}")
                st.metric("Longitude", f"{gps_data.get('longitude', 0):.6f}")
                st.metric("Accuracy", f"±{gps_data.get('accuracy', 0):.0f}m")
            
            # Show stored GPS data if available
            elif st.session_state.get('gps_latitude'):
                st.info("📍 GPS data stored in session")
                st.metric("Latitude", f"{st.session_state.gps_latitude:.6f}")
                st.metric("Longitude", f"{st.session_state.gps_longitude:.6f}")
                if st.session_state.get('gps_accuracy'):
                    st.metric("Accuracy", f"±{st.session_state.gps_accuracy:.0f}m")
        
        else:
            # Manual GPS entry
            st.info("📝 Enter GPS coordinates from your device")
            manual_gps_lat = st.number_input("GPS Latitude", value=0.0, format="%.6f", key="manual_gps_lat")
            manual_gps_lon = st.number_input("GPS Longitude", value=0.0, format="%.6f", key="manual_gps_lon")
            
            if st.button("✅ Use These GPS Coordinates", use_container_width=True):
                if manual_gps_lat != 0.0 and manual_gps_lon != 0.0:
                    st.session_state.gps_latitude = manual_gps_lat
                    st.session_state.gps_longitude = manual_gps_lon
                    st.session_state.gps_accuracy = None
                    st.success("✅ GPS coordinates saved!")
                    st.rerun()
                else:
                    st.error("❌ Please enter valid coordinates")
    
    with col2:
        st.markdown("#### 🤖 AI AI Verification")
        st.caption("Provides location context and address")
        
        # Manual location input for AI verification
        location_text = st.text_input(
            "Enter your location:",
            placeholder="e.g., Pune, Maharashtra",
            key="AI_location_input"
        )
        
        if st.button("🔍 Verify with AI", use_container_width=True):
            if location_text:
                with st.spinner("🤖 Verifying with AI AI..."):
                    ai_client = AIClient()
                    coords = ai_client.get_coordinates_from_google_search(location_text)
                    
                    if coords:
                        st.session_state.AI_latitude = coords['lat']
                        st.session_state.AI_longitude = coords['lon']
                        
                        st.success(f"✅ Location verified: {location_text}")
                        st.metric("Latitude", f"{coords['lat']:.6f}")
                        st.metric("Longitude", f"{coords['lon']:.6f}")
                    else:
                        st.error("❌ Could not verify location")
            else:
                st.warning("⚠️ Please enter a location")
    
    # Comparison section if both are available
    if (st.session_state.get('gps_latitude') and 
        st.session_state.get('AI_latitude')):
        
        st.markdown("---")
        st.markdown("### 📊 Location Comparison")
        
        gps_lat = st.session_state.gps_latitude
        gps_lon = st.session_state.gps_longitude
        gem_lat = st.session_state.AI_latitude
        gem_lon = st.session_state.AI_longitude
        
        # Calculate distance between two points
        from math import radians, cos, sin, asin, sqrt
        
        def haversine(lat1, lon1, lat2, lon2):
            """Calculate distance between two points on Earth"""
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371  # Radius of Earth in kilometers
            return c * r
        
        distance = haversine(gps_lat, gps_lon, gem_lat, gem_lon)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🛰️ GPS Location", 
                     f"({gps_lat:.4f}, {gps_lon:.4f})")
        
        with col2:
            st.metric("🤖 AI Location", 
                     f"({gem_lat:.4f}, {gem_lon:.4f})")
        
        with col3:
            st.metric("📏 Distance Apart", f"{distance:.2f} km")
        
        # Recommendation
        if distance < 1:
            st.success("✅ Both locations match! Using GPS coordinates (more accurate)")
            final_lat = gps_lat
            final_lon = gps_lon
            trust_level = "High"
        elif distance < 10:
            st.info("ℹ️ Small difference detected. Using GPS coordinates.")
            final_lat = gps_lat
            final_lon = gps_lon
            trust_level = "Medium"
        else:
            st.warning(f"⚠️ Large difference ({distance:.2f} km). Please verify your inputs.")
            final_lat = gps_lat
            final_lon = gps_lon
            trust_level = "Low - Verification needed"
        
        st.session_state.verified_latitude = final_lat
        st.session_state.verified_longitude = final_lon
        st.session_state.location_trust_level = trust_level
        
        # Display final decision
        st.markdown("---")
        st.markdown("### ✅ Final Verified Location")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div style='background:#E8F5E9;padding:15px;border-radius:10px;border-left:4px solid #4CAF50;'>
                <strong>📍 Selected Coordinates:</strong><br>
                Latitude: {final_lat:.6f}<br>
                Longitude: {final_lon:.6f}<br>
                <strong>🔒 Trust Level:</strong> {trust_level}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("💾 Save Verified Location to Profile", 
                        use_container_width=True, 
                        type="primary"):
                # This will be handled by the parent component
                st.session_state.save_verified_location = True
                st.success("✅ Location marked for saving!")
                return {
                    'latitude': final_lat,
                    'longitude': final_lon,
                    'trust_level': trust_level
                }
    
    return None


