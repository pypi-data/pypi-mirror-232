import subprocess
import sys
from datetime import datetime

import kthread
import what_os
from ansi.colour.rgb import rgb256
from ansi.colour import bg, fx
from touchtouch import touch
from kthread_sleep import sleep
from threading import Lock

lock = Lock()

strblackbg = str(bg.black)
resetstr = str(fx.reset)
backslash = "\\"
allthreads = []
allsubprocs = []

colors_with_black_bg = [
    (255, 255, 255),  # White
    (255, 0, 0),  # Red
    (0, 255, 0),  # Green
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
    (192, 255, 192),  # Light Green (3)
    (192, 192, 255),  # Light Blue (3)
    (255, 192, 255),  # Light Magenta (3)
    (192, 255, 255),  # Light Cyan (3)
    (255, 255, 192),  # Light Yellow (3)
    (255, 192, 128),  # Light Orange
    (255, 128, 255),  # Light Pink
    (128, 255, 192),  # Light Turquoise
    (192, 128, 255),  # Lavender
    (255, 255, 128),  # Light Lime
    (128, 192, 255),  # Baby Blue
    (192, 255, 128),  # Light Lime (2)
    (128, 255, 255),  # Light Aqua (2)
    (255, 128, 192),  # Light Rose
    (0, 128, 0),  # Green (dark)
    (0, 0, 128),  # Navy
    (128, 128, 0),  # Olive
    (128, 0, 128),  # Purple
    (0, 128, 128),  # Teal
    (192, 192, 192),  # Light Gray
    (128, 128, 128),  # Medium Gray
    (64, 64, 64),  # Dark Gray
    (255, 128, 0),  # Orange
    (0, 255, 128),  # Turquoise
    (128, 0, 255),  # Violet
    (255, 128, 128),  # Salmon
    (128, 255, 0),  # Lime
    (0, 128, 255),  # Sky Blue
    (255, 0, 128),  # Fuchsia
    (128, 255, 128),  # Light Green
    (128, 128, 255),  # Light Blue
    (255, 128, 255),  # Light Magenta
    (128, 255, 255),  # Light Cyan
    (255, 255, 128),  # Pale Yellow
    (192, 128, 0),  # Brown
    (128, 192, 0),  # Chartreuse
    (192, 0, 128),  # Indigo
    (0, 192, 128),  # Sea Green
    (128, 0, 192),  # Plum
    (192, 128, 128),  # Rosy Brown
    (128, 192, 128),  # Pale Green
    (128, 128, 192),  # Light Periwinkle
    (192, 128, 192),  # Orchid
    (192, 192, 128),  # Khaki
    (255, 128, 192),  # Pink
    (192, 255, 128),  # Lime Green
    (128, 192, 255),  # Light Sky Blue
    (255, 128, 255),  # Light Fuchsia
    (192, 255, 255),  # Light Aqua
    (255, 255, 192),  # Pale Lemon
    (128, 64, 0),  # Dark Orange
    (0, 128, 64),  # Dark Turquoise
    (64, 0, 128),  # Dark Violet
    (128, 64, 64),  # Dark Salmon
    (64, 128, 0),  # Dark Lime
    (0, 64, 128),  # Dark Sky Blue
    (128, 0, 64),  # Dark Fuchsia
    (64, 128, 64),  # Dark Sea Green
    (64, 64, 128),  # Dark Periwinkle
    (128, 64, 128),  # Dark Orchid
    (128, 128, 64),  # Dark Khaki
    (128, 0, 192),  # Dark Pink
    (192, 0, 64),  # Dark Indigo
    (0, 192, 64),  # Dark Sea Green (2)
    (64, 0, 192),  # Dark Plum
    (192, 64, 64),  # Dark Rosy Brown
    (64, 192, 64),  # Dark Pale Green
    (64, 64, 192),  # Dark Light Periwinkle
    (192, 64, 192),  # Dark Orchid (2)
    (192, 192, 64),  # Dark Khaki (2)
    (255, 64, 0),  # Darker Orange
    (0, 255, 64),  # Darker Turquoise
    (64, 0, 255),  # Darker Violet
    (255, 64, 64),  # Darker Salmon
    (64, 255, 0),  # Darker Lime
    (0, 64, 255),  # Darker Sky Blue
    (255, 0, 64),  # Darker Fuchsia
    (64, 255, 64),  # Darker Sea Green
    (64, 64, 255),  # Darker Periwinkle
    (255, 64, 255),  # Darker Orchid
    (64, 255, 255),  # Darker Light Blue
    (255, 255, 64),  # Darker Yellow
    (192, 192, 192),  # Light Gray (2)
    (255, 192, 0),  # Gold
    (0, 255, 192),  # Aquamarine
    (192, 0, 255),  # Hot Pink
    (192, 255, 0),  # Chartreuse (2)
    (0, 192, 255),  # Light Sky Blue (2)
    (255, 0, 192),  # Medium Orchid
    (255, 192, 192),  # Light Salmon
    (192, 255, 192),  # Light Green (2)
    (192, 192, 255),  # Light Blue (2)
    (255, 192, 255),  # Light Magenta (2)
    (192, 255, 255),  # Light Cyan (2)
    (255, 255, 192),  # Light Yellow (2)
    (255, 192, 64),  # Peach
    (192, 255, 64),  # Yellow-Green
    (192, 64, 255),  # Blue-Violet
    (64, 192, 255),  # Powder Blue
    (255, 64, 192),  # Raspberry
]


