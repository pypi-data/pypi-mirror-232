import json
import logging
from datetime import datetime, timedelta, date, time
from enum import Enum
from typing import List, NamedTuple, Optional, Any, Dict, Tuple

import requests
from requests import Response
from requests.adapters import HTTPAdapter
from retry import retry
from urllib3 import Retry

import auth
from auth import TLSAdapter


def sleep_until(target):
    import time

    now = datetime.now()
    delta = target - now
    if delta > timedelta():
        time.sleep(delta.total_seconds())
        return True
    else:
        return False


class Facility(NamedTuple):
    id: int
    name: str
    location: str

    # noinspection PyPep8Naming
    @staticmethod
    def from_dict(facilityID: int, facilityName: str, location: str):
        return Facility(facilityID, facilityName, location)


class Timeslot(NamedTuple):
    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    status: str = "Available"

    def __str__(self) -> str:
        return f"{self.__repr__()} ({self.status})"

    def __repr__(self) -> str:
        return f"{self.start_time_str()}-{self.end_time_str()}"

    def date_str(self):
        return self.date.strftime("%Y-%m-%d")

    def start_time_str(self):
        return self.start_time.strftime("%H:%M")

    def end_time_str(self):
        return self.end_time.strftime("%H:%M")


class BookingResult(NamedTuple):
    ust_id: str
    facility_id: int
    timeslot_date: str
    start_time: str
    end_time: str
    booking_ref: int


class BookingResultType(Enum):
    RESERVED = "Booking reserved by another user"
    SAME_TIMESLOT_SAME_FACILITY_BOOKED = "You have already booked this facility in this timeslot"
    SAME_TIMESLOT_ANOTHER_FACILITY_BOOKED = "You have already booked another facility in this timeslot"
    SAME_DAY_SAME_FACILITY_TYPE_BOOKED = "You have already booked one timeslot on the same day for the same facility type"
    ADVANCE_BOOKING = "You can only book the facility 7 days in advance"
    UNKNOWN = "The Unknown Reason"


class BookedByAnotherUserError(Exception):
    pass


class SameTimeslotSameFacilityBookedError(Exception):
    pass


class BookedAnotherFacilityByUserError(Exception):
    pass


class BookedSameFacilityTypeError(Exception):
    pass


class BookingInAdvanceError(Exception):
    pass


class FbsError(Exception):
    def __init__(self, reason: Any) -> None:
        self.reason = reason
        super().__init__(reason)


def parse_booking_response(resp: Response) -> Dict:
    resp.raise_for_status()
    resp_obj = resp.json()
    logging.debug(f'{json.dumps(resp_obj, indent=4)}')
    if resp_obj["status"] == "200":
        return resp_obj
    else:
        result_type = next(filter(lambda x: x.value in resp_obj["message"], BookingResultType), BookingResultType.UNKNOWN)
        match result_type:
            case BookingResultType.RESERVED:
                raise BookedByAnotherUserError()
            case BookingResultType.SAME_TIMESLOT_SAME_FACILITY_BOOKED:
                raise SameTimeslotSameFacilityBookedError()
            case BookingResultType.SAME_TIMESLOT_ANOTHER_FACILITY_BOOKED:
                raise BookedAnotherFacilityByUserError()
            case BookingResultType.SAME_DAY_SAME_FACILITY_TYPE_BOOKED:
                raise BookedSameFacilityTypeError()
            case BookingResultType.ADVANCE_BOOKING:
                raise BookingInAdvanceError()
            case _:
                raise FbsError(f"({resp_obj['status']}) {resp_obj['message']}")


def parse_fbs_response(resp: Response) -> Any:
    resp.raise_for_status()
    resp_obj = resp.json()
    if resp_obj["status"] != "200":
        raise FbsError(resp_obj)
    return resp_obj


