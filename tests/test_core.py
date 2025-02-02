"""Tests for core modules."""
import sys
import time
import pytest
from unittest.mock import patch, MagicMock
import platform
import codecs
from pathlib import Path
from tik_manager4.core import filelog
from tik_manager4.core import io
from tik_manager4.core import settings
from tik_manager4.core import utils
from tik_manager4.external import fileseq
from tik_manager4.ui.Qt import QtWidgets
from tik_manager4.external.filelock import FileLock, Timeout
from tik_manager4.core.cli import FeedbackCLI


def test_filelog(tmp_path: Path):
    """Test filelog module."""
    tmp_path_ = str(tmp_path)  # FIXME: remove when FileLog is typed
    # test new log
    logbasename = "test_log"
    
    test_log_path = tmp_path / f"{logbasename}.log"
    log = filelog.Filelog(logname=__name__, filename=f"{logbasename}", filedir=tmp_path_)

    assert log.header("Header Test") == "Header Test"
    assert log.title("Title Test") == "Title Test"
    assert log.seperator()
    assert log.info("Test info message") == "Test info message"
    assert log.warning("Test warning message") == "Test warning message"
    assert log.error("Test error message") == "Test error message"
    assert log.exception("Test exception message") == "Test exception message"
    pytest.raises(Exception, log.error, "do_not_proceed", proceed=False)
    assert log.get_last_message() == ("do_not_proceed", "error")

    # test continuing from existing log
    log = filelog.Filelog(logname="new_log_name", filename="test_log", filedir=tmp_path_, date=False, time=False, size_cap=0)
    assert log._get_now() == ""
    assert log.title("Test") == "Test"
    log.clear()
    
    with open(tmp_path / 'test_log.log') as fin:
        log_file_contents = fin.read()

    log_file_contents_truth = "============\nnew_log_name\n============\n\n"
    assert log_file_contents == log_file_contents_truth
    
    # We should probably supply the encoding argument?
    bytes_ = codecs.encode(log_file_contents_truth)
    newline_count = bytes_.count(b"\n")
    nbytes = len(bytes_)
    nbytes_truth_per_system = {
            "Linux": nbytes,
            "Windows": nbytes + newline_count,  # 2 chars for newline on windows
            "Darwin": nbytes
            }
    assert log.get_size() == nbytes_truth_per_system[platform.system()]

def test_creating_a_settings_object_with_and_without_arguments(tmp_path):
    """Test settings module"""
    # create a settings object without any arguments
    _settings = settings.Settings()
    # try defining non-valid file type
    with pytest.raises(Exception):
        _settings.settings_file = str(tmp_path / "test_settings.NA")
    # no extension error
    with pytest.raises(Exception):
        _settings.settings_file = str(tmp_path / "test_settings")
    # directory
    _settings.settings_file = str(tmp_path / "test_settings.json")
    assert _settings.settings_file == str(tmp_path / "test_settings.json")

    # create settings object with arguments
    _settings = settings.Settings(file_path=str(tmp_path / "test_settings.json"))

def test_settings_reading_and_writing_from_disk(tmp_path):
    """Test reading and writing settings from disk"""
    test_path = tmp_path / "test_settings.json"
    assert test_path.exists() == False
    _settings = settings.Settings(file_path=test_path)

    # writing empty data to the file without forcing:
    _settings.apply_settings()
    assert test_path.exists() == False

    # writing empty data to the file with forcing:
    _settings.apply_settings(force=True)
    assert test_path.exists() == True

