import time as t
import warnings
from datetime import datetime, timedelta, time

import pandas as pd
import streamlit as st
from streamlit_extras.grid import grid

import fbs
from setup import prepare_logger

warnings.filterwarnings("ignore")


def get_facilities():
    return pd.DataFrame(state.client.list_facilities())


def get_timeslots(facility_id):
    start_date = state.timeslot_date
    end_date = state.timeslot_date
    start_time = state.timeslot_time_range[0]
    end_time = state.timeslot_time_range[1]
    return state.client.list_facility_timeslots(
        facility_id,
        start_date,
        end_date,
        start_time,
        end_time,
    )


state = st.session_state


def def_state(name, default_value):
    if name not in state:
        state[name] = default_value
    return state[name]


if def_state('logger', True):
    prepare_logger()
    state['logger'] = False

def_state('client', None)
def_state('current_page', 0)
def_state('facilities', pd.DataFrame())

def_state('facility_timeslots', {})
def_state('timeslot_date', (datetime.now() + timedelta(days=8)).date())
def_state('timeslot_time_range', (time(hour=7), time(hour=23)))

st.set_page_config(
    page_title="FBS AutoBook @ HKUST",
    page_icon="🤖",
)
st.markdown("""<style>
    footer:after {
        content: '. Via the Poet @ HKUST';
        visibility: visible;
    }
</style>""", unsafe_allow_html=True)

PAGES = [
    "Welcome Page",
    "Choose Timeslots",
    "Review and Confirm",
    "Book"
]

if state.current_page > 0 and state.current_page != len(PAGES) - 1:
    st.caption("Navigate to Previous Page(s)... ")
    navigator = grid(len(PAGES))
    for i, page in enumerate(PAGES[:state.current_page]):
        if navigator.button(page, type='primary', use_container_width=True):
            state.current_page = i
            st.rerun()

placeholder = st.empty()


def render_welcome():
    st.markdown("# Welcome to <br>"
                "FBS AutoBook @ HKUST", unsafe_allow_html=True)
    st.error("**Disclaimer:** The use of *FBS AutoBook @ HKUST* **contradicts** the university's requirement for human input in facility bookings. "
             "This application is an **unofficial** tool and does **not** receive support from HKUST. "
             "By choosing to use this app, keep in mind that as you venture forth with care, consequences may lie in wait. "
             "You accept the potential **risks** and **responsibility** for any outcomes that may follow. "
             "Exercise caution, and use this app only after considering the possible repercussions and deeming them acceptable.")
    st.write("This app streamlines facility reservation through the *HKUST Facility Booking System* by automatically booking the facilities you select once they become available. "
             "To have your browser remember your login credentials, enter them below. "
             "Alternatively, you can skip this step and input your information directly on the official login page.")
    st.info("The app does **not** store your credentials. Your browser will be responsible for saving this information.")

    with st.form("login"):
        username = st.text_input("ITSC Username (without @connect.ust.hk)", autocomplete='username')
        password = st.text_input("ITSC Password", type="password", autocomplete='current-password')
        if st.form_submit_button("Login"):
            state.client = fbs.Client(username, password)
            state.current_page += 1
            st.rerun()

    with st.form('login_by_token'):
        token = st.text_input("Login Token", state.client.token_str if state.client is not None else "")
        if st.form_submit_button("Login by Token"):
            state.client = fbs.Client(token=token)
            state.current_page += 1
            st.rerun()


def render_choose():
    st.title("Choose Facilities, Timeslot Date & Time Range")

    st.success("Congratulations on a successful login. "
               "Your token is displayed below, which you can use for future logins. "
               "Do **not** share it with others, as it grants access to your account and the ability to reserve facilities on your behalf.")
    st.code(state.client.token_str, language='json')

    with st.form('filter'):
        timeslot_date = st.date_input(
            "Timeslot Date",
            value=state.timeslot_date
        )

        timeslot_time_range = st.slider(
            "Timeslot Time Range",
            value=state.timeslot_time_range,
            min_value=time(hour=7),
            max_value=time(hour=23),
            step=timedelta(hours=1),
        )

        next_page = st.form_submit_button("Next")

        state.facilities = get_facilities()
        state.facilities = state.facilities.set_index("id")
        state.facilities = state.facilities.sort_values(by=['id'])
        state.facilities["book"] = False
        facilities = st.data_editor(
            state.facilities,
            column_order=(
                'id',
                'location',
                'name',
                'book',
            ),
            column_config={
                'id': st.column_config.Column("ID"),
                'location': st.column_config.Column("Location"),
                'name': st.column_config.Column("Name"),
                'book': st.column_config.Column("Book"),
            },
            height=(len(state.facilities) + 1) * 35 + 2,
            use_container_width=True,
        )

        if next_page:
            state.facilities = facilities
            state.timeslot_date = timeslot_date
            state.timeslot_time_range = timeslot_time_range
            state.current_page += 1
            st.rerun()


