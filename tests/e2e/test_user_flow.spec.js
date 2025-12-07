import { test, expect } from '@playwright/test'

test.describe('User Flow', () => {
  test('user can register, login, and add a book', async ({ page }) => {
    // Navigate to login page
    await page.goto('http://localhost:5173/login')
    
    // Register new user
    await page.click('text=Create one')
    await page.getByLabel('Username').fill('testuser')
    await page.getByLabel('Email').fill('test@example.com')
    await page.getByLabel('Password').fill('O1234567!')
    await page.getByLabel('Confirm Password').fill('O1234567!')
    await page.getByRole('button', { name: 'Create Account' }).click()
    
    // Should redirect to home
    await expect(page).toHaveURL('http://localhost:5173/')
    
    // Navigate to books
    await page.click('text=My Books')
    await expect(page).toHaveURL('http://localhost:5173/books')
    
    // Add a book
    await page.fill('input[placeholder*="Title"]', 'Test Book')
    await page.fill('input[placeholder*="Author"]', 'Test Author')
    await page.click('button:has-text("Add Book")')
    
    // Should see the book in the list
    await expect(page.locator('text=Test Book')).toBeVisible()
  })
  
  test('user can search for books', async ({ page }) => {
    await page.goto('http://localhost:5173/login')
    
    // Login (assuming user exists)
    await page.getByLabel('Username or Email').fill('testuser')
    await page.getByLabel('Password').fill('O1234567!')
    await page.getByRole('button', { name: 'Login' }).click()
    
    // Navigate to books
    await page.click('text=My Books')
    
    // Search
    await page.fill('input[placeholder*="Start typing"]', 'test')
    await page.waitForTimeout(500) // Wait for search
    
    // Should see search results
    await expect(page.locator('.card')).toBeVisible()
  })
})

