"""
Phase 12: Visual regression testing with JWT authentication
Automated screenshot capture of all app screens and states
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

# Create screenshots directory
SCREENSHOTS_DIR = "../test-screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# Test credentials (JWT-based authentication)
TEST_EMAIL = "visual_test_parent@test.com"
TEST_PASSWORD = "VisualTest123!"
TEST_CHILD_NAME = "Visual Test Child"

async def ensure_test_user_exists():
    """Register test user if doesn't exist"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Try to register test user
            await page.goto('http://localhost:8002/register.html')
            await page.fill('input[name="email"]', TEST_EMAIL)
            await page.fill('input[name="password"]', TEST_PASSWORD)
            await page.fill('input[name="confirm_password"]', TEST_PASSWORD)
            await page.click('button:has-text("Register")')
            
            # Wait for navigation to login or success
            await page.wait_for_timeout(2000)
            print("✓ Test user registered")
        except Exception as e:
            print(f"ℹ Test user may already exist: {str(e)[:50]}")
        finally:
            await browser.close()

async def login_and_get_child_id(page):
    """Login and return the selected child ID"""
    # Navigate to login
    await page.goto('http://localhost:8002/login.html')
    
    # Fill login form
    await page.fill('input[name="email"]', TEST_EMAIL)
    await page.fill('input[name="password"]', TEST_PASSWORD)
    await page.click('button:has-text("Login")')
    
    # Wait for token to be saved
    await page.wait_for_function(
        'localStorage.getItem("authToken")',
        timeout=10000
    )
    await page.wait_for_timeout(500)
    
    # Navigate to child selector
    await page.goto('http://localhost:8002/select-child.html')
    await page.wait_for_load_state('networkidle')
    
    # Check if test child exists, if not create one
    try:
        # Try to find and click the test child
        child_btn = page.locator(f'.child-button:has-text("{TEST_CHILD_NAME}")').first
        await child_btn.click(timeout=2000)
    except Exception:
        # Child doesn't exist, create one
        print("   Creating test child...")
        await page.fill('input[name="childName"]', TEST_CHILD_NAME)
        await page.fill('input[name="childAge"]', '5')
        await page.click('button:has-text("Add Child")')
        await page.wait_for_timeout(1000)
        
        # Click the newly created child
        child_btn = page.locator(f'.child-button:has-text("{TEST_CHILD_NAME}")').first
        await child_btn.click()
    
    await page.wait_for_timeout(500)
    
    # Click "Start Practicing"
    await page.click('button:has-text("Start Practicing")')
    await page.wait_for_url("**/index.html", timeout=10000)
    
    # Get child ID from localStorage
    child_id = await page.evaluate('localStorage.getItem("selectedChildId")')
    return child_id

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
        
        try:
            # Test 1: Login Page
            print("\n1️⃣ Testing login flow...")
            await page.goto('http://localhost:8002/login.html')
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_01_login_page.png', full_page=True)
            print("   ✓ Login page captured")
            
            # Test 2-7: Main App with authentication
            print("\n2️⃣ Testing main app with JWT auth...")
            child_id = await login_and_get_child_id(page)
            print(f"   ✓ Logged in and selected child (ID: {child_id})")
            
            # Test 2: Main App - Initial Load
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_02_main_app_initial.png', full_page=True)
            print("   ✓ Initial load captured")
            
            # Test 3: Main App - Drawing canvas
            await page.click('#pen-btn')
            await page.wait_for_timeout(500)
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_03_main_app_pen_mode.png', full_page=True)
            print("   ✓ Pen mode captured")
            
            # Test 4: Main App - Eraser mode
            await page.click('#eraser-btn')
            await page.wait_for_timeout(500)
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_04_main_app_eraser_mode.png', full_page=True)
            print("   ✓ Eraser mode captured")
            
            # Test 5: Main App - Color picker
            await page.click('#color-picker')
            await page.wait_for_timeout(500)
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_05_main_app_color_picker.png', full_page=True)
            print("   ✓ Color picker captured")
            
            # Test 6: Main App - Dark mode
            await page.click('#dark-mode-toggle')
            await page.wait_for_timeout(500)
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_06_main_app_dark_mode.png', full_page=True)
            print("   ✓ Dark mode captured")
            
            # Test 7: Main App - Progress badge
            await page.click('#dark-mode-toggle')  # Back to light mode
            await page.wait_for_timeout(500)
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_07_main_app_with_badge.png', full_page=True)
            print("   ✓ Progress badge captured")
            
            # Test 8: Parent Dashboard
            print("\n3️⃣ Testing parent dashboard...")
            await page.goto('http://localhost:8002/dashboard.html')
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(2000)  # Wait for stats to load
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_08_dashboard_main.png', full_page=True)
            print("   ✓ Dashboard main view captured")
            
            # Test 9: Dashboard - Scrolled to word performance
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight / 2)')
            await page.wait_for_timeout(500)
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_09_dashboard_word_performance.png', full_page=True)
            print("   ✓ Word performance section captured")
            
            # Test 10: Dashboard - Scrolled to drawings
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(500)
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_10_dashboard_drawings.png', full_page=True)
            print("   ✓ Drawings gallery captured")
            
            # Test 11: Admin Panel - Login required
            print("\n4️⃣ Testing admin panel...")
            await page.goto('http://localhost:8002/admin.html')
            await page.wait_for_load_state('networkidle')
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_11_admin_auth_required.png', full_page=True)
            print("   ✓ Admin auth required page captured")
            
            # Test 12: Admin Panel - Authenticated
            # Login again for admin access
            await page.goto('http://localhost:8002/login.html')
            await page.fill('input[name="email"]', TEST_EMAIL)
            await page.fill('input[name="password"]', TEST_PASSWORD)
            await page.click('button:has-text("Login")')
            await page.wait_for_function('localStorage.getItem("authToken")', timeout=10000)
            
            # Navigate to admin
            await page.goto('http://localhost:8002/admin.html')
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(1000)
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_12_admin_dashboard.png', full_page=True)
            print("   ✓ Admin dashboard captured")
            
            # Test 13: Admin Panel - Add word form
            await page.click('#wordInput')
            await page.wait_for_timeout(500)
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_13_admin_add_word.png', full_page=True)
            print("   ✓ Add word form captured")
            
            # Test 14: Compatibility Test Page
            print("\n5️⃣ Testing compatibility page...")
            await page.goto('http://localhost:8002/test-compatibility.html')
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(2000)  # Wait for tests to run
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_14_compatibility_tests.png', full_page=True)
            print("   ✓ Compatibility tests captured")
            
            # Test 15: Mobile viewport - Main app
            print("\n6️⃣ Testing mobile viewports...")
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
            await mobile_page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_15_mobile_main_app.png', full_page=True)
            print("   ✓ Mobile main app captured")
            
            # Test 16: Mobile - Dashboard
            await mobile_page.goto('http://localhost:8002/dashboard.html')
            await mobile_page.wait_for_load_state('networkidle')
            await mobile_page.wait_for_timeout(2000)
            await mobile_page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_16_mobile_dashboard.png', full_page=True)
            print("   ✓ Mobile dashboard captured")
            
            # Test 17: Tablet viewport - Main app
            print("\n7️⃣ Testing tablet viewports...")
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
            await tablet_page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_17_tablet_main_app.png', full_page=True)
            print("   ✓ Tablet main app captured")
            
            # Test 18: Tablet landscape
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
            await tablet_landscape_page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_18_tablet_landscape.png', full_page=True)
            print("   ✓ Tablet landscape captured")
            
            # Close browser
            await browser.close()
            
            print("\n✅ All screenshots captured successfully!")
            print(f"📁 Location: {os.path.abspath(SCREENSHOTS_DIR)}")
            print(f"📊 Total screenshots: 18")
            
            # Create index HTML to view all screenshots
            create_screenshot_index(timestamp)
            
        except Exception as e:
            print(f"\n❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()
            await browser.close()
            raise

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
            <p><strong>Total Screenshots:</strong> 18</p>
            <p><strong>Browser:</strong> Chromium (Playwright)</p>
            <p><strong>Authentication:</strong> JWT-based (Phase 12)</p>
            <p>Click any screenshot to view full size</p>
        </div>
        
        <div class="screenshot-grid">
            <div class="screenshot-item">
                <div class="screenshot-title">1. Login Page</div>
                <img src="{timestamp}_01_login_page.png" alt="Login Page" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">2. Main App - Initial Load</div>
                <img src="{timestamp}_02_main_app_initial.png" alt="Main App Initial" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">3. Main App - Pen Mode</div>
                <img src="{timestamp}_03_main_app_pen_mode.png" alt="Pen Mode" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">4. Main App - Eraser Mode</div>
                <img src="{timestamp}_04_main_app_eraser_mode.png" alt="Eraser Mode" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">5. Main App - Color Picker</div>
                <img src="{timestamp}_05_main_app_color_picker.png" alt="Color Picker" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">6. Main App - Dark Mode</div>
                <img src="{timestamp}_06_main_app_dark_mode.png" alt="Dark Mode" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">7. Main App - Progress Badge</div>
                <img src="{timestamp}_07_main_app_with_badge.png" alt="Progress Badge" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">8. Dashboard - Main</div>
                <img src="{timestamp}_08_dashboard_main.png" alt="Dashboard Main" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">9. Dashboard - Word Performance</div>
                <img src="{timestamp}_09_dashboard_word_performance.png" alt="Word Performance" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">10. Dashboard - Drawings</div>
                <img src="{timestamp}_10_dashboard_drawings.png" alt="Drawings Gallery" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">11. Admin - Auth Required</div>
                <img src="{timestamp}_11_admin_auth_required.png" alt="Admin Auth" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">12. Admin - Dashboard</div>
                <img src="{timestamp}_12_admin_dashboard.png" alt="Admin Dashboard" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">13. Admin - Add Word</div>
                <img src="{timestamp}_13_admin_add_word.png" alt="Add Word" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">14. Compatibility Tests</div>
                <img src="{timestamp}_14_compatibility_tests.png" alt="Compatibility" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">15. Mobile - Main App</div>
                <img src="{timestamp}_15_mobile_main_app.png" alt="Mobile Main" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">16. Mobile - Dashboard</div>
                <img src="{timestamp}_16_mobile_dashboard.png" alt="Mobile Dashboard" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">17. Tablet - Main App</div>
                <img src="{timestamp}_17_tablet_main_app.png" alt="Tablet Main" onclick="window.open(this.src)">
            </div>
            <div class="screenshot-item">
                <div class="screenshot-title">18. Tablet - Landscape</div>
                <img src="{timestamp}_18_tablet_landscape.png" alt="Tablet Landscape" onclick="window.open(this.src)">
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
    print("VISUAL REGRESSION TESTING - Phase 12 JWT Auth")
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
        asyncio.run(ensure_test_user_exists())
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
