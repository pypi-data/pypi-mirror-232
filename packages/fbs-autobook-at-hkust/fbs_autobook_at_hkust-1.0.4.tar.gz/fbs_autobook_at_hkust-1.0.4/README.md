# FBS AutoBook @ HKUST

FBS AutoBook @ HKUST is a Python & Streamlit app that automates booking facilities through the HKUST Facility Booking
System (FBS).

## Prerequisites

- Python <br>
  *I use Python 3.11 for development, but I guess Python 3.10 / 3.9 should work fine too.*
- Chrome Browser <br>
  *For automate logging in to FBS (since there are some restrictions on the login process). I use Chrome 116.0, and I
  think any Chrome version should work.*

## Usage

Install the package through pip:

```commandline
pip install fbs-autobook-at-hkust
```

After successful installation, run the app with the following command:

```commandline
fbs-autobook-at-hkust
```

You shall see your browser window open with the app running.

## Overview

The app has the following pages:

### Welcome Page

Users can login with their ITSC credentials or a saved token. A disclaimer highlights that use of the app is at the
user's own risk and may contradict HKUST's booking requirements.

### Choose Facilities, Timeslot Date & Time Range

Users select which facilities to book, along with the desired booking date and time range. The app retrieves all
available timeslots matching the criteria for future booking attempts.

### Review and Confirm

A summary of the selected facilities and timeslots is shown for the user to review and confirm before proceeding. If FBS
is open, the app shows the actual available timeslots. Otherwise, it displays the user-specified date and time range.

### Book

The app automatically attempts to book the selected timeslots when they become available. Unavailability is often due to
FBS closure or the 7-day advance booking limit. The result of each booking attempt is displayed as a success or failure
message.

## Features

- Automated booking of multiple facilities when timeslots open up
- Login with ITSC credentials / token
- Custom selection of facilities, timeslot date and timeslot time range
- Review & Confirm the facilities before booking
- Status updates during booking process
- Messages on successful / fail bookings with reasons

## Tech Stack

- Python
- Streamlit for app UI

## Disclaimer

This app contradicts HKUST's requirement for manual booking. Use at your own risk! The developer is not responsible for
any consequences.