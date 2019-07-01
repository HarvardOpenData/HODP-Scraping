from typing import Callable
import requests
import json
import multiprocessing as mp


class MissingParamError(Exception):
    """Raised when an absent parameter prevents a job from being attached"""
    pass


class TimeoutError(Exception):
    """Raised when a job timeouts"""
    pass


class Monitor(object):
    def __init__(self,
                 endpoint: str = None):
        self.endpoint = endpoint

    def attach_job(self,
                   func: Callable,
                   job_name: str,
                   endpoint: str = None,
                   message_key: str = "text",
                   initiate_message: str = None,
                   success_message: str = None,
                   failure_message: str = None,
                   notify_on_failure_only: bool = True,
                   errors=(BaseException),
                   timeout: int = None,
                   *args,
                   **kwargs):
        """
          Attaches a handler to the job initiated by func.

          @ param func: a function executing some task; aka the starting point for your cron job

          @ param job_name: the name by which the process will be referred to default messages

          @ param endpoint: (default = None) the endpoint that will be posted to. If Monitor was initialized with an endpoint, ignore

          @ param message_key: (default = "text") the key corresponding to the message in the payload

          @ param initiate_message: (default = None) the message to send when initiating a job

          @ param success_message: (default = None) the message to send when a job successfully completes

          @ param failure_message: (default = None) the message to send when a job fails

          @ param notify_on_failure_only: (default = True) a payload will only be emitted on meeting a failure condition

          @ param errors: (default = BaseException) a tuple of exceptions to catch on while func is executed.

          @ param timeout: (default = None) sets the number of seconds after executing func after which a failure will be emitted.

          Returns a function that is used to execute/monitor func.
        """
        if endpoint is None:
            if self.endpoint is None:
                raise MissingParamError(
                    f"Endpoint not defined when attempting to attach {job_name}")
            elif type(self.endpoint) is str:
                endpoint = self.endpoint
            else:
                raise TypeError(
                    f"Endpoint for {job_name} is not of type string.")

        def handler():
            if not notify_on_failure_only:
                requests.post(
                    url=endpoint,
                    json={
                        message_key: f"initiated {job_name}" if initiate_message is None else initiate_message}
                )
            try:
                if timeout:
                    p = mp.Process(
                        target=func, args=args, kwargs=kwargs)
                    p.start()
                    p.join(timeout)

                    if p.is_alive():
                        p.terminate()
                        p.join()
                        raise TimeoutError(
                            f"{job_name} timed out after {timeout} seconds")
                else:
                    func(*args, **kwargs)

                if not notify_on_failure_only:
                    requests.post(
                        url=endpoint,
                        json={
                            message_key: f"{job_name} successfully completed!" if success_message is None else success_message}
                    )
            except errors as e:
                requests.post(
                    url=endpoint,
                    json={
                        "text": f"{job_name} failed with the following error message:\n {str(e)}" if failure_message is None else failure_message}
                )
        return handler
