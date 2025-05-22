import { test, expect } from '@playwright/test';

test('Check first email in YOPmail', async ({ page }) => {
  test.setTimeout(120000); // Setting timeout to 2 minutes
  // Navigate to YOPmail
  await page.goto('https://yopmail.com/wm');
  
  // Wait for the login input to be visible and enter email
  await page.waitForSelector('#login');
  await page.fill('#login', 'sibendu@yopmail.com');
    // Click the arrow button to check emails
  await page.click('.material-icons-outlined.f36');

  // Wait for the inbox iframe to load
  await page.waitForSelector('#ifinbox');
    // Switch to the inbox iframe
  const inboxFrame = page.frameLocator('#ifinbox');
  
  // Wait for emails to load and click the first one
  await inboxFrame.locator('.m').first().waitFor({ state: 'visible', timeout: 10000 });
  await inboxFrame.locator('.m').first().click();  // Verify we're on the email view and check email content
  const mailFrame = page.frameLocator('#ifmail');
  await expect(mailFrame.locator('#mail')).toBeVisible();
  
  // Add a short delay to ensure frame is loaded
  await page.waitForTimeout(2000);
  
  // Wait for any content in the mail frame
  await mailFrame.locator('body').waitFor({ state: 'visible', timeout: 10000 });
    // Get text content directly from the mail body
  const mailContent = await mailFrame.locator('body').allInnerTexts();
  console.log('Mail content:', mailContent);

  // Verify the content exists somewhere in the email
  expect(mailContent.some(text => text.includes('This is a test message'))).toBeTruthy();

  // Take a screenshot of the email content
  await page.screenshot({ path: 'tests/email-screenshot.png', fullPage: true });
});
