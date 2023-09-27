from kdb import report
from kdb.webdriver import kdb_driver


def test_browser_nav():
    # start browser
    report.add_comment("Test browser navigation")
    # start browser
    kdb_driver.start_browser()
    # load page for test.
    kdb_driver.open_url('https://demoqa.com/text-box')
    kdb_driver.screen_shot()

    # click a left menu "Điện Gia Dụng"
    # href="https://tiki.vn/dien-gia-dung/c1882"
    kdb_driver.click("xpath=//a[@href='https://tiki.vn/dien-gia-dung/c1882']")
    kdb_driver.verify_text_on_page("Back to products")
    #  //a[@data-view-index='1']/span[@title='Điện Gia Dụng']
    kdb_driver.screen_shot()
    kdb_driver.back()
    kdb_driver.verify_url_contains("https://www.saucedemo.com/inventory.html")
    kdb_driver.screen_shot()
    kdb_driver.forward()
    kdb_driver.verify_text_on_page("Back to products")
    kdb_driver.screen_shot()


    kdb_driver.close_browser()
