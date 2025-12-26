"""
Script to create placeholder screenshots for PWA
Replace these with actual app screenshots for better presentation
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    def create_screenshot(width, height, filename, text):
        """Create a placeholder screenshot"""
        # Create image with white background
        img = Image.new('RGB', (width, height), color='#ffffff')
        draw = ImageDraw.Draw(img)
        
        # Add green header
        draw.rectangle([(0, 0), (width, 80)], fill='#4CAF50')
        
        # Add title text
        title = "Smart Farmer Marketplace"
        try:
            title_font = ImageFont.truetype("arial.ttf", 24)
            desc_font = ImageFont.truetype("arial.ttf", 16)
        except:
            title_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()
        
        # Draw title
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) // 2, 25), title, fill='white', font=title_font)
        
        # Add description text in center
        draw.text((width // 2 - 100, height // 2), text, fill='#333333', font=desc_font)
        
        # Add some decorative elements
        draw.rectangle([(20, 120), (width-20, 180)], fill='#f5f5f5', outline='#4CAF50', width=2)
        draw.rectangle([(20, 200), (width-20, 260)], fill='#f5f5f5', outline='#4CAF50', width=2)
        
        # Save
        static_dir = 'static'
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        
        filepath = os.path.join(static_dir, filename)
        img.save(filepath, 'PNG')
        print(f"Created {filepath}")
    
    # Create screenshots
    create_screenshot(540, 720, 'screenshot1.png', 'Mobile View')
    create_screenshot(1280, 720, 'screenshot2.png', 'Desktop View')
    
    print("\n✅ PWA screenshots created successfully!")
    print("\nRecommendation:")
    print("Replace these placeholder screenshots with actual app screenshots")
    print("showing your app's key features for better user engagement.")
    
except ImportError:
    print("PIL/Pillow not installed.")
    print("Run: pip install Pillow")
except Exception as e:
    print(f"Error creating screenshots: {e}")
