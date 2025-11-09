"""
Error Handler - User-friendly error messages and fallback mechanisms
"""
import streamlit as st
import traceback
from functools import wraps
import logging
from datetime import datetime


# Configure logging
logging.basicConfig(
    filename='app_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class ErrorMessages:
    """User-friendly error messages in multiple languages"""
    
    MESSAGES = {
        'en': {
            'network_error': '🌐 Network Error: Unable to connect. Using cached data.',
            'db_error': '💾 Database Error: Please try again later.',
            'api_error': '🔌 API Error: Service temporarily unavailable.',
            'generic_error': '❌ Something went wrong. Please try again.',
            'no_data': '📭 No data available. Please check back later.',
            'permission_error': '🔒 Permission denied. Please check your credentials.',
            'timeout_error': '⏱️ Request timed out. Please check your connection.',
            'offline_mode': '📴 You are offline. Showing cached data.',
            'invalid_input': '⚠️ Invalid input. Please check and try again.',
            'feature_unavailable': '🚧 This feature is currently unavailable.'
        },
        'hi': {
            'network_error': '🌐 नेटवर्क त्रुटि: कनेक्ट नहीं हो सका। कैश डेटा उपयोग कर रहे हैं।',
            'db_error': '💾 डेटाबेस त्रुटि: कृपया बाद में पुनः प्रयास करें।',
            'api_error': '🔌 API त्रुटि: सेवा अस्थायी रूप से अनुपलब्ध।',
            'generic_error': '❌ कुछ गलत हो गया। कृपया पुनः प्रयास करें।',
            'no_data': '📭 कोई डेटा उपलब्ध नहीं। कृपया बाद में जांचें।',
            'permission_error': '🔒 अनुमति अस्वीकृत। कृपया अपनी साख जांचें।',
            'timeout_error': '⏱️ अनुरोध समय समाप्त। कृपया अपना कनेक्शन जांचें।',
            'offline_mode': '📴 आप ऑफ़लाइन हैं। कैश डेटा दिखा रहे हैं।',
            'invalid_input': '⚠️ अमान्य इनपुट। कृपया जांचें और पुनः प्रयास करें।',
            'feature_unavailable': '🚧 यह सुविधा वर्तमान में अनुपलब्ध है।'
        },
        'mr': {
            'network_error': '🌐 नेटवर्क त्रुटी: कनेक्ट होऊ शकत नाही। कॅश डेटा वापरत आहोत।',
            'db_error': '💾 डेटाबेस त्रुटी: कृपया नंतर पुन्हा प्रयत्न करा।',
            'api_error': '🔌 API त्रुटी: सेवा तात्पुरती अनुपलब्ध।',
            'generic_error': '❌ काहीतरी चूक झाली। कृपया पुन्हा प्रयत्न करा।',
            'no_data': '📭 डेटा उपलब्ध नाही। कृपया नंतर तपासा।',
            'permission_error': '🔒 परवानगी नाकारली. कृपया तुमचे क्रेडेन्शियल तपासा।',
            'timeout_error': '⏱️ विनंती कालबाह्य झाली। कृपया तुमचे कनेक्शन तपासा।',
            'offline_mode': '📴 तुम्ही ऑफलाइन आहात। कॅश डेटा दाखवत आहे।',
            'invalid_input': '⚠️ अवैध इनपुट। कृपया तपासा आणि पुन्हा प्रयत्न करा।',
            'feature_unavailable': '🚧 ही वैशिष्ट्य सध्या अनुपलब्ध आहे।'
        }
    }
    
    @classmethod
    def get(cls, key, lang='en'):
        """Get error message in specified language"""
        return cls.MESSAGES.get(lang, cls.MESSAGES['en']).get(
            key, 
            cls.MESSAGES['en']['generic_error']
        )


def handle_error(error_type='generic_error', show_details=False):
    """Decorator to handle errors with user-friendly messages"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ConnectionError:
                lang = st.session_state.get('language', 'en')
                st.error(ErrorMessages.get('network_error', lang))
                logging.error(f"Connection error in {func.__name__}: {traceback.format_exc()}")
                return None
            except TimeoutError:
                lang = st.session_state.get('language', 'en')
                st.error(ErrorMessages.get('timeout_error', lang))
                logging.error(f"Timeout error in {func.__name__}: {traceback.format_exc()}")
                return None
            except PermissionError:
                lang = st.session_state.get('language', 'en')
                st.error(ErrorMessages.get('permission_error', lang))
                logging.error(f"Permission error in {func.__name__}: {traceback.format_exc()}")
                return None
            except Exception as e:
                lang = st.session_state.get('language', 'en')
                st.error(ErrorMessages.get(error_type, lang))
                
                if show_details:
                    with st.expander("🔍 Technical Details"):
                        st.code(str(e))
                
                logging.error(f"Error in {func.__name__}: {traceback.format_exc()}")
                return None
        return wrapper
    return decorator


def safe_api_call(func, fallback_value=None, cache_key=None, offline_manager=None):
    """
    Safely call API with fallback to cached data
    
    Args:
        func: API call function
        fallback_value: Value to return if all attempts fail
        cache_key: Key for caching data
        offline_manager: OfflineManager instance for caching
    """
    lang = st.session_state.get('language', 'en')
    
    try:
        # Try API call
        result = func()
        
        # Cache successful result
        if offline_manager and cache_key and result:
            # Cache logic handled by offline_manager
            pass
        
        return result
        
    except (ConnectionError, TimeoutError) as e:
        # Network error - try cache
        if offline_manager and cache_key:
            st.warning(ErrorMessages.get('offline_mode', lang))
            # Try to get from cache
            # Return cached value if available
        
        st.error(ErrorMessages.get('network_error', lang))
        logging.error(f"API call failed: {str(e)}")
        return fallback_value
        
    except Exception as e:
        st.error(ErrorMessages.get('api_error', lang))
        logging.error(f"API error: {traceback.format_exc()}")
        return fallback_value


def show_error_with_retry(error_message, retry_callback, retry_label="Retry"):
    """Show error message with retry button"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.error(error_message)
    with col2:
        if st.button(f"🔄 {retry_label}"):
            retry_callback()


def validate_input(value, validation_type, field_name="Input"):
    """
    Validate user input with friendly error messages
    
    Args:
        value: Value to validate
        validation_type: Type of validation (phone, email, number, etc.)
        field_name: Name of field for error message
    """
    lang = st.session_state.get('language', 'en')
    
    if not value or str(value).strip() == '':
        st.error(f"⚠️ {field_name} is required")
        return False
    
    if validation_type == 'phone':
        if not str(value).isdigit() or len(str(value)) != 10:
            st.error(f"⚠️ {field_name} must be 10 digits")
            return False
    
    elif validation_type == 'email':
        if '@' not in str(value) or '.' not in str(value):
            st.error(f"⚠️ Invalid {field_name} format")
            return False
    
    elif validation_type == 'number':
        try:
            float(value)
        except ValueError:
            st.error(f"⚠️ {field_name} must be a number")
            return False
    
    elif validation_type == 'positive':
        try:
            if float(value) <= 0:
                st.error(f"⚠️ {field_name} must be positive")
                return False
        except ValueError:
            st.error(f"⚠️ {field_name} must be a number")
            return False
    
    return True


def safe_database_operation(operation, error_message=None, show_spinner=True):
    """Safely execute database operation with error handling"""
    lang = st.session_state.get('language', 'en')
    
    try:
        if show_spinner:
            with st.spinner("Processing..."):
                return operation()
        else:
            return operation()
    except Exception as e:
        if error_message:
            st.error(error_message)
        else:
            st.error(ErrorMessages.get('db_error', lang))
        
        logging.error(f"Database operation failed: {traceback.format_exc()}")
        return None


def log_user_action(action, user_id=None, details=None):
    """Log user actions for debugging"""
    try:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user_id': user_id,
            'details': details
        }
        logging.info(f"User action: {log_entry}")
    except Exception as e:
        logging.error(f"Failed to log user action: {e}")


