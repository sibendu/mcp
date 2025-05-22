import org.junit.jupiter.api.*;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import java.io.File;
import org.apache.commons.io.FileUtils;
//import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
//import io.github.bonigarcia.wdm.WebDriverManager;

import java.time.Duration;
import java.io.IOException;

public class YopmailTest {
    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeEach
    public void setUp() {
        //WebDriverManager.chromedriver().setup();
        //ChromeOptions options = new ChromeOptions();
        //options.addArguments("--remote-allow-origins=*");
        driver = new ChromeDriver(); //options
        wait = new WebDriverWait(driver, Duration.ofSeconds(20));
        driver.manage().window().maximize();
    }    
    
    @Test
    public void testYopmailEmailAccess() throws IOException {
        // Navigate to Yopmail
        driver.get("https://yopmail.com/wm");

        // Enter email address
        WebElement loginInput = wait.until(ExpectedConditions.presenceOfElementLocated(By.id("login")));
        loginInput.sendKeys("sibendu@yopmail.com");

        // Click the check inbox button
        WebElement checkButton = wait.until(ExpectedConditions.elementToBeClickable(
            By.cssSelector(".material-icons-outlined.f36")));
        checkButton.click();

        // Switch to inbox iframe and wait for it to load
        wait.until(ExpectedConditions.frameToBeAvailableAndSwitchToIt("ifinbox"));

        // Wait for and click the first email
        WebElement firstEmail = wait.until(ExpectedConditions.elementToBeClickable(
            By.cssSelector(".m")));
        firstEmail.click();

        // Switch back to default content
        driver.switchTo().defaultContent();        // Switch to email content iframe and verify it's loaded
        wait.until(ExpectedConditions.frameToBeAvailableAndSwitchToIt("ifmail"));
        WebElement mailContent = wait.until(ExpectedConditions.presenceOfElementLocated(By.id("mail")));
          // Verify email heading contains 'Password reset'
        WebElement emailHeading = wait.until(ExpectedConditions.presenceOfElementLocated(By.xpath("//*[contains(text(),'This is a test message')]")));
        Assertions.assertTrue(emailHeading.isDisplayed(), "Email heading with 'Password reset' should be visible");
        
        // Take screenshot of the email content
        File emailScreenshot = ((TakesScreenshot) driver).getScreenshotAs(OutputType.FILE);
        FileUtils.copyFile(emailScreenshot, new File("test-result-screenshots/email-screenshot.png"));

    }

    @AfterEach
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}