class Client:
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, token: Optional[str] = None) -> None:
        self.client, self.token_str = self.create_client(username, password, token)

    @staticmethod
    def create_client(username: Optional[str], password: Optional[str], token: Optional[str]) -> Tuple[requests.Session, str]:
        if username is not None and password is not None:
            logging.info(f"Logging in using credentials of {username}...")
            tokens = auth.auth((username, password))
        elif token is not None:
            logging.info("Logging in using token...")
            tokens = json.loads(token)
        else:
            logging.info("Logging in manually...")
            tokens = auth.auth()

        access_token, id_token, student_id = tokens

        client = requests.session()

        retries = Retry(
            total=15,
            allowed_methods=None,
            status_forcelist={x for x in range(400, 600)}
        )
        client.mount("http://", HTTPAdapter(max_retries=retries))
        client.mount("https://", TLSAdapter(max_retries=retries))

        del client.headers['Accept']
        client.headers['accept'] = 'application/json, text/plain, */*'
        client.headers['Accept-Encoding'] = 'gzip'
        client.headers['User-Agent'] = 'okhttp/4.9.2'

        client.headers["authorization"] = f"Bearer {id_token}"
        client.params = {"userType": "01", "ustID": student_id}

        logging.debug(f"Created a new FBS client {client.__dict__}.")
        logging.info("Logged in.")
        return client, json.dumps(tokens)

    def auto_book(self,
                  ids: List[str],
                  timeslot_date: str,
                  start_time: str,
                  end_time: str,
                  no_confirm: bool = False):
        ids = [int(x) for x in ids]
        timeslot_date = date.fromisoformat(timeslot_date)
        timeslot_start_time = time.fromisoformat(start_time)
        timeslot_end_time = time.fromisoformat(end_time)

        close_time = time.fromisoformat("00:00")
        open_time = time.fromisoformat("08:00")

        facilities_id_obj = {x.id: x for x in self.list_facilities()}

        confirmed = False
        if close_time <= datetime.now().time() < open_time:
            target_time = datetime.combine(datetime.now(), open_time)
            if not no_confirm and not confirmed:
                confirmed = True
                logging.info("The following facilities are going to be booked:")
                for facility_id in ids:
                    logging.info(f"\t")
                    logging.info(f"\tFacility ID: {facility_id}")
                    logging.info(f"\tFacility Location: {facilities_id_obj[facility_id].location}")
                    logging.info(f"\tFacility Name: {facilities_id_obj[facility_id].name}")
                    logging.info(f"\tTimeslot Date: {timeslot_date}")
                logging.info(f"\t")
                logging.info("Note that since the FBS is closed, the timeslots are not preview-able.")
                logging.info("Please confirm the booking. (y/N)")
                if input().lower() != "y":
                    logging.critical("The booking is cancelled.")
                    return
            logging.info(f"The FBS is closed. "
                         f"Waiting until {target_time.isoformat()}...")
            sleep_until(target_time)

        facilities_timeslots = {
            facility_id: self.list_facility_timeslots(
                facility_id,
                timeslot_date,
                timeslot_date,
                timeslot_start_time,
                timeslot_end_time
            )
            for facility_id in ids
        }

        if not no_confirm and not confirmed:
            logging.info("The following facilities and timeslots are going to be booked:")
            for facility_id, timeslots in facilities_timeslots.items():
                logging.info(f"\t")
                logging.info(f"\tFacility ID: {facility_id}")
                logging.info(f"\tFacility Location: {facilities_id_obj[facility_id].location}")
                logging.info(f"\tFacility Name: {facilities_id_obj[facility_id].name}")
                logging.info(f"\tTimeslot Date: {timeslot_date}")
                logging.info("\tTimeslot(s):")
                for timeslot in timeslots:
                    logging.info(f"\t\t{timeslot}")
            logging.info(f"\t")
            logging.info("Please confirm the booking. (y/N)")
            if input().lower() != "y":
                logging.critical("The booking is cancelled.")
                return

        available_time = datetime.combine(timeslot_date - timedelta(days=7), open_time)
        if close_time <= datetime.now().time() < open_time or datetime.now() < available_time:
            target_time = max(datetime.combine(datetime.now(), open_time), available_time)
            logging.info(f"The FBS is closed or the specified timeslot date has not become available yet. "
                         f"Waiting until {target_time.isoformat()}...")
            sleep_until(target_time)

        for facility_id in ids:
            for timeslot in facilities_timeslots[facility_id]:
                try:
                    self.book(facility_id, timeslot)
                    # Break if booked successfully.
                    # Because only one timeslot for one day and one facility is allowed.
                    break
                except FbsError as e:
                    match e.reason:
                        case FbsError.Reason.RESERVED:
                            logging.warning(f"The timeslot {timeslot} of the facility {facility_id} is reserved.")
                        case _:
                            logging.warning(f"Couldn't book the timeslot {timeslot} of the facility {facility_id}.",
                                            exc_info=True)

    @retry(exceptions=FbsError, tries=60, delay=1)
    def book(
            self,
            facility_id: int,
            timeslot: Timeslot
    ):
        logging.info(f"Booking the timeslot {timeslot} of the facility {facility_id}...")

        params = {
            "facilityID": str(facility_id),
            "timeslotDate": timeslot.date_str(),
            "startTime": timeslot.start_time_str(),
            "endTime": timeslot.end_time_str(),
            "cancelInd": "N",
        }

        resp = self.client.post("https://w5.ab.ust.hk/msapi/fbs/book", params=params)
        resp_obj = parse_booking_response(resp)
        result = resp_obj["bookingResult"][0]
        result = BookingResult(
            resp_obj["ustID"],
            result["facilityID"],
            result["timeslotDate"],
            result["startTime"],
            result["endTime"],
            result["bookingRef"],
        )
        logging.info(f"Booked the timeslot {timeslot} of the facility {facility_id}.")
        logging.info(f"Booking result: {result}")
        return result

    @retry(exceptions=FbsError, tries=60, delay=1)
    def list_facilities(self
                        ) -> List[Facility]:
        logging.info("Retrieving the facilities...")
        resp = self.client.get("https://w5.ab.ust.hk/msapi/fbs/facilities")
        facilities = [Facility.from_dict(**k) for k in parse_fbs_response(resp)["facility"]]
        logging.info(f"Retrieved {len(facilities)} facilities.")
        return facilities

    @retry(exceptions=FbsError, tries=60, delay=1)
    def list_facility_timeslots(self,
                                facility_id: int,
                                start_date: date,
                                end_date: date,
                                start_time: time = time.min,
                                end_time: time = time.max):
        logging.info(f"Retrieving the timeslots of the facility {facility_id}...")
        params = {
            "facilityID": str(facility_id),
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
        }
        try:
            resp = self.client.get("https://w5.ab.ust.hk/msapi/fbs/facilityTimeslot", params=params)
            resp_obj = parse_fbs_response(resp)
            timeslots = [
                Timeslot(
                    date.fromisoformat(k["timeslotDate"]),
                    time.fromisoformat(k["startTime"]),
                    time.fromisoformat(k["endTime"]),
                    k["timeslotStatus"],
                )
                for k in resp_obj["timeslot"]
            ]
            timeslots = [x for x in timeslots if start_time <= x.start_time and x.end_time <= end_time]
            logging.info(f"Retrieved the timeslots {timeslots} of the facility {facility_id}.")
            return timeslots
        except FbsError as e:
            if "Timeslot not found" in e.reason['message']:
                logging.info(f"No timeslot found for the facility {facility_id}.")
                return []
            else:
                raise e


def is_bookable(timeslot_date: datetime.date) -> bool:
    return datetime.now() >= bookable_time_of(timeslot_date)


def bookable_time_of(timeslot_date: datetime.date) -> datetime:
    return datetime.combine(timeslot_date - timedelta(days=7), time(hour=8))


def is_open() -> bool:
    return datetime.now() >= open_time()


def open_time() -> datetime:
    return datetime.combine(datetime.now().date(), time(hour=8))
