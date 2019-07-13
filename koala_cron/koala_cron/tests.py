from time import sleep
from functools import partial
from sys import argv

from koala_cron.monitor import build_job


class CustomError1(BaseException):
    pass


class CustomError2(BaseException):
    pass


decorator = partial(build_job,
                    job_name="hello",
                    endpoint="https://hooks.slack.com/services/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",
                    notify_on_failure_only=False)


@decorator
def passing_job():
    pass


def failing_job():
    return 1 / "str"


def custom_error1_job():
    raise CustomError1


def custom_error2_job():
    raise CustomError2


if __name__ == "__main__":
    passing_job()
