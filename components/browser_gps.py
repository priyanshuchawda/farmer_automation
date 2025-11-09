# components/browser_gps.py
"""
Browser GPS Detection Component
Uses JavaScript Geolocation API to detect user's location
"""

import streamlit as st
import streamlit.components.v1 as components

def render_browser_gps_detector():
    """
    Render a browser GPS detector that automatically gets user's location
    Automatically fills the coordinate input fields via JavaScript
    """
    
    # HTML + JavaScript for GPS detection with auto-fill
    gps_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .gps-container {
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            .gps-button {
                background: linear-gradient(135deg, #2E8B57 0%, #3CB371 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                width: 100%;
                margin-bottom: 20px;
                transition: all 0.3s ease;
            }
            .gps-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(46, 139, 87, 0.3);
            }
            .gps-button:active {
                transform: translateY(0);
            }
            .gps-button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .status-box {
                padding: 15px;
                border-radius: 8px;
                margin-top: 15px;
                display: none;
            }
            .status-box.show {
                display: block;
            }
            .status-loading {
                background-color: #FFF3E0;
                border-left: 4px solid #FF9800;
            }
            .status-success {
                background-color: #E8F5E9;
                border-left: 4px solid #4CAF50;
            }
            .status-error {
                background-color: #FFEBEE;
                border-left: 4px solid #F44336;
            }
            .coord-value {
                font-family: monospace;
                font-size: 18px;
                font-weight: bold;
                color: #2E8B57;
            }
            .info-box {
                background-color: #E3F2FD;
                border-left: 4px solid #2196F3;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #2E8B57;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                display: inline-block;
                margin-right: 10px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="gps-container">
            <div class="info-box">
                <b>🧭 Automatic GPS Detection</b><br>
                <small>Click the button below to detect your current location using your device's GPS</small>
            </div>
            
            <button id="gps-button" class="gps-button" onclick="getLocation()">
                🧭 Detect My Location Now
            </button>
            
            <div id="status-box" class="status-box"></div>
        </div>
        
        <script>
            function getLocation() {
                const button = document.getElementById('gps-button');
                const statusBox = document.getElementById('status-box');
                
                // Check if geolocation is supported
                if (!navigator.geolocation) {
                    showStatus('error', '❌ <b>Geolocation Not Supported</b><br>Your browser does not support location detection. Please use manual entry or GPS coordinates instead.');
                    return;
                }
                
                // Disable button and show loading
                button.disabled = true;
                button.innerHTML = '<span class="spinner"></span> Detecting GPS...';
                showStatus('loading', '🔍 <b>Requesting GPS Access...</b><br>Please allow location access when prompted by your browser.');
                
                // Get current position
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        // Success callback
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        const accuracy = position.coords.accuracy;
                        
                        // Show success message
                        showStatus('success', 
                            '✅ <b>GPS Location Detected Successfully!</b><br><br>' +
                            '<div style="background: #f0f0f0; padding: 15px; border-radius: 8px; margin: 10px 0;">' +
                            '<div style="font-size: 18px; font-weight: bold; margin-bottom: 10px;">📋 Detected Coordinates:</div>' +
                            '<div style="font-size: 20px; color: #2E8B57; font-weight: bold; margin: 5px 0;">📍 Latitude: ' + lat.toFixed(6) + '</div>' +
                            '<div style="font-size: 20px; color: #2E8B57; font-weight: bold; margin: 5px 0;">📍 Longitude: ' + lon.toFixed(6) + '</div>' +
                            '</div>' +
                            '🎯 Accuracy: ±' + accuracy.toFixed(0) + ' meters<br><br>' +
                            '<small>✅ Auto-filling coordinates now...</small>'
                        );
                        
                        console.log('GPS Detected - Latitude:', lat, 'Longitude:', lon, 'Accuracy:', accuracy);
                        
                        // Auto-fill by reloading parent page with query params
                        setTimeout(() => {
                            try {
                                const parentUrl = new URL(window.parent.location.href);
                                parentUrl.searchParams.set('gps_lat', lat.toFixed(6));
                                parentUrl.searchParams.set('gps_lon', lon.toFixed(6));
                                window.parent.location.href = parentUrl.toString();
                            } catch (e) {
                                console.error('Could not auto-fill:', e);
                                button.disabled = false;
                                button.innerHTML = '🔄 Detect Again';
                            }
                        }, 1000);
                    },
                    function(error) {
                        // Error callback
                        let errorMsg = '';
                        switch(error.code) {
                            case error.PERMISSION_DENIED:
                                errorMsg = '❌ <b>Permission Denied</b><br>You denied the location access request. Please enable location permissions in your browser settings and try again.';
                                break;
                            case error.POSITION_UNAVAILABLE:
                                errorMsg = '❌ <b>Location Unavailable</b><br>Your location information is not available. Make sure GPS is enabled on your device.';
                                break;
                            case error.TIMEOUT:
                                errorMsg = '❌ <b>Request Timeout</b><br>The request to get your location timed out. Please try again.';
                                break;
                            default:
                                errorMsg = '❌ <b>Unknown Error</b><br>An unknown error occurred while getting your location.';
                        }
                        
                        showStatus('error', errorMsg + '<br><br><small>💡 Try using manual entry or GPS coordinates instead.</small>');
                        
                        // Re-enable button
                        button.disabled = false;
                        button.innerHTML = '🧭 Try Again';
                    },
                    {
                        enableHighAccuracy: true,  // Use GPS if available
                        timeout: 10000,            // 10 second timeout
                        maximumAge: 0              // Don't use cached position
                    }
                );
            }
            
            function showStatus(type, message) {
                const statusBox = document.getElementById('status-box');
                statusBox.className = 'status-box status-' + type + ' show';
                statusBox.innerHTML = message;
            }
        </script>
    </body>
    </html>
    """
    
    # Render the component with increased height to see everything
    components.html(gps_html, height=500)
    
    # can remove this below one, 
    # Instructions below the component
    # st.markdown("""
    # <div style='background-color: #FFF3E0; padding: 15px; border-radius: 8px; border-left: 4px solid #FF9800; margin-top: 20px;'>
    #     <b>ℹ️ How Browser GPS Works:</b><br>
    #     <small>
    #     1. Click "Detect My Location Now" button above<br>
    #     2. Browser will ask for location permission - Click "Allow"<br>
    #     3. GPS coordinates will be detected and displayed<br>
    #     4. Copy the coordinates to the fields below<br>
    #     5. Click "Use These GPS Coordinates" to save them
    #     </small>
    # </div>
    
    # <div style='background-color: #FFEBEE; padding: 15px; border-radius: 8px; border-left: 4px solid #F44336; margin-top: 15px;'>
    #     <b>⚠️ Important Notes:</b><br>
    #     <small>
    #     • <b>HTTPS Required:</b> Browser GPS works best on secure (https://) sites<br>
    #     • <b>Mobile Better:</b> Works better on phones with built-in GPS<br>
    #     • <b>Laptop GPS:</b> May use Wi-Fi location (less accurate)<br>
    #     • <b>If GPS Fails:</b> Use manual entry or enter coordinates from a GPS app
    #     </small>
    # </div>
    # """, unsafe_allow_html=True)
