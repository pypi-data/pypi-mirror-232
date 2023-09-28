from cwrap import BaseCEnum


class JobSubmitStatusType(BaseCEnum):  # type: ignore
    TYPE_NAME = "job_submit_status_type_enum"
    SUBMIT_OK = None
    SUBMIT_JOB_FAIL = None
    SUBMIT_DRIVER_FAIL = None
    SUBMIT_QUEUE_CLOSED = None

    @classmethod
    def from_string(cls, name: str) -> "JobSubmitStatusType":
        return super().from_string(name)  # type: ignore


JobSubmitStatusType.addEnum("SUBMIT_OK", 0)
JobSubmitStatusType.addEnum("SUBMIT_JOB_FAIL", 1)
JobSubmitStatusType.addEnum("SUBMIT_DRIVER_FAIL", 2)
JobSubmitStatusType.addEnum("SUBMIT_QUEUE_CLOSED", 3)
