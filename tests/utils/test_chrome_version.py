import unittest
from unittest.mock import MagicMock, patch

from lox_services.utils.chrome_version import (
    extract_version_registry,
    extract_version_folder,
    get_chrome_version,
    get_platform,
)


class TestChromeVersion(unittest.TestCase):
    def setUp(self):
        self.dummy_fallback_value = 12
        self.dummy_version_value = 92
        self.dummy_version = "92.0.4515.107"
        self.dummy_full_version = "Google Chrome 92.0.4515.107"
        self.incorrect_version = "91,0,4472,164"
        self.registry_output = """
        Some other registry values...

        DisplayVersion    REG_SZ    92.0.4515.107
        """

    def test_extract_version_registry(self):
        version = extract_version_registry(self.registry_output)
        self.assertEqual(version, self.dummy_version)

    def test_extract_version_folder(self):
        with patch("os.scandir") as mock_scandir:
            with patch("os.path.isdir") as mock_isdir:
                mock_isdir.return_value = True
                mock_scandir.return_value = [
                    type(
                        "MockDir",
                        (object,),
                        {
                            "is_dir": lambda x: True,
                            "path": f"/path/to/Chrome/{self.dummy_version}",
                        },
                    )()
                ]

                version = extract_version_folder()
                self.assertEqual(version, self.dummy_version)

    def test_extract_version_folder_not_found(self):
        with patch("os.scandir") as mock_scandir:
            with patch("os.path.isdir") as mock_isdir:
                mock_isdir.return_value = True
                mock_scandir.return_value = [
                    type(
                        "MockDir",
                        (object,),
                        {
                            "is_dir": lambda x: True,
                            "path": f"/path/to/Chrome/{self.incorrect_version}",
                        },
                    )()
                ]

                with self.assertRaises(RuntimeError):
                    extract_version_folder()

    ###
    ### Test get_chrome_version
    ###

    # Real run (not mocked)
    def test_get_chrome_version_not_mocked(self):
        version = get_chrome_version(self.dummy_fallback_value)
        self.assertIsInstance(version, int)
        self.assertNotEqual(version, self.dummy_fallback_value)

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
                        read=MagicMock(return_value=self.dummy_full_version)
                    )
                    version = get_chrome_version(self.dummy_fallback_value)
                    self.assertEqual(version, self.dummy_version_value)

    # Mac
    def test_get_chrome_version_mac(self):
        with patch(
            "lox_services.utils.chrome_version.get_platform"
        ) as mock_get_platform:
            mock_get_platform.return_value = "mac"
            with patch("os.popen") as mock_popen:
                mock_popen.return_value = MagicMock(
                    read=MagicMock(return_value=self.dummy_full_version)
                )
                version = get_chrome_version(self.dummy_fallback_value)
                self.assertEqual(version, self.dummy_version_value)

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
                    mock_extract_version_registry.return_value = self.dummy_version
                    version = get_chrome_version(self.dummy_fallback_value)
                    self.assertEqual(version, self.dummy_version_value)

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
                        mock_extract_version_folder.return_value = self.dummy_version
                        version = get_chrome_version(self.dummy_fallback_value)
                        self.assertEqual(version, self.dummy_version_value)

    def test_get_chrome_version_windows_folder_error(self):
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
                        version = get_chrome_version(self.dummy_fallback_value)
                        self.assertEqual(version, self.dummy_fallback_value)

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
