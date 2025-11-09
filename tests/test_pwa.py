"""
Test script to verify PWA configuration
"""
import json
import os

def test_pwa_setup():
    print("🔍 Testing PWA Setup...\n")
    
    errors = []
    warnings = []
    success = []
    
    # Check static directory
    if os.path.exists('static'):
        success.append("✅ static/ directory exists")
    else:
        errors.append("❌ static/ directory missing")
    
    # Check manifest.json
    manifest_path = 'static/manifest.json'
    if os.path.exists(manifest_path):
        success.append("✅ manifest.json exists")
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Validate required fields
            required = ['name', 'short_name', 'start_url', 'display', 'icons']
            for field in required:
                if field in manifest:
                    success.append(f"  ✅ manifest.{field} configured")
                else:
                    errors.append(f"  ❌ manifest.{field} missing")
            
            # Check icons
            if 'icons' in manifest and len(manifest['icons']) >= 2:
                success.append(f"  ✅ {len(manifest['icons'])} icons defined")
            else:
                warnings.append("  ⚠️ Less than 2 icons defined")
                
        except Exception as e:
            errors.append(f"  ❌ manifest.json invalid: {e}")
    else:
        errors.append("❌ manifest.json missing")
    
    # Check service worker
    sw_path = 'static/service-worker.js'
    if os.path.exists(sw_path):
        success.append("✅ service-worker.js exists")
    else:
        errors.append("❌ service-worker.js missing")
    
    # Check icons
    for icon in ['icon-192.png', 'icon-512.png']:
        icon_path = f'static/{icon}'
        if os.path.exists(icon_path):
            size = os.path.getsize(icon_path)
            success.append(f"✅ {icon} exists ({size} bytes)")
        else:
            errors.append(f"❌ {icon} missing")
    
    # Check screenshots
    for screenshot in ['screenshot1.png', 'screenshot2.png']:
        screenshot_path = f'static/{screenshot}'
        if os.path.exists(screenshot_path):
            success.append(f"✅ {screenshot} exists")
        else:
            warnings.append(f"⚠️ {screenshot} missing (optional)")
    
    # Check PWA component
    pwa_component = 'components/pwa_component.py'
    if os.path.exists(pwa_component):
        success.append("✅ pwa_component.py exists")
    else:
        errors.append("❌ pwa_component.py missing")
    
    # Check config.toml
    config_path = '.streamlit/config.toml'
    if os.path.exists(config_path):
        success.append("✅ .streamlit/config.toml exists")
        with open(config_path, 'r') as f:
            config = f.read()
            if 'enableStaticServing = true' in config:
                success.append("  ✅ Static serving enabled")
            else:
                warnings.append("  ⚠️ Add 'enableStaticServing = true' to config.toml")
    else:
        warnings.append("⚠️ .streamlit/config.toml missing")
    
    # Print results
    print("=" * 60)
    print("SUCCESS:")
    print("=" * 60)
    for msg in success:
        print(msg)
    
    if warnings:
        print("\n" + "=" * 60)
        print("WARNINGS:")
        print("=" * 60)
        for msg in warnings:
            print(msg)
    
    if errors:
        print("\n" + "=" * 60)
        print("ERRORS:")
        print("=" * 60)
        for msg in errors:
            print(msg)
        print("\n❌ PWA setup incomplete. Please fix errors above.")
        return False
    else:
        print("\n" + "=" * 60)
        print("✅ PWA setup complete!")
        print("=" * 60)
        print("\n📱 Your app is now installable as a PWA!")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Visit http://localhost:8501")
        print("3. Look for the 'Install App' button")
        print("4. Test on mobile devices")
        print("\n📖 See PWA_SETUP.md for detailed instructions")
        return True

if __name__ == '__main__':
    test_pwa_setup()
