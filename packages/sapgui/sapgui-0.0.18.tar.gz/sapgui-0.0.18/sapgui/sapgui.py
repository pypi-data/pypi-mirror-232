import win32com.client
import pythoncom
import threading
import subprocess
import pandas as pd
import time
import os

SAP_APP_PATH = r'C:\Program Files (x86)\SAP\FrontEnd\SAPgui\\'
SAP_APP_FILE = 'saplogon.exe'
SAP_TMP_PATH = r'C:\temp\\'
SAP_TMP_FILE = 'tmp.txt'

threads = []


def sap_open(sap_module: dict) -> None:
    """
    Function to open SAP module to operate on it.
    :param sap_module: variable in form of dictionary: {Module Name: Module Code}
    :return: None
    """
    try:
        if SAP_APP_FILE not in str(subprocess.check_output('tasklist')):
            subprocess.Popen(SAP_APP_PATH + SAP_APP_FILE)
            time.sleep(5)
        sapgui = win32com.client.GetObject("SAPGUI")
        application = sapgui.GetScriptingEngine
        if application.Connections.Count == 0:
            connection = application.OpenConnection(list(sap_module.keys())[0])
            session = connection.Children(0)
            session.findById("wnd[0]").sendVKey(0)
    except Exception as e:
        print(e)


def sap_close() -> None:
    """
    Method to close all SAP instances.
    :return: None.
    """
    os.system(f'taskkill /F /IM {SAP_APP_FILE}')


def sap_run(func, *args, **kwargs) -> None:
    """
    Function to run SAP T-Code to generate some result
    :param func: T-Code function to be run
    :param args: parameters of T-Code to be run
    :param kwargs: parameters of T-Code to be run
    :return: None
    """
    sapgui = win32com.client.GetObject("SAPGUI")
    application = sapgui.GetScriptingEngine
    connection = application.Children(0)
    session = connection.Children(0)
    func(session, *args, **kwargs)


def sap_run_threads(func, *args, **kwargs) -> None:
    """
    Function to run SAP T-Code to generate some result in several threads (max 6)
    :param func: T-Code function to be run
    :param args: parameters of T-Code to be run
    :param kwargs: parameters of T-Code to be run
    :return: None
    """
    def sap_run_tread(*arguments):
        """
        Supportive function to run separate thread
        :param arguments: python com ID to open it in separate thread
        :return: None
        """
        pythoncom.CoInitialize()
        win32com.client.Dispatch(pythoncom.CoGetInterfaceAndReleaseStream(
            arguments[0], pythoncom.IID_IDispatch))
        sapgui = win32com.client.GetObject("SAPGUI")
        application = sapgui.GetScriptingEngine
        connection = application.Children(0)
        session = connection.Children(0)
        if kwargs['session_id'] != 0:
            session.createsession()
        time.sleep(3)
        session = connection.Children(kwargs['session_id'])
        if 'run_wait' in kwargs:
            time.sleep(kwargs['run_wait'])
        func(session, *args, **kwargs)
        if kwargs['session_id'] != 0:
            session.findById("wnd[0]").sendVKey(15)

    pythoncom.CoInitialize()
    xl = win32com.client.Dispatch('Excel.Application')
    xl_id = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch, xl)
    t = threading.Thread(target=sap_run_tread, args=[xl_id])
    threads.append(t)
    t.start()


def sap_run_threads_wait() -> None:
    """
    Function to wait for all threads to finish
    :return: None
    """
    for x in threads:
        x.join()


def sap_download_tmp_file_del(file_name: str = SAP_TMP_FILE,
                              file_path: str = SAP_TMP_PATH) -> None:
    """
    Funtion to remove temporary downloaded file according to variable SAP_TMP_FILE
    :param file_name: name of the file which will be considered
    :param file_path: path of the file which will be considered
    :return: None
    """
    if os.path.isfile(file_path+file_name):
        os.remove(file_path+file_name)


def sap_download_tmp_files_del(sap_tmp_files: list, file_path: str = SAP_TMP_PATH) -> None:
    """
    Function to remove indicated list of downloaded files
    :param sap_tmp_files: list of files
    :param file_path: path to the list of files
    :return: None
    """
    for file in sap_tmp_files:
        if os.path.isfile(file_path+file):
            os.remove(file_path+file)


def sap_download_tmp_file(header_row: int, tmp_file_del: bool = True,
                          dtypes: dict = None, file_name: str = SAP_TMP_FILE,
                          file_path: str = SAP_TMP_PATH) -> pd.DataFrame:
    """
    Function to extract downloaded SAP file to pandas dataframe
    :param header_row: number of row where is header fo data
    :param tmp_file_del: fill which need to be extracted, default SAP_TMP_FILE.
    :param dtypes: dictionary to indicate what type proper column should have
    :param file_name: name of the file which will be considered
    :param file_path: path of the file which will be considered
    :return: None
    """
    df = pd.read_csv(file_path + file_name, header=header_row, engine='python',
                     delimiter='\t', encoding='unicode_escape',
                     on_bad_lines='skip', dtype=dtypes)
    label_drop = [x for x in df if 'Unnamed' in x]
    df.drop(label_drop, axis=1, inplace=True)
    if tmp_file_del:
        sap_download_tmp_file_del(file_name, file_path)
    return df