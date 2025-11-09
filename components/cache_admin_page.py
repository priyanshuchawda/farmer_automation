# components/cache_admin_page.py
"""
Cache Administration Page
Allows admins to view and manage the prediction cache
"""

import streamlit as st
from database.cache_manager import CacheManager

def render_cache_admin_page():
    """Render cache administration interface."""
    
    st.header("🗄️ Cache Management System")
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%); 
                padding: 20px; border-radius: 12px; margin-bottom: 20px; 
                border-left: 5px solid #4CAF50;'>
        <h4 style='color: #2E8B57; margin: 0;'>Smart Caching System</h4>
        <p style='margin: 8px 0 0 0; color: #666;'>
            Reduces API costs by caching weather, market data, and predictions for 24 hours.
            This improves performance and saves money on repeated searches.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize cache manager
    cache = CacheManager()
    
    # Get cache info
    cache_info = cache.get_cache_info()
    stats = cache_info['statistics']
    
    # Overview metrics
    st.subheader("📊 Cache Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Weather Cached", cache_info['weather_cached'], help="Cached weather entries")
    with col2:
        st.metric("Prices Cached", cache_info['market_prices_cached'], help="Cached market price entries")
    with col3:
        st.metric("Predictions Cached", cache_info['predictions_cached'], help="Cached prediction entries")
    with col4:
        st.metric("Total Entries", cache_info['total_cached'], help="Total cached entries")
    
    st.markdown("---")
    
    # Cache Statistics
    st.subheader("📈 Cache Performance Statistics")
    
    if stats:
        col1, col2, col3 = st.columns(3)
        
        # Weather Stats
        with col1:
            if 'weather' in stats:
                w_stats = stats['weather']
                st.markdown(f"""
                <div style='background: #E3F2FD; padding: 15px; border-radius: 10px; border-left: 4px solid #2196F3;'>
                    <h4 style='margin: 0; color: #1976D2;'>🌤️ Weather Cache</h4>
                    <p style='margin: 10px 0 5px 0;'><strong>Hit Rate:</strong> {w_stats['hit_rate']}%</p>
                    <p style='margin: 5px 0;'><strong>Hits:</strong> {w_stats['hits']} | <strong>Misses:</strong> {w_stats['misses']}</p>
                    <p style='margin: 5px 0 0 0; font-size: 12px;'>Total: {w_stats['total_requests']} requests</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No weather cache statistics yet")
        
        # Market Price Stats
        with col2:
            if 'market_price' in stats:
                m_stats = stats['market_price']
                st.markdown(f"""
                <div style='background: #FFF3E0; padding: 15px; border-radius: 10px; border-left: 4px solid #FF9800;'>
                    <h4 style='margin: 0; color: #F57C00;'>💰 Market Price Cache</h4>
                    <p style='margin: 10px 0 5px 0;'><strong>Hit Rate:</strong> {m_stats['hit_rate']}%</p>
                    <p style='margin: 5px 0;'><strong>Hits:</strong> {m_stats['hits']} | <strong>Misses:</strong> {m_stats['misses']}</p>
                    <p style='margin: 5px 0 0 0; font-size: 12px;'>Total: {m_stats['total_requests']} requests</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No market price cache statistics yet")
        
        # Prediction Stats
        with col3:
            if 'prediction' in stats:
                p_stats = stats['prediction']
                st.markdown(f"""
                <div style='background: #E8F5E9; padding: 15px; border-radius: 10px; border-left: 4px solid #4CAF50;'>
                    <h4 style='margin: 0; color: #388E3C;'>🤖 Prediction Cache</h4>
                    <p style='margin: 10px 0 5px 0;'><strong>Hit Rate:</strong> {p_stats['hit_rate']}%</p>
                    <p style='margin: 5px 0;'><strong>Hits:</strong> {p_stats['hits']} | <strong>Misses:</strong> {p_stats['misses']}</p>
                    <p style='margin: 5px 0 0 0; font-size: 12px;'>Total: {p_stats['total_requests']} requests</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No prediction cache statistics yet")
    else:
        st.info("No cache statistics available yet. Statistics will appear after first cache usage.")
    
    st.markdown("---")
    
    # Cache Management Actions
    st.subheader("🔧 Cache Management Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧹 Clear Expired Cache", use_container_width=True):
            result = cache.clear_expired_cache()
            if result['total_deleted'] > 0:
                st.success(f"✅ Cleared {result['total_deleted']} expired entries!")
                st.info(f"Weather: {result['weather_deleted']}, Prices: {result['market_price_deleted']}, Predictions: {result['prediction_deleted']}")
            else:
                st.info("No expired entries found")
            st.rerun()
    
    with col2:
        if st.button("🌤️ Clear Weather Cache", use_container_width=True):
            cache.clear_weather_cache()
            st.success("✅ Weather cache cleared!")
            st.rerun()
    
    with col3:
        if st.button("💰 Clear Price Cache", use_container_width=True):
            cache.clear_market_price_cache()
            st.success("✅ Market price cache cleared!")
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🤖 Clear Prediction Cache", use_container_width=True):
            cache.clear_prediction_cache()
            st.success("✅ Prediction cache cleared!")
            st.rerun()
    
    with col2:
        if st.button("⚠️ Clear ALL Cache", use_container_width=True, type="secondary"):
            if st.checkbox("I confirm clearing all cache data"):
                cache.clear_all_cache()
                st.success("✅ All cache data cleared!")
                st.rerun()
            else:
                st.warning("Please confirm to clear all cache")
    
    st.markdown("---")
    
    # Cache Benefits Info
    st.subheader("💡 Cache System Benefits")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Cost Savings:**
        - Reduces API calls to Weather API
        - Reduces Google Search grounding usage
        - Saves AI AI tokens
        - Lower monthly API costs
        """)
    
    with col2:
        st.markdown("""
        **Performance:**
        - Instant responses for cached data
        - Better user experience
        - Reduced latency
        - Less API rate limiting
        """)
    
    st.info("💡 **Tip:** Cache is automatically managed. Weather data cached for 6 hours, market prices and predictions for 24 hours.")