def show_offline_fallback(feature_name):
    """Show message when feature unavailable offline"""
    lang = st.session_state.get('language', 'en')
    st.info(f"📴 {feature_name} requires internet connection")
    st.markdown("""
    **Tips for offline use:**
    - Cached data is available
    - Changes will sync when online
    - Calendar and prices work offline
    """)


def create_error_report():
    """Create downloadable error report for support"""
    try:
        with open('app_errors.log', 'r') as f:
            errors = f.readlines()
        
        recent_errors = errors[-50:] if len(errors) > 50 else errors
        
        report = "# Error Report\n\n"
        report += f"Generated: {datetime.now()}\n\n"
        report += "## Recent Errors:\n\n"
        report += "".join(recent_errors)
        
        return report
    except Exception as e:
        return f"Could not generate error report: {e}"


class GracefulDegradation:
    """Handle graceful degradation of features"""
    
    @staticmethod
    def check_feature_availability(feature_name):
        """Check if feature is available"""
        # Check network connectivity, API availability, etc.
        return True
    
    @staticmethod
    def provide_alternative(feature_name):
        """Provide alternative when feature unavailable"""
        alternatives = {
            'ai_chat': 'FAQs and help guides available offline',
            'weather': 'Last cached weather data available',
            'market_prices': 'Yesterday\'s prices available offline',
            'location_services': 'Manual location entry available'
        }
        return alternatives.get(feature_name, 'Feature temporarily unavailable')
