"""
Tests for the CMS Downloader functionality.

These tests focus on the file checking and selective download logic
without requiring actual network connections.
"""

import shutil
import sys
from pathlib import Path
from unittest.mock import patch

# Add the project root to the path so we can import the downloader
sys.path.insert(0, str(Path(__file__).parent.parent))
from pydrg.helpers.cms_downloader import CMSDownloader


class TestFileCheckingMethods:
    """Test the file checking and JAR discovery methods."""

    def test_check_existing_jars_empty_directories(self, tmp_path):
        """Test checking for JARs when directories are empty."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        result = downloader.check_existing_jars()

        assert result == {"main": set(), "pricers": set()}

    def test_check_existing_jars_with_main_jars(self, tmp_path):
        """Test discovering JARs in the main directory."""
        jars_dir = tmp_path / "jars"
        jars_dir.mkdir()

        # Create some sample JAR files
        (jars_dir / "slf4j-simple-2.0.9.jar").touch()
        (jars_dir / "gfc-base-api-3.4.9.jar").touch()
        (jars_dir / "not-a-jar.txt").touch()  # Should be ignored

        downloader = CMSDownloader(
            jars_dir=str(jars_dir), download_dir=str(tmp_path / "downloads")
        )

        result = downloader.check_existing_jars()

        expected_main = {"slf4j-simple-2.0.9.jar", "gfc-base-api-3.4.9.jar"}
        assert result["main"] == expected_main
        assert result["pricers"] == set()

    def test_check_existing_jars_with_pricers(self, tmp_path):
        """Test discovering JARs in the pricers subdirectory."""
        jars_dir = tmp_path / "jars"
        pricers_dir = jars_dir / "pricers"
        pricers_dir.mkdir(parents=True)

        # Create some sample pricer JAR files
        (pricers_dir / "ipps-pricer-application-2.10.0.jar").touch()
        (pricers_dir / "opps-pricer-application-2.11.0.jar").touch()

        downloader = CMSDownloader(
            jars_dir=str(jars_dir), download_dir=str(tmp_path / "downloads")
        )

        result = downloader.check_existing_jars()

        expected_pricers = {
            "ipps-pricer-application-2.10.0.jar",
            "opps-pricer-application-2.11.0.jar",
        }
        assert result["main"] == set()
        assert result["pricers"] == expected_pricers

    def test_get_missing_jars_for_component_slf4j_all_missing(self, tmp_path):
        """Test detecting missing SLF4J JARs when none are present."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        existing_jars = {"main": set(), "pricers": set()}
        missing = downloader.get_missing_jars_for_component("slf4j", existing_jars)

        expected_missing = {"slf4j-simple-2.0.9.jar", "slf4j-api-2.0.9.jar"}
        assert set(missing) == expected_missing

    def test_get_missing_jars_for_component_slf4j_partial(self, tmp_path):
        """Test detecting missing SLF4J JARs when some are present."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        existing_jars = {"main": {"slf4j-simple-2.0.9.jar"}, "pricers": set()}
        missing = downloader.get_missing_jars_for_component("slf4j", existing_jars)

        assert missing == ["slf4j-api-2.0.9.jar"]

    def test_get_missing_jars_for_component_slf4j_all_present(self, tmp_path):
        """Test detecting missing SLF4J JARs when all are present."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        existing_jars = {
            "main": {"slf4j-simple-2.0.9.jar", "slf4j-api-2.0.9.jar"},
            "pricers": set(),
        }
        missing = downloader.get_missing_jars_for_component("slf4j", existing_jars)

        assert missing == []

    def test_get_missing_jars_for_component_pricers(self, tmp_path):
        """Test detecting missing pricer JARs using regex."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        # One pricer JAR exists.
        existing_jars = {
            "main": set(),
            "pricers": {"ipps-pricer-application-2.10.0.jar"},
        }
        missing = downloader.get_missing_jars_for_component("pricers", existing_jars)

        # Should be missing patterns for all other pricers
        assert len(missing) == len(downloader.REQUIRED_JARS["pricers"]) - 1

        # Check that the pattern for the existing jar is NOT in missing
        assert r"ipps-pricer-application-[\d\.]+\.jar" not in missing

        # Check that a pattern for a missing jar IS in missing
        assert r"opps-pricer-application-[\d\.]+\.jar" in missing

    def test_get_missing_jars_for_component_ioce(self, tmp_path):
        """Test detecting missing ioce JARs using regex."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        # No ioce JAR exists.
        existing_jars = {"main": set(), "pricers": set()}
        missing = downloader.get_missing_jars_for_component("ioce", existing_jars)
        assert len(missing) == 1
        assert r"ioce-standalone-[\d\.]+\.jar" in missing

        # An ioce JAR exists.
        existing_jars = {"main": {"ioce-standalone-26.2.0.7.jar"}, "pricers": set()}
        missing = downloader.get_missing_jars_for_component("ioce", existing_jars)
        assert len(missing) == 0

    def test_get_missing_jars_for_component_invalid_component(self, tmp_path):
        """Test handling of invalid component names."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        existing_jars = {"main": set(), "pricers": set()}
        missing = downloader.get_missing_jars_for_component("invalid", existing_jars)

        assert missing == []

    def test_is_component_complete_true(self, tmp_path):
        """Test component completeness when all JARs are present."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        existing_jars = {"main": {"gfc-base-api-3.4.9.jar"}, "pricers": set()}
        is_complete = downloader.is_component_complete("gfc", existing_jars)

        assert is_complete is True

    def test_is_component_complete_false(self, tmp_path):
        """Test component completeness when JARs are missing."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        existing_jars = {"main": set(), "pricers": set()}
        is_complete = downloader.is_component_complete("gfc", existing_jars)

        assert is_complete is False

    def test_get_all_missing_jars_empty_environment(self, tmp_path):
        """Test getting all missing JARs from an empty environment."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        # Mock check_existing_jars to return empty
        with patch.object(
            downloader,
            "check_existing_jars",
            return_value={"main": set(), "pricers": set()},
        ):
            missing = downloader.get_all_missing_jars()

        # Should have missing JARs for all components
        assert "slf4j" in missing
        assert "gfc" in missing
        assert "grpc" in missing
        assert "msdrg" in missing
        assert "ioce" in missing
        assert "pricers" in missing

    def test_get_all_missing_jars_partial_environment(self, tmp_path):
        """Test getting missing JARs when some components are complete."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        # Mock check_existing_jars to show GFC is complete
        existing_jars = {"main": {"gfc-base-api-3.4.9.jar"}, "pricers": set()}
        with patch.object(
            downloader, "check_existing_jars", return_value=existing_jars
        ):
            missing = downloader.get_all_missing_jars()

        # GFC should not be in missing components
        assert "gfc" not in missing
        # But others should be
        assert "slf4j" in missing


class TestUtilityMethods:
    """Test the utility and reporting methods."""

    def test_list_jar_inventory_empty(self, tmp_path):
        """Test inventory reporting with empty environment."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        with patch.object(
            downloader,
            "check_existing_jars",
            return_value={"main": set(), "pricers": set()},
        ):
            inventory = downloader.list_jar_inventory()

        assert inventory["summary"]["main_jars_count"] == 0
        assert inventory["summary"]["pricer_jars_count"] == 0
        assert inventory["summary"]["components_complete"] == 0
        assert inventory["summary"]["components_missing"] == len(
            downloader.REQUIRED_JARS
        )

    def test_list_jar_inventory_partial(self, tmp_path):
        """Test inventory reporting with partial environment."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        existing_jars = {
            "main": {"gfc-base-api-3.4.9.jar", "slf4j-simple-2.0.9.jar"},
            "pricers": set(),
        }
        with patch.object(
            downloader, "check_existing_jars", return_value=existing_jars
        ):
            inventory = downloader.list_jar_inventory()

        assert inventory["summary"]["main_jars_count"] == 2
        assert inventory["summary"]["pricer_jars_count"] == 0
        assert inventory["components"]["gfc"]["complete"] is True
        assert inventory["components"]["slf4j"]["complete"] is False  # Missing one JAR

    def test_validate_jar_environment_complete(self, tmp_path):
        """Test environment validation when complete."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        # Mock to return no missing components
        with patch.object(downloader, "get_all_missing_jars", return_value={}):
            validation = downloader.validate_jar_environment()

        assert validation["is_valid"] is True
        assert validation["missing_components"] == {}
        assert validation["complete_components"] == len(downloader.REQUIRED_JARS)
        assert "complete" in validation["status_message"]

    def test_validate_jar_environment_incomplete(self, tmp_path):
        """Test environment validation when incomplete."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        # Mock to return missing components
        missing_components = {
            "slf4j": ["slf4j-api-2.0.9.jar"],
            "gfc": ["gfc-base-api-3.4.9.jar"],
        }
        with patch.object(
            downloader, "get_all_missing_jars", return_value=missing_components
        ):
            validation = downloader.validate_jar_environment()

        assert validation["is_valid"] is False
        assert validation["missing_components"] == missing_components
        assert validation["complete_components"] == len(downloader.REQUIRED_JARS) - 2
        assert "Missing 2 components" in validation["status_message"]

    def test_print_jar_inventory_output(self, tmp_path, capsys):
        """Test that print_jar_inventory produces output."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        existing_jars = {"main": {"gfc-base-api-3.4.9.jar"}, "pricers": set()}
        with patch.object(
            downloader, "check_existing_jars", return_value=existing_jars
        ):
            downloader.print_jar_inventory()

        captured = capsys.readouterr()
        assert "JAR Environment Inventory" in captured.out
        assert "Component Status" in captured.out
        assert "GFC" in captured.out

    def test_map_url_to_jar_filename(self, tmp_path):
        """Test URL to JAR filename mapping for pricer downloads."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        # Test cases based on actual CMS pricer URLs
        test_cases = [
            (
                "https://www.cms.gov/files/zip/snf-pricer-20250-v241-executable-jar.zip",
                "snf-pricer-application-2.4.1.jar",
            ),
            (
                "https://www.cms.gov/files/zip/esrd-pricer-20252-v280-executable-jar.zip",
                "esrd-pricer-application-2.8.0.jar",
            ),
            (
                "https://www.cms.gov/files/zip/fqhc-pricer-20252-v270-executable-jar.zip",
                "fqhc-pricer-application-2.7.0.jar",
            ),
            (
                "https://www.cms.gov/files/zip/hha-pricer-20251-v250-executable-jar.zip",
                "hha-pricer-application-2.5.0.jar",
            ),
            (
                "https://www.cms.gov/files/zip/hospice-pricer-20250-v240-executable-jar.zip",
                "hospice-pricer-application-2.4.0.jar",
            ),
            (
                "https://www.cms.gov/files/zip/ipps-pricer-20251-v2100-executable-jar.zip",
                "ipps-pricer-application-2.10.0.jar",
            ),
            (
                "https://www.cms.gov/files/zip/ipf-pricer-20251-v250-executable.zip",
                "ipf-pricer-application-2.5.0.jar",
            ),
            (
                "https://www.cms.gov/files/zip/irf-pricer-20250-v250-executable-jar.zip",
                "irf-pricer-application-2.5.0.jar",
            ),
            (
                "https://www.cms.gov/files/zip/ltch-pricer-20251-v250-executable-jar.zip",
                "ltch-pricer-application-2.5.0.jar",
            ),
            (
                "https://www.cms.gov/files/zip/opps-pricer-20253-v2110-executable-jar.zip",
                "opps-pricer-application-2.11.0.jar",
            ),
        ]

        for url, expected_jar in test_cases:
            result = downloader.map_url_to_jar_filename(url)
            assert result == expected_jar, (
                f"Failed for URL: {url}, expected {expected_jar}, got {result}"
            )

    def test_map_url_to_jar_filename_invalid_url(self, tmp_path):
        """Test URL mapping with invalid/non-pricer URLs."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        # Test with non-pricer URLs
        invalid_urls = [
            "https://www.cms.gov/files/zip/some-other-file.zip",
            "https://example.com/invalid.zip",
            "not-a-url",
        ]

        for url in invalid_urls:
            result = downloader.map_url_to_jar_filename(url)
            assert result is None, f"Expected None for invalid URL: {url}, got {result}"


