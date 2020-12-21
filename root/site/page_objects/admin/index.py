from root.site.page_objects import BaseAdminPage


class AdminMainPage(BaseAdminPage):
    page_locator = "//div[@id='index']"
