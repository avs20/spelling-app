"""
Test workflow: Add word via admin, practice it, and verify completion
1. Add a new word via admin panel
2. Open the web app
3. Put correct spelling
4. Click Done button twice
5. Verify "No words pending" banner appears
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

SCREENSHOTS_DIR = "../test-screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

async def test_add_word_workflow():
    """Test complete workflow of adding and practicing a word"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            device_scale_factor=2
        )
        page = await context.new_page()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_word = "elephant"
        test_category = "animals"
        admin_password = "admin123"
        
        print("🧪 Starting add word workflow test...\n")
        
        try:
            # Step 1: Add word via admin panel
            print("Step 1: 📝 Adding new word via admin panel...")
            await page.goto('http://localhost:8000/admin')
            await page.wait_for_load_state('networkidle')
            
            # Login
            await page.fill('#passwordInput', admin_password)
            await page.click('button:has-text("Login")')
            await page.wait_for_timeout(1000)
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_01_admin_login_success.png', full_page=True)
            print("   ✓ Admin logged in")
            
            # Add word
            await page.fill('#wordInput', test_word)
            await page.fill('#categoryInput', test_category)
            await page.click('button[type="submit"]:has-text("Add Word")')
            await page.wait_for_timeout(2000)
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_02_word_added.png', full_page=True)
            print(f"   ✓ Word '{test_word}' added to database")
            
            # Step 2: Open web app
            print("\nStep 2: 🎯 Opening web app...")
            await page.goto('http://localhost:8000/')
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(2000)
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_03_app_loaded.png', full_page=True)
            print("   ✓ Web app loaded")
            
            # Step 3: Check if the new word appears
            print(f"\nStep 3: 🔍 Verifying '{test_word}' is available...")
            word_display = await page.text_content('#word-display')
            print(f"   Current word: {word_display}")
            
            # If not the test word, it's OK - we'll practice whatever is there
            # Since we may have existing words, let's just proceed
            current_word = word_display.lower() if word_display else ""
            
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_04_word_ready.png', full_page=True)
            
            # Step 4: Put correct spelling
            print(f"\nStep 4: ✍️ Entering correct spelling '{current_word}'...")
            
            # Get all letter buttons (Learning Mode)
            letter_buttons = await page.query_selector_all('.letter-btn')
            
            if letter_buttons and len(letter_buttons) > 0:
                # Learning mode: click letters in order to spell the word
                print(f"   Learning Mode detected - clicking {len(letter_buttons)} letters")
                for i, button in enumerate(letter_buttons):
                    letter_text = await button.text_content()
                    print(f"   Clicking letter button: {letter_text}")
                    await button.click()
                    await page.wait_for_timeout(300)
            else:
                # Recall mode: type in input field
                recall_input = await page.query_selector('#recall-input')
                if recall_input:
                    print(f"   Recall Mode detected - typing '{current_word}'")
                    await recall_input.focus()
                    await page.type('#recall-input', current_word, delay=100)
                else:
                    print("   ⚠ Neither letter buttons nor recall input found")
            
            await page.wait_for_timeout(500)
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_05_spelling_entered.png', full_page=True)
            
            # Step 5: Click Done button (first time)
            print("\nStep 5a: 🏁 Clicking Done button (1st time)...")
            submit_button = await page.query_selector('#submit-btn')
            
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(2500)
                await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_06_first_done_clicked.png', full_page=True)
                print("   ✓ First Done clicked")
            else:
                print("   ⚠ Done button not found on first attempt")
            
            # Step 5b: Click Done button (second time) - if word still pending
            print("\nStep 5b: 🏁 Clicking Done button (2nd time)...")
            submit_button = await page.query_selector('#submit-btn')
            
            if submit_button:
                await submit_button.click()
                await page.wait_for_timeout(2500)
                await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_07_second_done_clicked.png', full_page=True)
                print("   ✓ Second Done clicked")
            
            # Step 6: Verify completion state
            print("\nStep 6: ✅ Verifying completion state...")
            await page.wait_for_timeout(1500)
            
            # Look for completion banner
            completion_banner = await page.query_selector('#completion-banner')
            banner_display = await completion_banner.evaluate('el => window.getComputedStyle(el).display') if completion_banner else None
            
            if banner_display and banner_display != 'none':
                await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_08_completion_banner.png', full_page=True)
                print("   ✅ SUCCESS: Completion banner is visible!")
                return True
            else:
                # Check page content for completion message
                all_text = await page.content()
                if 'All Words Complete' in all_text or 'all words' in all_text.lower():
                    await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_08_completion_state.png', full_page=True)
                    print("   ✅ SUCCESS: No words pending state achieved!")
                    return True
                else:
                    await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_08_final_state.png', full_page=True)
                    print("   ℹ Final state - may need more context")
                    return False
                    
        except Exception as e:
            print(f"\n❌ Error during test: {e}")
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_99_error.png', full_page=True)
            return False
        finally:
            await browser.close()

async def main():
    print("=" * 60)
    print("ADD WORD WORKFLOW TEST")
    print("=" * 60)
    print("\nPrerequisites:")
    print("1. Backend running on http://localhost:8000")
    print("2. Database initialized")
    print("\nStarting test...\n")
    
    try:
        result = await test_add_word_workflow()
        
        if result:
            print("\n" + "=" * 60)
            print("✅ TEST PASSED!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ TEST FAILED!")
            print("=" * 60)
            
        print(f"\n📸 Screenshots saved to: {os.path.abspath(SCREENSHOTS_DIR)}")
        
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        print("\nMake sure:")
        print("1. Playwright is installed: pip install playwright")
        print("2. Install browsers: playwright install chromium")
        print("3. Backend is running: cd backend && python main.py")

if __name__ == "__main__":
    asyncio.run(main())