def render_review():
    st.title("Review and Confirm")
    st.write("Take a moment to review your selected facilities. ")
    st.write("Upon confirmation, the system will automatically reserve all selected facilities for you.")
    st.write("Please note that the system will attempt to reserve all selected facilities nearly simultaneously. "
             "However, the Facility Booking System only allows **one user to book one facility in the same timeslot**, "
             "and **one user to book the same type of facility in the same day**.")

    facilities = state.facilities[state.facilities["book"]]
    for facility_id, facility_data in facilities.iterrows():
        facility_location = facility_data['location']
        facility_name = facility_data['name']

        st.subheader(f"({facility_id}) {facility_location}/{facility_name}")
        if time.fromisoformat("00:00") <= datetime.now().time() < time.fromisoformat("08:00"):
            st.warning("FBS system is closed between 00:00 and 08:00, so the timeslot preview is unavailable. ", icon="⚠️")
            st.write(f"**Timeslot Date**: "
                     f"{str(state.timeslot_date)}")
            st.write(f"**Timeslot Time Range**: "
                     f"{state.timeslot_time_range[0].isoformat('minutes')}-{state.timeslot_time_range[1].isoformat('minutes')}")
        else:
            with st.spinner("Loading timeslots... "):
                state.facility_timeslots[facility_id] = get_timeslots(facility_id)
                timeslot_data = pd.DataFrame(state.facility_timeslots[facility_id], columns=list(fbs.Timeslot._fields))
                timeslot_data = timeslot_data.drop(columns=['start_time', 'end_time'])
                timeslot_data['time_range'] = [str(x) for x in state.facility_timeslots[facility_id]]
                st.dataframe(
                    timeslot_data.style.apply(lambda row: ['background-color: lightgray' if row['status'] != 'Available' else '' for _ in row], axis=1),
                    column_config={
                        'date': st.column_config.Column("Date"),
                        'status': st.column_config.Column("Status"),
                        'time_range': st.column_config.Column("Time Range")
                    },
                    height=(len(timeslot_data) + 1) * 35 + 2,
                    use_container_width=True,
                    hide_index=True,
                )

    if st.button("Confirm"):
        state.require_refresh = True
        state.current_page += 1
        st.rerun()


def render_book():
    if state.require_refresh:
        state.require_refresh = False
        placeholder.empty()
        st.rerun()

    st.title("Book")

    timeslot_date = state.timeslot_date
    if not fbs.is_open() or not fbs.is_bookable(timeslot_date):
        begin, end = datetime.now(), max(fbs.open_time(), fbs.bookable_time_of(timeslot_date))
        remaining = timedelta(seconds=(end - datetime.now()).seconds)
        progress_text = (f"Waiting until **the selected timeslots become bookable** or **FBS reopens** ({end.isoformat()})...  "
                         f"**Remaining**: {remaining}")
        progress = st.progress(0, text=progress_text)
        while datetime.now() < end:
            remaining = timedelta(seconds=(end - datetime.now()).seconds)
            percentage = 1 - (end - datetime.now()) / (end - begin)
            progress_text = (f"Waiting until **the selected timeslots become bookable** or **FBS reopens** ({end.isoformat()})...  "
                             f"**Remaining**: {remaining}")
            progress.progress(percentage, text=progress_text)
            t.sleep(.1)

    booked_count = 0
    with st.status("Booking... ", expanded=True) as status:
        for facility_id, facility_data in state.facilities[state.facilities["book"]].iterrows():
            if facility_id in state.facility_timeslots:
                timeslots = state.facility_timeslots[facility_id]
            else:
                timeslots = get_timeslots(facility_id)
            for timeslot in timeslots:
                name = facility_data['name']
                location = facility_data['location']
                try:
                    status.update(label=f"Booking **({facility_id}) {location}/{name}** at **{timeslot}**... ")
                    state.client.book(facility_id, timeslot)
                    st.success(f"Successfully booked **({facility_id}) {location}/{name}** at **{timeslot}**! ")
                    booked_count += 1
                except fbs.BookedByAnotherUserError:
                    st.warning(f"**({facility_id}) {location}/{name}** at **{timeslot}** cannot be booked.  \n"
                               f"Because it has been booked by someone else. ", icon="⚠️")
                    continue
                except fbs.SameTimeslotSameFacilityBookedError:
                    st.warning(f"**({facility_id}) {location}/{name}** at **{timeslot}** cannot be booked.  \n"
                               f"Because you have booked this facility in the same timeslot. ", icon="⚠️")
                    continue
                except fbs.BookedAnotherFacilityByUserError:
                    st.warning(f"**({facility_id}) {location}/{name}** at **{timeslot}** cannot be booked.  \n"
                               f"Because you have booked another facility in the same timeslot. ", icon="⚠️")
                    break
                except fbs.BookedSameFacilityTypeError:
                    st.warning(f"**({facility_id}) {location}/{name}** at **{timeslot}** cannot be booked.  \n"
                               f"Because you have booked facility on the same day for the same facility type. ", icon="⚠️")
                    break
                except fbs.BookingInAdvanceError:
                    st.warning(f"**({facility_id}) {location}/{name}** at **{timeslot}** cannot be booked.  \n"
                               f"Because you can only book the facility 7 days in advance. ", icon="⚠️")
                    break
                except fbs.FbsError as e:
                    st.error(f"**({facility_id}) {location}/{name}** at **{timeslot}** cannot be booked.  \n"
                             f"Reason: {e} ")
        status.update(label=f"Completed. Successfully booked **{booked_count}** timeslots of facilities in total. ", state='complete')


match state['current_page']:
    case 0:
        render_welcome()
    case 1:
        render_choose()
    case 2:
        with placeholder.container():
            render_review()
    case 3:
        render_book()