class TestDownloadLogic:
    """Test the selective download logic."""

    def test_process_slf4j_jar_skip_existing(self, tmp_path):
        """Test that SLF4J processing is skipped when JARs exist."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        # Mock is_component_complete to return True
        with patch.object(downloader, "is_component_complete", return_value=True):
            with patch.object(downloader, "download_slf4j_jar") as mock_download:
                downloader.process_slf4j_jar(force_download=False)

                # Should not call download since component is complete
                mock_download.assert_not_called()

    def test_process_slf4j_jar_force_download(self, tmp_path):
        """Test that SLF4J processing proceeds when forced."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        # Create jars directory
        (tmp_path / "jars").mkdir()

        # Mock download to return mock paths
        mock_paths = [str(tmp_path / "downloads" / "slf4j-simple-2.0.9.jar")]
        with patch.object(downloader, "is_component_complete", return_value=True):
            with patch.object(
                downloader, "download_slf4j_jar", return_value=mock_paths
            ):
                # Create the mock downloaded file
                (tmp_path / "downloads").mkdir()
                (tmp_path / "downloads" / "slf4j-simple-2.0.9.jar").touch()

                downloader.process_slf4j_jar(force_download=True)

                # Should have moved file to jars directory
                assert (tmp_path / "jars" / "slf4j-simple-2.0.9.jar").exists()

    def test_process_slf4j_jar_missing_jars(self, tmp_path):
        """Test that SLF4J processing proceeds when JARs are missing."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        # Create jars directory
        (tmp_path / "jars").mkdir()

        # Mock download to return mock paths
        mock_paths = [
            str(tmp_path / "downloads" / "slf4j-simple-2.0.9.jar"),
            str(tmp_path / "downloads" / "slf4j-api-2.0.9.jar"),
        ]

        with patch.object(downloader, "is_component_complete", return_value=False):
            with patch.object(
                downloader, "download_slf4j_jar", return_value=mock_paths
            ) as mock_download:
                # Create the mock downloaded files
                (tmp_path / "downloads").mkdir()
                for path in mock_paths:
                    Path(path).touch()

                downloader.process_slf4j_jar(force_download=False)

                # Should have called download since component is incomplete
                mock_download.assert_called_once()
                # Should have moved files to jars directory
                assert (tmp_path / "jars" / "slf4j-simple-2.0.9.jar").exists()
                assert (tmp_path / "jars" / "slf4j-api-2.0.9.jar").exists()

    def test_process_gfc_jar_skip_existing(self, tmp_path):
        """Test that GFC processing is skipped when JAR exists."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        with patch.object(downloader, "is_component_complete", return_value=True):
            with patch.object(downloader, "download_gfc_jar") as mock_download:
                downloader.process_gfc_jar(force_download=False)

                # Should not call download since component is complete
                mock_download.assert_not_called()

    def test_process_grpc_jar_missing_jars(self, tmp_path):
        """Test that GRPC processing proceeds when JARs are missing."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        # Create jars directory
        (tmp_path / "jars").mkdir()

        # Mock download to return mock paths
        mock_paths = [
            str(tmp_path / "downloads" / "protobuf-java-3.22.2.jar"),
            str(tmp_path / "downloads" / "protobuf-java-3.21.7.jar"),
        ]

        with patch.object(downloader, "is_component_complete", return_value=False):
            with patch.object(
                downloader, "download_grpc_jar", return_value=mock_paths
            ) as mock_download:
                # Create the mock downloaded files
                (tmp_path / "downloads").mkdir()
                for path in mock_paths:
                    Path(path).touch()

                downloader.process_grpc_jar(force_download=False)

                # Should have called download since component is incomplete
                mock_download.assert_called_once()
                # Should have moved files to jars directory
                assert (tmp_path / "jars" / "protobuf-java-3.22.2.jar").exists()
                assert (tmp_path / "jars" / "protobuf-java-3.21.7.jar").exists()

    def test_build_jar_environment_selective_all_complete(self, tmp_path):
        """Test selective build when all components are complete."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        # Create jars directory
        (tmp_path / "jars").mkdir()

        # Mock all components as complete
        with patch.object(downloader, "is_component_complete", return_value=True):
            with patch.object(downloader, "get_all_missing_jars", return_value={}):
                with patch.object(downloader, "download_msdrg_files") as mock_msdrg:
                    with patch.object(downloader, "download_ioce_files") as mock_ioce:
                        with patch.object(
                            downloader, "download_web_pricers"
                        ) as mock_pricers:
                            result = downloader.build_jar_environment(
                                clean_existing=False
                            )

                            # Should succeed without calling download methods
                            assert result is True
                            mock_msdrg.assert_not_called()
                            mock_ioce.assert_not_called()
                            mock_pricers.assert_not_called()

    def test_build_jar_environment_clean_existing(self, tmp_path):
        """Test clean build that forces all downloads."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        # Create existing jars directory with some files
        jars_dir = tmp_path / "jars"
        jars_dir.mkdir()
        (jars_dir / "existing.jar").touch()

        with patch.object(downloader, "download_msdrg_files", return_value=None):
            with patch.object(downloader, "download_ioce_files", return_value=None):
                with patch.object(downloader, "download_web_pricers"):
                    with patch.object(downloader, "process_gfc_jar") as mock_gfc:
                        downloader.build_jar_environment(clean_existing=True)

                        # Should have cleaned existing directory
                        assert not (jars_dir / "existing.jar").exists()
                        # Should call individual component processors with force_download=True
                        mock_gfc.assert_called_once_with(force_download=True)

    def test_process_zip_for_jars_selective_extraction(self, tmp_path):
        """Test that process_zip_for_jars only extracts specified missing JARs."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        # Create directories
        (tmp_path / "jars").mkdir()
        (tmp_path / "downloads").mkdir()

        # Create a test ZIP file with multiple JARs
        zip_path = tmp_path / "downloads" / "test-package.zip"
        temp_dir = tmp_path / "temp_create_zip"
        temp_dir.mkdir()

        # Create some fake JAR files
        jar1_path = temp_dir / "jar1.jar"
        jar2_path = temp_dir / "jar2.jar"
        jar3_path = temp_dir / "jar3.jar"

        jar1_path.write_text("fake jar 1 content")
        jar2_path.write_text("fake jar 2 content")
        jar3_path.write_text("fake jar 3 content")

        # Create ZIP file containing all JARs
        import zipfile

        with zipfile.ZipFile(zip_path, "w") as zip_ref:
            zip_ref.write(jar1_path, "jar1.jar")
            zip_ref.write(jar2_path, "jar2.jar")
            zip_ref.write(jar3_path, "jar3.jar")

        # Create one existing JAR to simulate partial component
        existing_jar = tmp_path / "jars" / "jar1.jar"
        existing_jar.write_text("existing jar content")

        # Test selective extraction - only extract missing JARs
        missing_jars = ["jar2.jar", "jar3.jar"]  # jar1.jar already exists
        downloader.process_zip_for_jars(
            str(zip_path), "test", missing_jars=missing_jars
        )

        # Verify results
        assert existing_jar.exists()  # Original jar1.jar should remain unchanged
        assert existing_jar.read_text() == "existing jar content"

        assert (tmp_path / "jars" / "jar2.jar").exists()  # Should extract jar2.jar
        assert (tmp_path / "jars" / "jar2.jar").read_text() == "fake jar 2 content"

        assert (tmp_path / "jars" / "jar3.jar").exists()  # Should extract jar3.jar
        assert (tmp_path / "jars" / "jar3.jar").read_text() == "fake jar 3 content"

        # Clean up temp directory
        shutil.rmtree(temp_dir)

    def test_process_zip_for_jars_selective_extraction_regex(self, tmp_path):
        """Test that process_zip_for_jars only extracts specified missing JARs using regex."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        # Create directories
        (tmp_path / "jars").mkdir()
        (tmp_path / "downloads").mkdir()

        # Create a test ZIP file with multiple JARs
        zip_path = tmp_path / "downloads" / "test-ioce-package.zip"
        temp_dir = tmp_path / "temp_create_zip_ioce"
        temp_dir.mkdir()

        # Create some fake JAR files
        jar1_path = temp_dir / "ioce-standalone-1.2.3.jar"
        jar2_path = temp_dir / "another-file.jar"
        jar1_path.write_text("fake ioce jar content")
        jar2_path.write_text("fake other jar content")

        # Create ZIP file containing all JARs
        import zipfile

        with zipfile.ZipFile(zip_path, "w") as zip_ref:
            zip_ref.write(jar1_path, "ioce-standalone-1.2.3.jar")
            zip_ref.write(jar2_path, "another-file.jar")

        # Test selective extraction with regex
        missing_jars = [r"ioce-standalone-[\d\.]+\.jar"]
        downloader.process_zip_for_jars(
            str(zip_path), "ioce", missing_jars=missing_jars
        )

        # Verify results
        assert (tmp_path / "jars" / "ioce-standalone-1.2.3.jar").exists()
        assert not (tmp_path / "jars" / "another-file.jar").exists()

        # Clean up temp directory
        shutil.rmtree(temp_dir)

    def test_process_zip_for_jars_all_existing(self, tmp_path):
        """Test that process_zip_for_jars skips extraction when all JARs exist."""
        downloader = CMSDownloader(
            jars_dir=str(tmp_path / "jars"), download_dir=str(tmp_path / "downloads")
        )

        # Create directories
        (tmp_path / "jars").mkdir()
        (tmp_path / "downloads").mkdir()

        # Create a test ZIP file
        zip_path = tmp_path / "downloads" / "test-package.zip"
        temp_dir = tmp_path / "temp_create_zip"
        temp_dir.mkdir()

        jar_path = temp_dir / "existing.jar"
        jar_path.write_text("jar content in zip")

        import zipfile

        with zipfile.ZipFile(zip_path, "w") as zip_ref:
            zip_ref.write(jar_path, "existing.jar")

        # Create existing JAR
        existing_jar = tmp_path / "jars" / "existing.jar"
        existing_jar.write_text("original jar content")

        # Test with empty missing_jars list
        downloader.process_zip_for_jars(str(zip_path), "test", missing_jars=[])

        # Verify original JAR was not modified
        assert existing_jar.exists()
        assert existing_jar.read_text() == "original jar content"

        # Clean up temp directory
        shutil.rmtree(temp_dir)
