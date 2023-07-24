import unittest
from unittest.mock import MagicMock, patch
import sys

from lox_services.utils.chrome_version import (
    extract_version_registry,
    extract_version_folder,
    get_chrome_version,
    get_platform,
)


class TestChromeVersion(unittest.TestCase):
    def test_extract_version_registry(self):
        output = """
        Some other registry values...

        DisplayVersion    REG_SZ    92.0.4515.107
        """
        version = extract_version_registry(output)
        self.assertEqual(version, "92.0.4515.107")

    def test_extract_version_folder(self):
        # You can create some test directories and files to simulate the Chrome installation folders
        # For simplicity, let's just set one version here:
        chrome_version = "91.0.4472.164"
        with patch("os.scandir") as mock_scandir:
            with patch("os.path.isdir") as mock_isdir:
                mock_isdir.return_value = True
                mock_scandir.return_value = [
                    type(
                        "MockDir",
                        (object,),
                        {
                            "is_dir": lambda x: True,
                            "path": f"/path/to/Chrome/{chrome_version}",
                        },
                    )()
                ]

                version = extract_version_folder()
                self.assertEqual(version, chrome_version)

    def test_extract_version_folder_not_found(self):
        chrome_version = "91,0,4472,164"
        with patch("os.scandir") as mock_scandir:
            with patch("os.path.isdir") as mock_isdir:
                mock_isdir.return_value = True
                mock_scandir.return_value = [
                    type(
                        "MockDir",
                        (object,),
                        {
                            "is_dir": lambda x: True,
                            "path": f"/path/to/Chrome/{chrome_version}",
                        },
                    )()
                ]

                with self.assertRaises(RuntimeError):
                    extract_version_folder()

    ###
    ### Test get_chrome_version
    ###

    # Linux
    def test_get_chrome_version_linux(self):
        with patch(
            "lox_services.utils.chrome_version.get_platform"
        ) as mock_get_platform:
            mock_get_platform.return_value = "linux"
            with patch("os.path.exists") as mock_exists:
                mock_exists.return_value = True
                with patch("os.popen") as mock_popen:
                    mock_popen.return_value = MagicMock(
                        read=MagicMock(return_value="Google Chrome 92.0.4515.107")
                    )
                    version = get_chrome_version(12)
                    self.assertEqual(version, 92)

    # Mac
    def test_get_chrome_version_mac(self):
        with patch(
            "lox_services.utils.chrome_version.get_platform"
        ) as mock_get_platform:
            mock_get_platform.return_value = "mac"
            with patch("os.popen") as mock_popen:
                mock_popen.return_value = MagicMock(
                    read=MagicMock(return_value="Google Chrome 92.0.4515.107")
                )
                version = get_chrome_version(12)
                self.assertEqual(version, 92)

    # Windows
    def test_get_chrome_version_windows_registry(self):
        with patch(
            "lox_services.utils.chrome_version.get_platform"
        ) as mock_get_platform:
            mock_get_platform.return_value = "windows"
            with patch("os.popen") as mock_popen:
                mock_popen.return_value = MagicMock(read=MagicMock(return_value=""))
                with patch(
                    "lox_services.utils.chrome_version.extract_version_registry"
                ) as mock_extract_version_registry:
                    mock_extract_version_registry.return_value = "92.0.4515.107"
                    version = get_chrome_version(12)
                    self.assertEqual(version, 92)

    def test_get_chrome_version_windows_folder(self):
        with patch(
            "lox_services.utils.chrome_version.get_platform"
        ) as mock_get_platform:
            mock_get_platform.return_value = "windows"
            with patch("os.popen") as mock_popen:
                mock_popen.return_value = MagicMock(read=MagicMock(return_value=""))
                with patch(
                    "lox_services.utils.chrome_version.extract_version_registry"
                ) as mock_extract_version_registry:
                    mock_extract_version_registry.side_effect = RuntimeError
                    with patch(
                        "lox_services.utils.chrome_version.extract_version_folder"
                    ) as mock_extract_version_folder:
                        mock_extract_version_folder.return_value = "92.0.4515.107"
                        version = get_chrome_version(12)
                        self.assertEqual(version, 92)

    def test_get_chrome_version_windows_folder(self):
        with patch(
            "lox_services.utils.chrome_version.get_platform"
        ) as mock_get_platform:
            mock_get_platform.return_value = "windows"
            with patch("os.popen") as mock_popen:
                mock_popen.return_value = MagicMock(read=MagicMock(return_value=""))
                with patch(
                    "lox_services.utils.chrome_version.extract_version_registry"
                ) as mock_extract_version_registry:
                    mock_extract_version_registry.side_effect = RuntimeError
                    with patch(
                        "lox_services.utils.chrome_version.extract_version_folder"
                    ) as mock_extract_version_folder:
                        mock_extract_version_folder.side_effect = RuntimeError
                        version = get_chrome_version(12)
                        self.assertEqual(version, 12)

    @patch("sys.platform", "linux")
    def test_linux_platform(self):
        self.assertEqual(get_platform(), "linux")

    @patch("sys.platform", "darwin")
    def test_mac_platform(self):
        self.assertEqual(get_platform(), "mac")

    @patch("sys.platform", "win32")
    def test_windows_platform(self):
        self.assertEqual(get_platform(), "windows")

    @patch("sys.platform", "not_an_os")
    def test_unsupported_platform(self):
        with self.assertRaises(RuntimeError):
            get_platform()


if __name__ == "__main__":
    unittest.main()
