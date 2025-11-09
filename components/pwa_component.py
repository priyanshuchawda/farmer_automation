import streamlit as st
import streamlit.components.v1 as components


def inject_pwa_code():
    """Inject PWA initialization code into Streamlit app"""
    pwa_code = """
    <script>
        // Register Service Worker
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/static/service-worker.js')
                    .then(registration => {
                        console.log('ServiceWorker registered:', registration);
                    })
                    .catch(error => {
                        console.log('ServiceWorker registration failed:', error);
                    });
            });
        }

        // PWA Install Prompt
        let deferredPrompt;
        let installButton = null;

        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            showInstallButton();
        });

        function showInstallButton() {
            if (!installButton) {
                installButton = document.createElement('button');
                installButton.textContent = '📱 Install App';
                installButton.style.cssText = `
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: #4CAF50;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 25px;
                    font-size: 16px;
                    cursor: pointer;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    z-index: 9999;
                    font-weight: bold;
                `;
                installButton.addEventListener('click', async () => {
                    if (deferredPrompt) {
                        deferredPrompt.prompt();
                        const { outcome } = await deferredPrompt.userChoice;
                        console.log(`User response: ${outcome}`);
                        deferredPrompt = null;
                        installButton.remove();
                    }
                });
                document.body.appendChild(installButton);
            }
        }

        window.addEventListener('appinstalled', () => {
            console.log('PWA installed successfully');
            if (installButton) {
                installButton.remove();
            }
        });
    </script>
    
    <link rel="manifest" href="/static/manifest.json">
    <meta name="theme-color" content="#4CAF50">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="FarmerMarket">
    <link rel="apple-touch-icon" href="/static/icon-192.png">
    """
    
    components.html(pwa_code, height=0)


def render_pwa_install_banner():
    """Render a banner encouraging PWA installation"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    ">
        <h4 style="margin: 0 0 10px 0;">📱 Install as App</h4>
        <p style="margin: 0; font-size: 14px;">
            Install this app on your device for a better experience!
            <br>Works offline and launches like a native app.
        </p>
    </div>
    """, unsafe_allow_html=True)
