"""
Notification Manager - Push notifications for PWA
"""
import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime


class NotificationManager:
    """Manage push notifications for PWA"""
    
    @staticmethod
    def request_permission():
        """Request notification permission from user"""
        notification_code = """
        <script>
        async function requestNotificationPermission() {
            if (!('Notification' in window)) {
                console.log('This browser does not support notifications');
                return 'unsupported';
            }
            
            if (Notification.permission === 'granted') {
                return 'granted';
            }
            
            if (Notification.permission !== 'denied') {
                const permission = await Notification.requestPermission();
                return permission;
            }
            
            return Notification.permission;
        }
        
        // Request permission when page loads
        requestNotificationPermission().then(permission => {
            console.log('Notification permission:', permission);
            if (permission === 'granted') {
                // Store permission in sessionStorage
                sessionStorage.setItem('notificationPermission', 'granted');
            }
        });
        </script>
        """
        components.html(notification_code, height=0)
    
    @staticmethod
    def show_notification(title, message, icon=None, tag=None):
        """
        Display a notification
        
        Args:
            title: Notification title
            message: Notification message
            icon: Icon URL (optional)
            tag: Notification tag for grouping (optional)
        """
        if icon is None:
            icon = '/static/icon-192.png'
        
        notification_data = {
            'title': title,
            'body': message,
            'icon': icon,
            'tag': tag or 'default',
            'timestamp': datetime.now().isoformat()
        }
        
        notification_code = f"""
        <script>
        function showNotification() {{
            if ('Notification' in window && Notification.permission === 'granted') {{
                const notificationData = {json.dumps(notification_data)};
                
                if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {{
                    // Send to service worker
                    navigator.serviceWorker.controller.postMessage({{
                        type: 'SHOW_NOTIFICATION',
                        data: notificationData
                    }});
                }} else {{
                    // Fallback to direct notification
                    new Notification(notificationData.title, {{
                        body: notificationData.body,
                        icon: notificationData.icon,
                        tag: notificationData.tag,
                        requireInteraction: false
                    }});
                }}
            }} else {{
                console.log('Notifications not permitted or not supported');
            }}
        }}
        
        showNotification();
        </script>
        """
        components.html(notification_code, height=0)
    
    @staticmethod
    def render_notification_settings():
        """Render notification settings UI"""
        st.markdown("### 🔔 Notification Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            notify_weather = st.checkbox(
                "Weather Alerts",
                value=st.session_state.get('notify_weather', True),
                help="Get notified about severe weather"
            )
            st.session_state['notify_weather'] = notify_weather
        
        with col2:
            notify_prices = st.checkbox(
                "Price Alerts",
                value=st.session_state.get('notify_prices', True),
                help="Get notified about price changes"
            )
            st.session_state['notify_prices'] = notify_prices
        
        col3, col4 = st.columns(2)
        
        with col3:
            notify_calendar = st.checkbox(
                "Calendar Reminders",
                value=st.session_state.get('notify_calendar', True),
                help="Get reminders for calendar events"
            )
            st.session_state['notify_calendar'] = notify_calendar
        
        with col4:
            notify_sync = st.checkbox(
                "Sync Notifications",
                value=st.session_state.get('notify_sync', False),
                help="Get notified when offline data syncs"
            )
            st.session_state['notify_sync'] = notify_sync
        
        # Test notification button
        if st.button("🔔 Test Notification"):
            NotificationManager.show_notification(
                "Test Notification",
                "If you see this, notifications are working! 🎉",
                tag="test"
            )
            st.success("Test notification sent!")
        
        # Request permission button
        st.markdown("---")
        if st.button("🔓 Enable Notifications"):
            NotificationManager.request_permission()
            st.info("Check your browser for permission prompt")


def notify_weather_alert(condition, temperature, location):
    """Send weather alert notification"""
    if st.session_state.get('notify_weather', True):
        NotificationManager.show_notification(
            f"⛈️ Weather Alert - {location}",
            f"{condition} - {temperature}°C",
            tag="weather"
        )