def kill_subproc(ffmprocproc: subprocess.Popen) -> None:
    try:
        # let's try to terminate it gracefully
        try:
            ffmprocproc.stdout.close()
        except Exception:
            pass
        try:
            ffmprocproc.stdin.close()
        except Exception:
            pass
        try:
            ffmprocproc.stderr.close()
        except Exception:
            pass
        try:
            ffmprocproc.wait(timeout=0.0001)
        except Exception:
            pass
        try:
            ffmprocproc.terminate()
        except Exception:
            pass
    except Exception:
        pass


def _start_logcat(
    ini,
    color,
    color2,
    color3,
    color4,
    device_serial,
    print_stdout=True,
    clear_log=True,
    ljustserial=20,
):
    device_serialcolor = (
        strblackbg + color3 + device_serial.ljust(ljustserial) + resetstr
    )
    colorsep = strblackbg + color4 + "█" + resetstr
    if clear_log:
        subprocess.run(
            f"{path_adb} -s {device_serial} logcat -c",
            capture_output=True,
        )
    p = subprocess.Popen(
        f"{path_adb} -s {device_serial} logcat",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    allsubprocs.append(p)
    for line in iter(p.stdout.readline, b""):
        try:
            l = line.decode("utf-8").strip()
            if not l:
                continue
            a, b = l.split(": ", maxsplit=1)
            aa = a.split(maxsplit=5)
            while len(aa) < 6:
                aa.append("")
            aa = [x1.strip() for x1 in aa]
            try:
                lock.acquire()
                f.write(
                    f""""{device_serial}","{aa[0]}","{aa[1]}","{aa[2]}","{aa[3]}","{aa[4]}","{aa[5]}","{b.replace('"', f'{backslash}"')}"\n"""
                )
            finally:
                lock.release()
            aacolor = colorsep.join(
                [
                    strblackbg
                    + color
                    + (
                        aaa.ljust(6)
                        if i == 2 or i == 3
                        else aaa.ljust(25)
                        if i == 5
                        else aaa
                    )
                    + resetstr
                    for i, aaa in enumerate(aa)
                ]
            )
            bbcolor = strblackbg + color2 + b + resetstr
            if print_stdout:
                try:
                    lock.acquire()
                    print(device_serialcolor + colorsep + aacolor + colorsep + bbcolor)
                finally:
                    lock.release()
        except Exception as fe:
            print(fe)
            continue


def start_logcat(
    adb_path,
    csv_output,
    device_serials,
    print_stdout=True,
    clear_log=True,
    ljustserial=16,
):
    r"""
    Starts logging Android device logs using ADB.

    This function initiates log capturing for specified Android devices using ADB (Android Debug Bridge).
    Logs are saved to a CSV file for further analysis.

    Args:
        adb_path (str): Path to the ADB executable.
        csv_output (str): Path to the CSV file where the logs will be saved.
        device_serials (str or list): A single device serial number as a string, or a list of serial numbers
                                      for multiple devices. Serial numbers are used to identify connected devices.
        print_stdout (bool, optional): If True, prints log messages to the console. Default is True.
        clear_log (bool, optional): If True, clears the device log before capturing. Default is True.
        ljustserial (int, optional): Left-justifies the device serial number in the printed output. Default is 16.

    Returns:
        None

    Example:
        from logcatdevices import start_logcat

        androidcsv = "c:\\csvandroisad.csv"
        _ = start_logcat(
            adb_path=r"C:\Android\android-sdk\platform-tools\adb.exe",
            csv_output=androidcsv,
            device_serials=[
                "127.0.0.1:5565",
                "127.0.0.1:7555",
                "127.0.0.1:7556",
                "emulator-5554",
                "emulator-5564",
            ],
            print_stdout=True,
            clear_log=True,
            ljustserial=16,
        )
    """
    if isinstance(device_serials, tuple):
        device_serials = list(device_serials)
    if isinstance(device_serials, list):
        device_serials = "|".join(device_serials)

    try:
        subprocess.run(
            [
                sys.executable,
                __file__,
                adb_path,
                csv_output,
                device_serials,
                str(int(print_stdout)),
                str(int(clear_log)),
                str(int(ljustserial)),
            ]
        )
    except KeyboardInterrupt:
        pass


def csv2df(csvfile):
    r"""
    Converts a CSV log file to a pandas DataFrame.

    This function reads a CSV file containing Android device log data and converts it into a structured
    pandas DataFrame, enabling easy data manipulation and analysis.

    Args:
        csvfile (str): Path to the CSV log file.

    Returns:
        pandas.DataFrame: A DataFrame containing log data with the following columns:
            - aa_source (str): Source of the log message.
            - aa_date (datetime): Date and time of the log message.
            - aa_processID (int): Process ID associated with the log message.
            - aa_threadID (int): Thread ID associated with the log message.
            - aa_logType (str): Type of log message (e.g., 'V', 'D', 'I', 'W', 'E').
            - aa_tag (str): Tag associated with the log message.
            - aa_message (str): Log message content.

    Example:
        from logcatdevices import csv2df
        androidcsv = "c:\\csvandroisad.csv"
        df = csv2df(androidcsv)
        print(df.to_string())
    """

    import importlib

    pd = importlib.import_module("pandas")
    cols = [
        "aa_source",
        "aa_date",
        "aa_time",
        "aa_processID",
        "aa_threadID",
        "aa_logType",
        "aa_tag",
        "aa_message",
    ]
    df = pd.read_csv(
        csvfile,
        names=cols,
        escapechar="\\",
        quotechar='"',
        delimiter=",",
        encoding="utf-8",
        on_bad_lines="warn",
        encoding_errors="backslashreplace",
    )
    try:
        df["aa_source"] = df["aa_source"].astype("category")
    except Exception:
        pass
    try:
        df["aa_date"] = (
            df["aa_date"] + "-" + str(datetime.now().year) + "-" + df["aa_time"]
        )
        df = df.drop(columns="aa_time")
        df["aa_date"] = pd.to_datetime(df["aa_date"], format="%m-%d-%Y-%H:%M:%S.%f")
    except Exception:
        pass
    try:
        df["aa_processID"] = df["aa_processID"].astype("Int64")
    except Exception:
        pass
    try:
        df["aa_threadID"] = df["aa_threadID"].astype("Int64")
    except Exception:
        pass
    try:
        df["aa_logType"] = df["aa_logType"].astype("category")
    except Exception:
        pass
    try:
        df["aa_tag"] = df["aa_tag"].astype("category")
    except Exception:
        pass
    return df


if __name__ == "__main__":
    collen = len(colors_with_black_bg)
    path_adb = sys.argv[1]
    csvfile = sys.argv[2]
    allserials = sys.argv[3].split("|")
    print_stdout = bool(int(sys.argv[4]))
    clear_log = bool(int(sys.argv[5]))
    ljustserial = int(sys.argv[6])

    if what_os.check_os() == "windows":
        import shortpath83

        path_adb = shortpath83.convert_path_in_string(path_adb)
        csvfile = shortpath83.convert_path_in_string(csvfile)

    touch(csvfile)
    with open(csvfile, mode="a", encoding="utf-8") as f:
        for ini, device_serial in enumerate(allserials):
            color = rgb256(*colors_with_black_bg[ini % collen])
            color2 = rgb256(*colors_with_black_bg[(ini + 1) % collen])
            color3 = rgb256(*colors_with_black_bg[(ini + 2) % collen])
            color4 = rgb256(*colors_with_black_bg[(ini + 3) % collen])
            t = kthread.KThread(
                target=_start_logcat,
                args=(
                    ini,
                    color,
                    color2,
                    color3,
                    color4,
                    device_serial,
                    print_stdout,
                    clear_log,
                    ljustserial,
                ),
                name=device_serial,
            )
            # t.daemon = True
            t.start()
            allthreads.append(t)
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            try:
                for p in allsubprocs:
                    try:
                        kill_subproc(p)
                    except:
                        pass
            except:
                pass
            try:
                for t in allthreads:
                    try:
                        t.kill()
                        sleep(0.1)
                    except:
                        pass

            except:
                pass
    sys.exit(0)
