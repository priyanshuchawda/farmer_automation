"""
Script to create PWA icons for the Smart Farmer Marketplace
Run this script to generate icon-192.png and icon-512.png
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    def create_icon(size, filename):
        """Create a simple icon with text"""
        # Create image with green background
        img = Image.new('RGB', (size, size), color='#4CAF50')
        draw = ImageDraw.Draw(img)
        
        # Add text
        text = "🌾"
        try:
            # Try to use a larger font
            font_size = size // 2
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position (center)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size - text_width) // 2, (size - text_height) // 2)
        
        # Draw text
        draw.text(position, text, fill='white', font=font)
        
        # Save
        static_dir = 'static'
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        
        filepath = os.path.join(static_dir, filename)
        img.save(filepath, 'PNG')
        print(f"Created {filepath}")
    
    # Create icons
    create_icon(192, 'icon-192.png')
    create_icon(512, 'icon-512.png')
    
    print("\n✅ PWA icons created successfully!")
    print("Note: You can replace these with custom designed icons for better branding.")
    
except ImportError:
    print("PIL/Pillow not installed. Installing...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'Pillow'])
    print("Please run this script again after Pillow is installed.")
except Exception as e:
    print(f"Error creating icons: {e}")
    print("\nManual alternative:")
    print("1. Create two PNG images: icon-192.png (192x192) and icon-512.png (512x512)")
    print("2. Save them in the 'static' folder")
    print("3. Use your app logo or a farming-related icon")