def test_getting_and_setting_values_with_settings(tmp_path):
    """Test getting property values from settings object"""
    _settings = settings.Settings()
    # test checking the the properties when there is no setting file
    assert _settings.date_modified == None
    assert _settings.settings_file == None
    assert _settings.keys == []
    assert _settings.values == []
    assert _settings.properties == {}

    # define a settings file, add some values
    _settings.settings_file = str(tmp_path / "test_settings.json")
    _settings.add_property("test_string", "test")
    _settings.add_property("test_dict", {"sub_test": "sub_test_initial_value"})
    _settings.apply_settings()
    # try to adding the same property without forcing
    assert _settings.add_property("test_string", "THIS SHOULDNT EXIST", force=False) == False

    # read the __str__ method
    assert str(_settings) == "Settings({'test_string': 'test', 'test_dict': {'sub_test': 'sub_test_initial_value'}})"
    # read the __repr__ method
    assert repr(_settings) == "{'test_string': 'test', 'test_dict': {'sub_test': 'sub_test_initial_value'}}"

    # read the values back
    assert _settings.get_property("test_string") == "test"
    assert _settings.get("test_string") == "test"
    assert _settings.get_property("test_dict") == {"sub_test": "sub_test_initial_value"}
    assert _settings.get("test_dict") == {"sub_test": "sub_test_initial_value"}
    assert _settings.get_sub_property(["test_dict", "sub_test"]) == "sub_test_initial_value"

    # edit the values
    _settings.edit_property("test_string", "test_edited")
    _settings.edit_sub_property(["test_dict", "sub_test"], "sub_test_edited")

    # read the values back
    assert _settings.get_property("test_string") == "test_edited"
    assert _settings.get("test_string") == "test_edited"
    assert _settings.get_property("test_dict") == {"sub_test": "sub_test_edited"}
    assert _settings.get("test_dict") == {"sub_test": "sub_test_edited"}
    assert _settings.get_sub_property(["test_dict", "sub_test"]) == "sub_test_edited"

    # reset the settings
    assert _settings.is_settings_changed() == True
    _settings.reset_settings()

    # read the values back
    assert _settings.get_property("test_string") == "test"
    assert _settings.get("test_string") == "test"
    assert _settings.get_property("test_dict") == {"sub_test": "sub_test_initial_value"}
    assert _settings.get("test_dict") == {"sub_test": "sub_test_initial_value"}
    assert _settings.get_sub_property(["test_dict", "sub_test"]) == "sub_test_initial_value"

    # delete a property
    _settings.delete_property("test_string")
    assert _settings.get_property("test_string") == None

    # update the settings with a new dictionary
    test_data_2 = {"update_test": "this is coming from a new dictionary"}
    _settings.update(test_data_2, add_missing_keys=False)
    assert _settings.get_property("update_test") == None
    _settings.update(test_data_2, add_missing_keys=True)
    assert _settings.get_property("update_test") == "this is coming from a new dictionary"

    # update the settings with another settings object
    test_data_3 = {"update_test_2": "this is coming from another settings object"}
    _settings_2 = settings.Settings()
    _settings_2.set_data(test_data_3)
    _settings.update(_settings_2, add_missing_keys=True)
    assert _settings.get_property("update_test_2") == "this is coming from another settings object"


def test_initialize_and_setting_data_with_settings(tmp_path):
    """Initialize and set data with settings object."""

    _settings_for_initialize = settings.Settings()

    test_data = {"test": "test"}
    # initializing does not considered as altering the data.
    _settings_for_initialize.initialize(test_data)
    assert _settings_for_initialize.is_settings_changed() == False
    assert _settings_for_initialize.get_data() == test_data

    # setting data does considered as altering the data.
    _settings_for_set_data = settings.Settings()
    _settings_for_set_data.set_data(test_data)
    assert _settings_for_set_data.is_settings_changed() == True
    assert _settings_for_set_data.get_data() == test_data

