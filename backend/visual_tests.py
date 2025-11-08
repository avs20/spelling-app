"""
Phase 9: Visual regression testing
Automated screenshot capture of all app screens and states
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

# Create screenshots directory
SCREENSHOTS_DIR = "../test-screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

async def capture_screenshots():
    """Capture screenshots of all app pages and states"""
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            device_scale_factor=2  # Retina quality
        )
        page = await context.new_page()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("📸 Starting visual regression tests...")
        print(f"Screenshots will be saved to: {SCREENSHOTS_DIR}")
        
        # Test 1: Main App - Initial Load
        print("\n1️⃣ Testing main app (index.html)...")
        await page.goto('http://localhost:8002/index.html')
        await page.wait_for_load_state('networkidle')
        await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_01_main_app_initial.png', full_page=True)
        print("   ✓ Initial load captured")
        
        # Test 2: Main App - Drawing canvas
        await page.click('#pen-btn')
        await page.wait_for_timeout(500)
        await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_02_main_app_pen_mode.png', full_page=True)
        print("   ✓ Pen mode captured")
        
        # Test 3: Main App - Eraser mode
        await page.click('#eraser-btn')
        await page.wait_for_timeout(500)
        await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_03_main_app_eraser_mode.png', full_page=True)
        print("   ✓ Eraser mode captured")
        
        # Test 4: Main App - Color picker
        await page.click('#color-picker')
        await page.wait_for_timeout(500)
        await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_04_main_app_color_picker.png', full_page=True)
        print("   ✓ Color picker captured")
        
        # Test 5: Main App - Dark mode
        await page.click('#dark-mode-toggle')
        await page.wait_for_timeout(500)
        await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_05_main_app_dark_mode.png', full_page=True)
        print("   ✓ Dark mode captured")
        
        # Test 6: Main App - Progress badge
        await page.click('#dark-mode-toggle')  # Back to light mode
        await page.wait_for_timeout(500)
        await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_06_main_app_with_badge.png', full_page=True)
        print("   ✓ Progress badge captured")
        
        # Test 7: Admin Panel - Login
        print("\n2️⃣ Testing admin panel (admin.html)...")
        await page.goto('http://localhost:8002/admin.html')
        await page.wait_for_load_state('networkidle')
        await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_07_admin_login.png', full_page=True)
        print("   ✓ Admin login page captured")
        
        # Test 8: Admin Panel - Authenticated
        await page.fill('#passwordInput', 'admin123')
        await page.click('button:has-text("Login")')
        await page.wait_for_timeout(1000)
        await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_08_admin_dashboard.png', full_page=True)
        print("   ✓ Admin dashboard captured")
        
        # Test 9: Admin Panel - Add word form focused
        await page.click('#wordInput')
        await page.wait_for_timeout(500)
        await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_09_admin_add_word.png', full_page=True)
        print("   ✓ Add word form captured")
        
        # Test 10: Parent Dashboard
        print("\n3️⃣ Testing parent dashboard (dashboard.html)...")
        await page.goto('http://localhost:8002/dashboard.html')
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)  # Wait for stats to load
        await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_10_dashboard_main.png', full_page=True)
        print("   ✓ Dashboard main view captured")
        
        # Test 11: Dashboard - Scrolled to word performance
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight / 2)')
        await page.wait_for_timeout(500)
        await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_11_dashboard_word_performance.png', full_page=True)
        print("   ✓ Word performance section captured")
        
        # Test 12: Dashboard - Scrolled to drawings
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await page.wait_for_timeout(500)
        await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_12_dashboard_drawings.png', full_page=True)
        print("   ✓ Drawings gallery captured")
        
        # Test 13: Compatibility Test Page
        print("\n4️⃣ Testing compatibility page (test-compatibility.html)...")
        await page.goto('http://localhost:8002/test-compatibility.html')
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)  # Wait for tests to run
        await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_13_compatibility_tests.png', full_page=True)
        print("   ✓ Compatibility tests captured")
        
        # Test 14: Mobile viewport - Main app
        print("\n5️⃣ Testing mobile viewports...")
        await context.close()
        mobile_context = await browser.new_context(
            viewport={'width': 375, 'height': 812},  # iPhone X
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True
        )
        mobile_page = await mobile_context.new_page()
        
        await mobile_page.goto('http://localhost:8002/index.html')
        await mobile_page.wait_for_load_state('networkidle')
        await mobile_page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_14_mobile_main_app.png', full_page=True)
        print("   ✓ Mobile main app captured")
        
        # Test 15: Mobile - Dashboard
        await mobile_page.goto('http://localhost:8002/dashboard.html')
        await mobile_page.wait_for_load_state('networkidle')
        await mobile_page.wait_for_timeout(2000)
        await mobile_page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_15_mobile_dashboard.png', full_page=True)
        print("   ✓ Mobile dashboard captured")
        
        # Test 16: Tablet viewport - Main app
        print("\n6️⃣ Testing tablet viewports...")
        await mobile_context.close()
        tablet_context = await browser.new_context(
            viewport={'width': 1024, 'height': 768},  # iPad
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        tablet_page = await tablet_context.new_page()
        
        await tablet_page.goto('http://localhost:8002/index.html')
        await tablet_page.wait_for_load_state('networkidle')
        await tablet_page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_16_tablet_main_app.png', full_page=True)
        print("   ✓ Tablet main app captured")
        
        # Test 17: Tablet landscape
        await tablet_context.close()
        tablet_landscape_context = await browser.new_context(
            viewport={'width': 1024, 'height': 768},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        tablet_landscape_page = await tablet_landscape_context.new_page()
        
        await tablet_landscape_page.goto('http://localhost:8002/index.html')
        await tablet_landscape_page.wait_for_load_state('networkidle')
        await tablet_landscape_page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_17_tablet_landscape.png', full_page=True)
        print("   ✓ Tablet landscape captured")
        
        # Close browser
        await browser.close()
        
        print("\n✅ All screenshots captured successfully!")
        print(f"📁 Location: {os.path.abspath(SCREENSHOTS_DIR)}")
        print(f"📊 Total screenshots: 17")
        
        # Create index HTML to view all screenshots
        create_screenshot_index(timestamp)

def create_screenshot_index(timestamp):
    """Create an HTML index to view all screenshots"""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visual Test Results - {timestamp}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
        }}
        h1 {{
            color: #333;
            margin-bottom: 30px;
        }}
        .screenshot-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        .screenshot-item {{
            border: 2px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            background: white;
        }}
        .screenshot-item img {{
            width: 100%;
            height: auto;
            display: block;
            cursor: pointer;
            transition: transform 0.3s;
        }}
        .screenshot-item img:hover {{
            transform: scale(1.05);
        }}
        .screenshot-title {{
            padding: 15px;
            background: #667eea;
            color: white;
            font-weight: bold;
        }}
        .info {{
            background: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📸 Visual Regression Test Results</h1>
        <div class="info">
            <p><strong>Timestamp:</strong> {timestamp}</p>
            <p><strong>Total Screenshots:</strong> 17</p>
            <p><strong>Browser:</strong> Chromium (Playwright)</p>
            <p>Click any screenshot to view full size</p>
        </div>
        
        <div class="screenshot-grid">
            <div class="screenshot-item">
                <div class="screenshot-title">1. Main App - Initial Load</div>
                <img src="{timestamp}_01_main_app_initial.png" alt="Main App Initial" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">2. Main App - Pen Mode</div>
                <img src="{timestamp}_02_main_app_pen_mode.png" alt="Pen Mode" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">3. Main App - Eraser Mode</div>
                <img src="{timestamp}_03_main_app_eraser_mode.png" alt="Eraser Mode" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">4. Main App - Color Picker</div>
                <img src="{timestamp}_04_main_app_color_picker.png" alt="Color Picker" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">5. Main App - Dark Mode</div>
                <img src="{timestamp}_05_main_app_dark_mode.png" alt="Dark Mode" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">6. Main App - Progress Badge</div>
                <img src="{timestamp}_06_main_app_with_badge.png" alt="Progress Badge" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">7. Admin - Login</div>
                <img src="{timestamp}_07_admin_login.png" alt="Admin Login" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">8. Admin - Dashboard</div>
                <img src="{timestamp}_08_admin_dashboard.png" alt="Admin Dashboard" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">9. Admin - Add Word</div>
                <img src="{timestamp}_09_admin_add_word.png" alt="Add Word" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">10. Dashboard - Main</div>
                <img src="{timestamp}_10_dashboard_main.png" alt="Dashboard Main" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">11. Dashboard - Word Performance</div>
                <img src="{timestamp}_11_dashboard_word_performance.png" alt="Word Performance" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">12. Dashboard - Drawings</div>
                <img src="{timestamp}_12_dashboard_drawings.png" alt="Drawings Gallery" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">13. Compatibility Tests</div>
                <img src="{timestamp}_13_compatibility_tests.png" alt="Compatibility" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">14. Mobile - Main App</div>
                <img src="{timestamp}_14_mobile_main_app.png" alt="Mobile Main" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">15. Mobile - Dashboard</div>
                <img src="{timestamp}_15_mobile_dashboard.png" alt="Mobile Dashboard" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">16. Tablet - Main App</div>
                <img src="{timestamp}_16_tablet_main_app.png" alt="Tablet Main" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">17. Tablet - Landscape</div>
                <img src="{timestamp}_17_tablet_landscape.png" alt="Tablet Landscape" onclick="window.open(this.src)">
            </div>
        </div>
    </div>
</body>
</html>"""
    
    index_path = f'{SCREENSHOTS_DIR}/{timestamp}_index.html'
    with open(index_path, 'w') as f:
        f.write(html_content)
    
    print(f"\n📄 Screenshot index created: {os.path.abspath(index_path)}")
    print(f"   Open in browser to view all screenshots")

if __name__ == "__main__":
    print("=" * 60)
    print("VISUAL REGRESSION TESTING")
    print("=" * 60)
    print("\nPrerequisites:")
    print("1. Backend running on http://localhost:8000")
    print("2. Frontend running on http://localhost:8002")
    print("\nStarting tests in 3 seconds...")
    print("Press Ctrl+C to cancel")
    print("=" * 60 + "\n")
    
    try:
        import time
        time.sleep(3)
        asyncio.run(capture_screenshots())
    except KeyboardInterrupt:
        print("\n\n❌ Tests cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. Playwright is installed: uv pip install playwright")
        print("2. Install browsers: playwright install chromium")
        print("3. Backend is running: cd backend && uv run python main.py")
        print("4. Frontend is running: cd frontend && uv run python -m http.server 8002")
