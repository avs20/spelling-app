"""
Test workflow: Complete all 3 initial words and verify completion banner
1. Reset database to 3 initial words (bee, spider, butterfly)
2. Practice word 1 with correct spelling
3. Practice word 2 with correct spelling
4. Practice word 3 with correct spelling
5. Verify "All Words Complete!" banner appears with display: block
"""

import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime
from database import reset_db_to_initial

SCREENSHOTS_DIR = "../test-screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

async def test_complete_all_words():
    """Test completing all 3 initial words to reach completion state"""
    
    # Reset database first
    print("Resetting database to 3 initial words...")
    reset_db_to_initial()
    print("✓ Database reset to: bee, spider, butterfly\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            device_scale_factor=2
        )
        page = await context.new_page()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("🧪 Starting complete all words test...\n")
        
        try:
            # Open web app
            print("📱 Opening web app...")
            await page.goto('http://localhost:8000/')
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(1500)
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_00_app_start.png', full_page=True)
            print("✓ Web app loaded\n")
            
            words_completed = []
            
            # Practice each word
            for word_num in range(1, 4):
                print(f"{'='*50}")
                print(f"WORD {word_num}/3")
                print(f"{'='*50}")
                
                # Get current word
                word_display = await page.text_content('#word-display')
                print(f"Current word: {word_display}\n")
                
                await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_{word_num:02d}a_word_{word_num}_ready.png', full_page=True)
                
                # Enter correct spelling
                print(f"Entering spelling: {word_display}")
                letter_buttons = await page.query_selector_all('.letter-btn')
                
                if letter_buttons and len(letter_buttons) > 0:
                    # Learning mode: click letters in correct order
                    word_upper = word_display.upper()
                    print(f"Target spelling (uppercase): {word_upper}")
                    
                    for target_letter in word_upper:
                        # Find button with this letter
                        for button in letter_buttons:
                            button_text = await button.text_content()
                            if button_text.strip() == target_letter:
                                print(f"  Clicking: {target_letter}")
                                await button.click()
                                await page.wait_for_timeout(200)
                                break
                else:
                    # Recall mode: type
                    recall_input = await page.query_selector('#recall-input')
                    if recall_input:
                        print(f"Recall mode: typing {word_display}")
                        await recall_input.focus()
                        await page.type('#recall-input', word_display, delay=50)
                
                await page.wait_for_timeout(500)
                await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_{word_num:02d}b_spelling_entered.png', full_page=True)
                print("✓ Spelling entered")
                
                # Submit
                print("Submitting answer...")
                submit_button = await page.query_selector('#submit-btn')
                if submit_button:
                    await submit_button.click()
                    await page.wait_for_timeout(2500)
                    await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_{word_num:02d}c_submitted.png', full_page=True)
                    print("✓ Submitted\n")
                    words_completed.append(word_display)
                
                # Check if we're at completion or next word loaded
                if word_num < 3:
                    # Not the last word, should have next word loaded
                    next_word = await page.text_content('#word-display')
                    print(f"Next word loaded: {next_word}\n")
            
            # Verify completion banner
            print(f"{'='*50}")
            print("VERIFICATION: Checking completion banner")
            print(f"{'='*50}\n")
            
            # Wait longer for app to complete transition
            print("Waiting for app to load next word or completion screen (3 seconds)...")
            await page.wait_for_timeout(3000)
            
            # Debug: get word display text
            word_display_final = await page.text_content('#word-display')
            print(f"Final word-display text: '{word_display_final}'")
            
            # Debug: get main content display
            main_content = await page.query_selector('#main-content')
            if main_content:
                main_display = await main_content.evaluate('el => window.getComputedStyle(el).display')
                print(f"Main content display: {main_display}")
            
            # Check completion banner visibility
            completion_banner = await page.query_selector('#completion-banner')
            
            if not completion_banner:
                print("❌ Completion banner element not found")
                await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_99_error_no_banner_element.png', full_page=True)
                return False
            
            # Get computed style
            display_style = await completion_banner.evaluate('el => window.getComputedStyle(el).display')
            print(f"Banner display style: {display_style}\n")
            
            # Get banner visibility
            is_visible = await completion_banner.evaluate('el => el.offsetParent !== null')
            print(f"Banner is visible: {is_visible}")
            
            # Get banner text
            banner_text = await completion_banner.text_content()
            print(f"Banner text: {banner_text}\n")
            
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_99_final_completion.png', full_page=True)
            
            # Verify
            if display_style == 'block' or is_visible:
                print(f"{'='*50}")
                print("✅ SUCCESS: Completion banner is visible!")
                print(f"{'='*50}")
                print(f"\nWords completed: {', '.join(words_completed)}")
                return True
            else:
                print(f"{'='*50}")
                print("❌ FAILED: Banner not visible")
                print(f"{'='*50}")
                print(f"Display style: {display_style}")
                print(f"Offsetparent null: {not is_visible}")
                return False
                
        except Exception as e:
            print(f"\n❌ Error during test: {e}")
            import traceback
            traceback.print_exc()
            await page.screenshot(path=f'{SCREENSHOTS_DIR}/{timestamp}_99_error.png', full_page=True)
            return False
        finally:
            await browser.close()

async def main():
    print("=" * 60)
    print("COMPLETE ALL WORDS TEST")
    print("=" * 60)
    print("\nPrerequisites:")
    print("1. Backend running on http://localhost:8000")
    print("2. Database will be reset to 3 initial words")
    print("\nStarting test...\n")
    
    try:
        result = await test_complete_all_words()
        
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
        print("1. Backend is running: cd backend && python main.py")

if __name__ == "__main__":
    asyncio.run(main())
