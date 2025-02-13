import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import datetime
import sys

# Add the directory containing file_reporter.py to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from file_reporter import (
    get_file_info,
    read_file_content,
    load_or_create_ignore_list,
    should_ignore,
    generate_report,
    main,
)

# Save the original sys.exit function
original_sys_exit = sys.exit


def custom_sys_exit(code):
    original_sys_exit(code)


class TestFileReporter(unittest.TestCase):

    @patch("os.path.getmtime")
    @patch("os.path.getsize")
    @patch("os.path.isdir")
    @patch("os.path.basename")
    def test_get_file_info(
        self, mock_basename, mock_isdir, mock_getsize, mock_getmtime
    ):
        mock_basename.return_value = "test.txt"
        mock_isdir.return_value = False
        mock_getsize.return_value = 1024
        mock_getmtime.return_value = datetime.datetime(2023, 10, 1).timestamp()

        expected = {
            "path": "test.txt",
            "name": "test.txt",
            "modification_date": "2023-10-01 00:00:00",
            "size": 1024,
            "type": "File",
        }
        result = get_file_info("test.txt")
        self.assertEqual(result, expected)

    @patch("builtins.open", new_callable=mock_open, read_data="file content")
    def test_read_file_content(self, mock_file):
        result = read_file_content("test.txt")
        self.assertEqual(result, "file content")

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=".git/\nsecret/\n")
    def test_load_ignore_list(self, mock_file, mock_exists):
        mock_exists.return_value = True
        result = load_or_create_ignore_list("test.ignore")
        self.assertEqual(result, [".git", "secret"])

    def test_should_ignore(self):
        ignore_list = [".git", "secret"]
        self.assertTrue(should_ignore(".git", ignore_list))
        self.assertFalse(should_ignore("test.txt", ignore_list))

    @patch("os.walk")
    @patch("file_reporter.get_file_info")
    @patch("file_reporter.read_file_content")
    def test_generate_report(
        self, mock_read_file_content, mock_get_file_info, mock_os_walk
    ):
        mock_os_walk.return_value = [
            ("/root", ("subdir",), ("file1.txt", "file2.txt")),
            ("/root/subdir", (), ("file3.txt",)),
        ]
        mock_get_file_info.side_effect = lambda x: {
            "path": x,
            "name": os.path.basename(x),
            "modification_date": "2023-10-01 00:00:00",
            "size": 1024,
            "type": "File",
        }
        mock_read_file_content.side_effect = lambda x: f"Content of {x}"

        ignore_list = []
        result = generate_report("/root", ignore_list)
        expected = (
            "\r\n\r\nDATEI\r\n[/root/file1.txt]\nName: file1.txt\r\nGeändert: 2023-10-01 00:00:00\r\nGröße: 1024 Bytes\r\nTyp: File\r\n"
            "\r\nContent of /root/file1.txt\r\n"
            "\r\n\r\nDATEI\r\n[/root/file2.txt]\nName: file2.txt\r\nGeändert: 2023-10-01 00:00:00\r\nGröße: 1024 Bytes\r\nTyp: File\r\n"
            "\r\nContent of /root/file2.txt\r\n"
            "\r\n\r\nDATEI\r\n[/root/subdir/file3.txt]\nName: file3.txt\r\nGeändert: 2023-10-01 00:00:00\r\nGröße: 1024 Bytes\r\nTyp: File\r\n"
            "\r\nContent of /root/subdir/file3.txt"
        )
        self.assertEqual(result.replace("\\", "/"), expected)

    @patch("os.walk")
    @patch("file_reporter.get_file_info")
    @patch("file_reporter.read_file_content")
    def test_generate_report_with_ignore_list(
        self, mock_read_file_content, mock_get_file_info, mock_os_walk
    ):
        mock_os_walk.return_value = [
            (
                "/root",
                ("subdir", ".git", "__pycache__", "build"),
                ("file1.txt", "file2.txt"),
            ),
            ("/root/subdir", (), ("file3.txt",)),
            ("/root/.git", (), ("file4.txt",)),
            ("/root/__pycache__", (), ("file5.txt",)),
            ("/root/build", (), ("file6.txt",)),
        ]
        mock_get_file_info.side_effect = lambda x: {
            "path": x,
            "name": os.path.basename(x),
            "modification_date": "2023-10-01 00:00:00",
            "size": 1024,
            "type": "File",
        }
        mock_read_file_content.side_effect = lambda x: f"Content of {x}"

        ignore_list = [".git", "__pycache__", "build/"]
        result = generate_report("/root", ignore_list)
        expected = (
            "\r\n\r\nDATEI\r\n[/root/file1.txt]\nName: file1.txt\r\nGeändert: 2023-10-01 00:00:00\r\nGröße: 1024 Bytes\r\nTyp: File\r\n"
            "\r\nContent of /root/file1.txt\r\n"
            "\r\n\r\nDATEI\r\n[/root/file2.txt]\nName: file2.txt\r\nGeändert: 2023-10-01 00:00:00\r\nGröße: 1024 Bytes\r\nTyp: File\r\n"
            "\r\nContent of /root/file2.txt\r\n"
            "\r\n\r\nDATEI\r\n[/root/subdir/file3.txt]\nName: file3.txt\r\nGeändert: 2023-10-01 00:00:00\r\nGröße: 1024 Bytes\r\nTyp: File\r\n"
            "\r\nContent of /root/subdir/file3.txt"
        )
        self.assertEqual(result.replace("\\", "/"), expected)

    @patch("sys.argv", ["file_reporter.py"])
    @patch("file_reporter.print_help")
    @patch("sys.exit", side_effect=custom_sys_exit)
    def test_main_no_arguments(self, mock_exit, mock_print_help):
        with self.assertRaises(SystemExit):
            main()
        mock_print_help.assert_called_once()
        mock_exit.assert_called_once_with(1)

    @patch("sys.argv", ["file_reporter.py", "--help"])
    @patch("file_reporter.print_help")
    @patch("sys.exit", side_effect=custom_sys_exit)
    def test_main_help_argument(self, mock_exit, mock_print_help):
        with self.assertRaises(SystemExit):
            main()
        mock_print_help.assert_called_once()
        mock_exit.assert_called_once_with(0)

    @patch("sys.argv", ["file_reporter.py", "test_directory"])
    @patch("os.path.exists", return_value=True)
    @patch("file_reporter.find_ignore_file", return_value="test.ignore")
    @patch("file_reporter.load_or_create_ignore_list", return_value=[])
    @patch("file_reporter.generate_report", return_value="report content")
    @patch("file_reporter.save_report_to_file")
    @patch("builtins.open", new_callable=mock_open)
    @patch("sys.exit", side_effect=custom_sys_exit)
    def test_main_valid_directory(
        self,
        mock_exit,
        mock_open,
        mock_save_report_to_file,
        mock_generate_report,
        mock_load_ignore_list,
        mock_find_ignore_file,
        mock_exists,
    ):
        main()
        mock_exists.assert_any_call("test_directory")
        mock_find_ignore_file.assert_called_once_with(None)
        mock_load_ignore_list.assert_called_once_with("test.ignore")
        mock_generate_report.assert_called_once_with("test_directory", [])
        mock_save_report_to_file.assert_called_once_with(
            "report content", os.path.join(os.getcwd(), "file_report.txt")
        )

    @patch("sys.argv", ["file_reporter.py", "invalid_directory"])
    @patch("os.path.exists", return_value=False)
    @patch("sys.exit", side_effect=custom_sys_exit)
    def test_main_invalid_directory(self, mock_exit, mock_exists):
        with self.assertRaises(SystemExit):
            main()
        mock_exists.assert_any_call("invalid_directory")
        mock_exit.assert_called_once_with(1)

    @patch(
        "sys.argv",
        ["file_reporter.py", "test_directory", "--ignore-file", "custom.ignore"],
    )
    @patch("os.path.exists", return_value=True)
    @patch("file_reporter.find_ignore_file", return_value="custom.ignore")
    @patch("file_reporter.load_or_create_ignore_list", return_value=[".git", "secret"])
    @patch("file_reporter.generate_report", return_value="report content")
    @patch("file_reporter.save_report_to_file")
    @patch("builtins.open", new_callable=mock_open)
    @patch("sys.exit", side_effect=custom_sys_exit)
    def test_main_with_ignore_file(
        self,
        mock_exit,
        mock_open,
        mock_save_report_to_file,
        mock_generate_report,
        mock_load_ignore_list,
        mock_find_ignore_file,
        mock_exists,
    ):
        main()
        mock_exists.assert_any_call("test_directory")
        mock_find_ignore_file.assert_called_once_with("custom.ignore")
        mock_load_ignore_list.assert_called_once_with("custom.ignore")
        mock_generate_report.assert_called_once_with(
            "test_directory", [".git", "secret"]
        )
        mock_save_report_to_file.assert_called_once_with(
            "report content", os.path.join(os.getcwd(), "file_report.txt")
        )


if __name__ == "__main__":
    unittest.main(exit=False)
