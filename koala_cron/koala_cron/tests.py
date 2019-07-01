from time import sleep
from sys import argv

from monitor import Monitor


class CustomError1(BaseException):
    pass


class CustomError2(BaseException):
    pass


def passing_job():
    pass


def failing_job():
    return 1 / "str"


def custom_error1_job():
    raise CustomError1


def custom_error2_job():
    raise CustomError2


def timeout_job():
    sleep(10)


mn = Monitor(
    argv[1])


def test_success():
    (mn.attach_job(func=passing_job, job_name="example job", notify_on_failure_only=False))()
    return True


def test_failure():
    (mn.attach_job(func=failing_job, job_name="failing job", notify_on_failure_only=False))()


def test_custom_errors(errors):
    (mn.attach_job(func=custom_error1_job, job_name="custom_error1_job",
                   errors=errors, notify_on_failure_only=False))()
    (mn.attach_job(func=custom_error2_job, job_name="custom_error2_job",
                   errors=errors, notify_on_failure_only=False))()


def test_timeout(timeout):
    (mn.attach_job(func=timeout_job, job_name="timeout job",
                   timeout=timeout, notify_on_failure_only=False))()


if __name__ == "__main__":
    (test_success())
    (test_failure())
    (test_custom_errors((CustomError1, CustomError2)))
    (test_timeout(2))
