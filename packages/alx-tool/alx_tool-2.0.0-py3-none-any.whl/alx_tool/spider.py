import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.crawler import CrawlerProcess


class AlxSpider(scrapy.Spider):
    name = "alx"
    allowed_domains = ["intranet.alxswe.com"]
    handle_httpstatus_list = [404, 410, 301, 500]

    def __init__(self, user_login_email, user_login_password, url_to_project, return_data_callback):
        self.user_login_email = user_login_email
        self.user_login_password = user_login_password
        self.url_to_project = url_to_project
        self.return_data_callback = return_data_callback

    def start_requests(self):
        yield scrapy.Request(self.url_to_project, callback=self.check_login, dont_filter=True)
    
    def check_login(self, response):
        if "sign_in" in response.url:
            yield scrapy.FormRequest.from_response(
                response,
                formdata = {
                    "authenticity_token": response.css("form input[name=authenticity_token]::attr(value)").extract_first(),
                    "user[email]": self.user_login_email,
                    "user[password]": self.user_login_password
                },
                callback=self.parse,
            )

        else:
            self.logger.info("Already logged in.")
            yield self.parse(response)

    def parse(self, response):
        alert: str = response.css(".alert.alert-danger::text").get()

        if alert is not None:
            msg = "Login failed. please check your email and password and try again."
            raise CloseSpider(msg)
        
        if response.status in [404, 410, 301, 500]:
            msg = "The provided URL is incorrect or does not lead to the project page. Please check the URL and try again."
            raise CloseSpider(msg)

        tasks = response.css("div[id^=task-num-]")

        data = {
            "url": response.url,
            "title": response.css("h1.gap::text").get(),
            "no_of_tasks": len(tasks),
            "tasks": [
                {
                    "no": index,
                    "title": task.css(".panel-title::text").extract_first().strip(),
                    "type": task.css(".label-info::text").extract_first().strip(),
                    "body": task.css(".panel-body > .task_progress_score_bar ~ *").extract() if task.css(".panel-body > .task_progress_score_bar ~ *").extract() != [] else task.css(".panel-body > #user_id ~ *").extract(),
                    "github_repository": task.css(".list-group-item > ul > li:contains('GitHub repository:') code::text").get(),
                    "directory": task.css(".list-group-item > ul > li:contains('Directory:') code::text").get(),
                    "files": task.css(".list-group-item > ul > li:contains('File:') code::text").extract_first().split(", ") if task.css(".list-group-item > ul > li:contains('File:') code::text").get() is not None else [],
                    "prototypes": task.css(".panel-body ul li:contains('Prototype:') code::text").extract(),
                }
                for index, task in enumerate(tasks)
            ]
        }

        self.return_data_callback(data)

def run_spider(user_login_email, user_login_password, url_to_project) -> list:
    results = []

    def return_data_callback(data):
        results.append(data)

    process = CrawlerProcess(
        settings={
            "LOG_ENABLED": False,
        },
    )

    process.crawl(
        crawler_or_spidercls=AlxSpider,
        user_login_email=user_login_email,
        user_login_password=user_login_password,
        url_to_project=url_to_project,
        return_data_callback=return_data_callback,
    )
    
    try:
        process.start()
    except CloseSpider as error:
        raise SystemExit(error)
    
    results_dict = results[0]

    return results_dict
