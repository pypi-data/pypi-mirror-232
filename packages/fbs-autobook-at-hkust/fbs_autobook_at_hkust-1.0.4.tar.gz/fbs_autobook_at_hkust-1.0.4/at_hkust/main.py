from pathlib import Path

import streamlit.web.cli as stcli


def main():
    # noinspection PyTypeChecker
    stcli.main_run([str(Path(__file__).parent / 'ui.py')])


if __name__ == '__main__':
    main()