def test_reading_back_from_an_existing_settings_file(tmp_path):
    """Read back from an existing settings file."""
    _settings_1 = settings.Settings(file_path=str(tmp_path / "test_read_settings.json"))
    # add some data
    _settings_1.add_property("test_string", "test")
    _settings_1.add_property("test_dict", {"sub_test": "sub_test_initial_value"})
    _settings_1.apply_settings()
    # read the data back
    _settings_2 = settings.Settings(file_path=str(tmp_path / "test_read_settings.json"))
    assert _settings_2.get_property("test_string") == "test"
    assert _settings_2.get_property("test_dict") == {"sub_test": "sub_test_initial_value"}

    # modify the first settings file and check if the second one will understand that its modified
    _settings_1.edit_property("test_string", "test_edited")
    _settings_1.apply_settings()
    # assert _settings_2.is_modified()
    _settings_2.is_modified()

    # _setting_2 should still hold the old data
    assert _settings_2.get_property("test_string") == "test"
    # reload the data
    _settings_2.reload()
    # now it should hold the new data
    assert _settings_2.get_property("test_string") == "test_edited"

def test_settings_fallback_function(tmp_path):
    """Test settings fallback function."""
    _fallback_settings = settings.Settings(file_path=str(tmp_path / "test_settings_fallback.json"))
    _fallback_settings.add_property("test_string", "fallback_test")
    _fallback_settings.apply_settings()

    _settings = settings.Settings(file_path=str(tmp_path / "test_settings.json"))
    _settings.set_fallback(str(tmp_path / "test_settings_fallback.json"))

    # read the data back
    assert _settings.get_property("test_string") == "fallback_test"

def test_io(tmp_path):
    """Test io module"""
    # create a io module without any arguments
    _io = io.IO()
    # try defining non-valid file type
    with pytest.raises(Exception):
        _io.file_path = str(tmp_path / "test_io.NA")
    # no extension error
    with pytest.raises(Exception):
        _io.file_path = str(tmp_path / "test_io")
    # directory
    _io.file_path = str(tmp_path / "test_io.json")
    assert _io.file_path == str(tmp_path / "test_io.json")

    # create io object with arguments
    _io = io.IO(file_path=str(tmp_path / "test_io.json"))

    test_data = {"test": "test"}

    # test locked files
    _lock = FileLock(str(tmp_path/"test_io.json.lock"))
    _lock.acquire()
    # write data to file
    with pytest.raises(Timeout):
        _io.write(test_data)
    _lock.release()

    # write data to file
    _io.write(test_data)

    # read data from file
    test_data_read = _io.read()
    assert test_data == test_data_read

    # read data from file with different file_path
    _io.read(file_path=str(tmp_path / "test_io.json"))

    # try to read data from file that does not exist
    assert _io.file_exists(str(tmp_path / "test_io.NA")) == False
    with pytest.raises(Exception):
        _io.read(file_path=str(tmp_path/"test_io.NA"))

    # corrupt the test_io.json file purpose is to test the file_exists function
    with open(tmp_path / "test_io.json", "w") as f:
        f.write("test")

    # test reading corrupted file
    pytest.raises(Exception, _io.read)

def test_getting_home_dir(monkeypatch):
    """Test the utils module."""
    # test get_home_dir
    # monkeypatch the os.getenv function
    monkeypatch.setenv("HOME", "/home/user")
    monkeypatch.setenv("USERPROFILE", "/home/user")
    # mock the CURRENT_PLATFORM variable with monkeypatch
    monkeypatch.setattr(utils, "CURRENT_PLATFORM", "Windows")
    assert utils.get_home_dir() == str(Path("/home/user"))
    monkeypatch.setattr(utils, "CURRENT_PLATFORM", "Linux")
    assert utils.get_home_dir() == str(Path("/home/user"))

