# Test Automation with VS Code and Copilot

This repo demonstrates usijng VS Code and Copilot to generate automated test cases with frameworks like Playwright, Selenium

Steps:

1. Configure VS Code with MCP servers as in mcp_configurations.json 

2. Go to respective folders e.g. playwright (for selenium do similar with files inside corresponding folder)

- Add the file 'generate_playwright.txt' to context
- Use Prompt as described in Notes.txt

Once the initial test case is generated, iterate and extend incrementally with further prompts

To run the test cases: follow standard commands as per framework used e.g.
    - For Playwright, use command: npm run test:ui  (for UI mode, also can run in headless mode)