def notify_price_change(commodity, old_price, new_price):
    """Send price change notification"""
    if st.session_state.get('notify_prices', True):
        change = new_price - old_price
        direction = "📈" if change > 0 else "📉"
        NotificationManager.show_notification(
            f"{direction} Price Update: {commodity}",
            f"Changed from ₹{old_price} to ₹{new_price}",
            tag="price"
        )


def notify_calendar_event(event_title, event_time):
    """Send calendar event reminder"""
    if st.session_state.get('notify_calendar', True):
        NotificationManager.show_notification(
            "📅 Event Reminder",
            f"{event_title} at {event_time}",
            tag="calendar"
        )


def notify_sync_complete(items_synced):
    """Send sync completion notification"""
    if st.session_state.get('notify_sync', False):
        NotificationManager.show_notification(
            "✅ Sync Complete",
            f"{items_synced} items synchronized",
            tag="sync"
        )


def notify_offline_mode():
    """Notify user that app is in offline mode"""
    NotificationManager.show_notification(
        "📴 Offline Mode",
        "You're offline. Changes will sync when connected.",
        tag="offline"
    )


def notify_online_mode():
    """Notify user that app is back online"""
    NotificationManager.show_notification(
        "🟢 Back Online",
        "Connection restored. Syncing your data...",
        tag="online"
    )


def setup_notification_triggers():
    """Setup automatic notification triggers"""
    notification_code = """
    <script>
    // Monitor online/offline status
    let wasOffline = !navigator.onLine;
    
    window.addEventListener('online', () => {
        if (wasOffline) {
            // Show online notification
            if ('Notification' in window && Notification.permission === 'granted') {
                new Notification('🟢 Back Online', {
                    body: 'Connection restored. Syncing your data...',
                    icon: '/static/icon-192.png',
                    tag: 'online'
                });
            }
        }
        wasOffline = false;
    });
    
    window.addEventListener('offline', () => {
        wasOffline = true;
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('📴 Offline Mode', {
                body: "You're offline. Changes will sync when connected.",
                icon: '/static/icon-192.png',
                tag: 'offline'
            });
        }
    });
    
    // Listen for messages from service worker
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.addEventListener('message', (event) => {
            if (event.data.type === 'SYNC_COMPLETE') {
                if ('Notification' in window && Notification.permission === 'granted') {
                    new Notification('✅ Sync Complete', {
                        body: `${event.data.count} items synchronized`,
                        icon: '/static/icon-192.png',
                        tag: 'sync'
                    });
                }
            }
        });
    }
    </script>
    """
    components.html(notification_code, height=0)


def render_notification_banner():
    """Show notification permission banner if not granted"""
    permission_banner = """
    <script>
    if ('Notification' in window && Notification.permission === 'default') {
        const banner = document.createElement('div');
        banner.style.cssText = `
            position: fixed;
            top: 60px;
            left: 50%;
            transform: translateX(-50%);
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 9998;
            display: flex;
            align-items: center;
            gap: 15px;
            max-width: 90%;
        `;
        
        banner.innerHTML = `
            <span style="font-size: 24px;">🔔</span>
            <span style="flex: 1;">Enable notifications to get weather alerts, price updates, and reminders</span>
            <button onclick="requestNotifications(this)" style="
                background: white;
                color: #4CAF50;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                cursor: pointer;
                font-weight: bold;
            ">Enable</button>
            <button onclick="this.parentElement.remove()" style="
                background: transparent;
                color: white;
                border: none;
                cursor: pointer;
                font-size: 20px;
            ">×</button>
        `;
        
        document.body.appendChild(banner);
    }
    
    async function requestNotifications(button) {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            button.parentElement.remove();
            new Notification('🎉 Notifications Enabled!', {
                body: 'You will now receive important updates',
                icon: '/static/icon-192.png'
            });
        }
    }
    </script>
    """
    components.html(permission_banner, height=0)


def init_notifications():
    """Initialize notification system"""
    # Request permission if not already granted
    NotificationManager.request_permission()
    
    # Setup automatic triggers
    setup_notification_triggers()
    
    # Show permission banner if needed
    render_notification_banner()