def test_execute(tmp_path):
    """Test execute function."""
    # test the situation where the file does not exist
    _file = tmp_path / "test_execute.txt"
    # create a file
    _file.touch()

    # an executable that does not exist
    with pytest.raises(ValueError):
        utils.execute(str(_file), executable="non_existing_executable")
    # pretend that the executable exists
    with patch("pathlib.Path.is_file", return_value=True):
        with patch("subprocess.Popen") as mock_popen:
            utils.execute(str(_file), executable="existing_executable")

    if platform.system() == "Windows":
        # Test for Windows
        with patch("tik_manager4.core.utils.CURRENT_PLATFORM", "Windows"):
            with patch("os.startfile") as mock_startfile:
                utils.execute(str(_file))
                mock_startfile.assert_called_once_with(str(_file))

    # Test for Linux
    with patch("tik_manager4.core.utils.CURRENT_PLATFORM", "Linux"):
        with patch("subprocess.Popen") as mock_popen:
            utils.execute(str(_file))
            mock_popen.assert_called_once_with(["xdg-open", str(_file)])

    # Test for another platform (Darwin in this case)
    with patch("tik_manager4.core.utils.CURRENT_PLATFORM", "Darwin"):
        with patch("subprocess.Popen") as mock_popen:
            utils.execute(str(_file))
            mock_popen.assert_called_once_with(["open", str(_file)])

def test_execute_with_sequential_file(monkeypatch, tmp_path):
    """Test execute function with a sequential file."""
    # Create a mock sequential file
    seq_file = tmp_path / "test_seq.0001.exr"
    seq_file.touch()

    mock_seq = MagicMock()
    monkeypatch.setattr(fileseq, "findSequenceOnDisk", lambda x: mock_seq)

    if platform.system() == "Windows":
        with patch("tik_manager4.core.utils.CURRENT_PLATFORM", "Windows"):
            with patch("os.startfile") as mock_startfile:
                utils.execute(str(seq_file.as_posix()))
                mock_startfile.assert_called_once_with(str(seq_file.as_posix()))

    # Test for Linux
    with patch("tik_manager4.core.utils.CURRENT_PLATFORM", "Linux"):
        with patch("subprocess.Popen") as mock_popen:
            utils.execute(str(seq_file.as_posix()))
            mock_popen.assert_called_once_with(["xdg-open", str(seq_file.as_posix())])

    # Test for another platform (Darwin in this case)
    with patch("tik_manager4.core.utils.CURRENT_PLATFORM", "Darwin"):
        with patch("subprocess.Popen") as mock_popen:
            utils.execute(str(seq_file.as_posix()))
            mock_popen.assert_called_once_with(["open", str(seq_file.as_posix())])

def test_execute_with_nonexistent_file(tmp_path):
    """Test execute function with a nonexistent file."""
    non_existent_file = tmp_path / "non_existent_file.txt"
    with pytest.raises(FileNotFoundError):
        utils.execute(non_existent_file.as_posix())

def test_execute_with_nonexistent_sequential_file(tmp_path):
    """Test execute function with a nonexistent sequential file."""
    non_existent_seq_file = tmp_path / "non_existent_seq.0001.exr"
    with pytest.raises(FileNotFoundError):
        print(non_existent_seq_file.as_posix())
        utils.execute(non_existent_seq_file.as_posix())

def test_pop_info_displays_message_and_exits_on_critical():
    feedback = FeedbackCLI()
    with patch("sys.exit") as mock_exit, patch("builtins.input", return_value=""):
        result = feedback.pop_info(
            title="Critical Info",
            text="This is a critical message.",
            critical=True
        )
        assert result == 1
        mock_exit.assert_called_once_with(1)

def test_pop_info_displays_message_and_returns_ok():
    feedback = FeedbackCLI()
    with patch("builtins.input", return_value=""):
        result = feedback.pop_info(
            title="Info",
            text="This is an informational message."
        )
        assert result == 1

def test_pop_question_displays_question_and_returns_user_selection():
    feedback = FeedbackCLI()
    with patch("builtins.input", return_value="yes"):
        result = feedback.pop_question(
            title="Question",
            text="Do you want to proceed?",
            buttons=["yes", "no"]
        )
        assert result == "yes"

def test_pop_question_reprompts_on_invalid_input():
    feedback = FeedbackCLI()
    with patch("builtins.input", side_effect=["invalid", "yes"]):
        result = feedback.pop_question(
            title="Question",
            text="Do you want to proceed?",
            buttons=["yes", "no"]
        )
        assert result == "yes"