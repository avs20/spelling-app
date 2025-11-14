/**
 * Website UI Test - Automated checks for frontend
 * Usage: node test_website_ui.js
 */

const http = require('http');
const BASE_URL = 'http://localhost:8000';

// Color codes for output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m'
};

let testCount = 0;
let passedCount = 0;
let failedCount = 0;

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function test(name, result, expected = true) {
  testCount++;
  if ((result && expected) || (!result && !expected)) {
    passedCount++;
    log(`✓ Test ${testCount}: ${name}`, colors.green);
  } else {
    failedCount++;
    log(`✗ Test ${testCount}: ${name}`, colors.red);
  }
}

async function getPageContent(path) {
  return new Promise((resolve, reject) => {
    http.get(`${BASE_URL}${path}`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

async function runTests() {
  log('\n========================================', colors.blue);
  log('SPELLING APP WEBSITE UI TESTS', colors.blue);
  log('========================================\n', colors.blue);

  try {
    // Test 1: Check if server is running
    log('Testing Server Connectivity...', colors.yellow);
    try {
      const health = await getPageContent('/api/health');
      test('API health endpoint responds', health.includes('ok'));
    } catch (e) {
      test('API health endpoint responds', false);
    }
    log('');

    // Test 2: Check landing page
    log('Testing Landing Page...', colors.yellow);
    const indexPage = await getPageContent('/');
    test('Landing page loads', indexPage.length > 0);
    test('Index page has title', indexPage.includes('<title>'));
    test('Index page has canvas element', indexPage.includes('canvas'));
    test('Index page loads style.css', indexPage.includes('/static/style.css'));
    test('Index page loads app.js', indexPage.includes('/static/app.js'));
    test('Index page loads api.js', indexPage.includes('/static/api.js'));
    test('Index page loads canvas.js', indexPage.includes('/static/canvas.js'));
    log('');

    // Test 3: Check admin page
    log('Testing Admin Page...', colors.yellow);
    const adminPage = await getPageContent('/admin');
    test('Admin page loads', adminPage.length > 0);
    test('Admin page has form for adding words', adminPage.includes('form') || adminPage.includes('word'));
    log('');

    // Test 4: Check dashboard page
    log('Testing Dashboard Page...', colors.yellow);
    const dashboardPage = await getPageContent('/dashboard');
    test('Dashboard page loads', dashboardPage.length > 0);
    test('Dashboard has statistics elements', dashboardPage.includes('stats') || dashboardPage.includes('dashboard'));
    log('');

    // Test 5: Check login page
    log('Testing Login Page...', colors.yellow);
    const loginPage = await getPageContent('/login');
    test('Login page loads', loginPage.length > 0);
    test('Login page has form', loginPage.includes('form'));
    test('Login page has email input', loginPage.includes('email'));
    test('Login page has password input', loginPage.includes('password'));
    log('');

    // Test 6: Check register page
    log('Testing Register Page...', colors.yellow);
    const registerPage = await getPageContent('/register');
    test('Register page loads', registerPage.length > 0);
    test('Register page has form', registerPage.includes('form'));
    test('Register page has email input', registerPage.includes('email'));
    log('');

    // Test 7: Check child selector page
    log('Testing Child Selector Page...', colors.yellow);
    const selectChildPage = await getPageContent('/select-child');
    test('Child selector page loads', selectChildPage.length > 0);
    test('Child selector page has form', selectChildPage.includes('form') || selectChildPage.includes('child'));
    log('');

    // Test 8: Check user profile page
    log('Testing User Profile Page...', colors.yellow);
    const profilePage = await getPageContent('/user-profile');
    test('User profile page loads', profilePage.length > 0);
    test('User profile page has user info section', profilePage.includes('profile') || profilePage.includes('user'));
    log('');

    // Test 9: Check static files
    log('Testing Static Files...', colors.yellow);
    const cssFile = await getPageContent('/static/style.css');
    test('CSS file loads', cssFile.length > 0 && cssFile.includes(':root'));
    
    const apiJsFile = await getPageContent('/static/api.js');
    test('API.js file loads', apiJsFile.length > 0 && apiJsFile.includes('function'));
    
    const appJsFile = await getPageContent('/static/app.js');
    test('App.js file loads', appJsFile.length > 0 && appJsFile.includes('function'));
    
    const canvasJsFile = await getPageContent('/static/canvas.js');
    test('Canvas.js file loads', canvasJsFile.length > 0 && canvasJsFile.includes('function'));
    log('');

  } catch (error) {
    log(`Error running tests: ${error.message}`, colors.red);
  }

  // Print summary
  log('========================================', colors.blue);
  log('TEST SUMMARY', colors.blue);
  log('========================================', colors.blue);
  log(`Total Tests: ${testCount}`);
  log(`Passed: ${passedCount}`, colors.green);
  log(`Failed: ${failedCount}`, colors.red);
  
  if (failedCount === 0) {
    log('\n✓ All tests passed!', colors.green);
    process.exit(0);
  } else {
    log(`\n✗ ${failedCount} test(s) failed`, colors.red);
    process.exit(1);
  }
}

// Run tests
runTests();
