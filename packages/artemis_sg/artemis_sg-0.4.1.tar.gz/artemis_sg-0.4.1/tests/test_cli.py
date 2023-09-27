import os.path
from unittest.mock import Mock

import pytest
from click.testing import CliRunner

import artemis_sg.cli as cli


def test_scrape_without_vendor(monkeypatch):
    """
    GIVEN cli
    WHEN the scrape sub-command is called without a vendor argument
    THEN an error exit code occurs
    AND usage text is displayed
    """
    monkeypatch.setattr(cli, "scraper_wrapper", lambda *args: None)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["scrape"])

    assert result.exit_code != 0
    assert "Try 'cli scrape --help'" in result.output


@pytest.mark.parametrize("option", ("-s", "--worksheet"))
def test_scrape_with_args_and_debug(option, monkeypatch):
    """
    GIVEN cli
    WHEN the scrape sub-command is called with a vendor argument
    AND a sheet_id argument
    AND a worksheet argument
    AND the debug flag
    THEN scraper is run with vendor
    AND debug mode is enabled
    """
    expected_path = os.path.join("foo", "bar")
    monkeypatch.setattr(cli, "scraper_wrapper", lambda *args: None)
    monkeypatch.setitem(cli.CFG["asg"]["data"]["file"], "scraped", expected_path)
    vendor_code = "AWESOME_VENDOR"
    sheet_id = "TEST_SHEET_ID"
    worksheet = "TEST_SHEET_TAB"

    runner = CliRunner()
    result = runner.invoke(
        cli.cli, ["--debug", "scrape", option, worksheet, vendor_code, sheet_id]
    )

    assert result.exit_code == 0
    assert "Debug mode enabled" in result.output
    assert f"Running scraper for '{vendor_code}'" in result.output
    assert f"on tab: '{worksheet}' of id: '{sheet_id}'" in result.output
    assert f"saving to '{expected_path}'..." in result.output


def test_scrape_without_worksheet(monkeypatch):
    """
    GIVEN cli
    WHEN the scrape sub-command is called with a vendor argument
    AND a sheet_id argument
    AND the debug flag
    THEN scraper is run with vendor
    AND debug mode is enabled
    """

    def mock_method(*args):
        pass

    monkeypatch.setattr(cli, "scraper_wrapper", mock_method)

    expected_path = os.path.join("foo", "bar")
    monkeypatch.setitem(cli.CFG["asg"]["data"]["file"], "scraped", expected_path)
    vendor_code = "AWESOME_VENDOR"
    sheet_id = "TEST_SHEET_ID"

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["scrape", vendor_code, sheet_id])

    assert result.exit_code == 0
    assert f"Running scraper for '{vendor_code}'" in result.output
    assert f"on tab: 'None' of id: '{sheet_id}'" in result.output
    assert f"saving to '{expected_path}'..." in result.output


def test_download(monkeypatch):
    """
    GIVEN cli
    WHEN the download sub-command is called
    THEN image downloader is run
    """
    monkeypatch.setattr(cli, "img_downloader_wrapper", lambda *args: None)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["download"])

    assert result.exit_code == 0
    assert "Running image downloader..." in result.output


def test_upload(monkeypatch):
    """
    GIVEN cli
    WHEN the upload sub-command is called
    THEN Google Cloud uploader is run
    """
    monkeypatch.setattr(cli, "gcloud_wrapper", lambda *args: None)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["upload"])

    assert result.exit_code == 0
    assert "Running Google Cloud uploader..." in result.output


@pytest.mark.parametrize("s_option", ("-s", "--worksheet"))
@pytest.mark.parametrize("t_option", ("-t", "--title"))
def test_generate(s_option, t_option, monkeypatch):
    """
    GIVEN cli
    WHEN the generate sub-command is called with a title and vendor
    THEN slide generator is run with given title and vendor
    """
    monkeypatch.setattr(cli, "slide_generator_wrapper", lambda *args: None)
    title = "Badass Deck"
    vendor_code = "AWESOME_VENDOR"
    sheet_id = "TEST_SHEET_ID"
    worksheet = "TEST_WORKSHEET"

    runner = CliRunner()
    result = runner.invoke(
        cli.cli,
        ["generate", s_option, worksheet, t_option, title, vendor_code, sheet_id],
    )

    assert result.exit_code == 0
    assert (
        f"Running slide generator to create slide deck '{title}' for '{vendor_code}'"
        in result.output
    )
    assert f"using tab: '{worksheet}' of id: '{sheet_id}'..." in result.output


@pytest.mark.parametrize("s_option", ("-s", "--worksheet"))
def test_generate_no_title(s_option, monkeypatch):
    """
    GIVEN cli
    WHEN the generate sub-command is called without a title
    AND with a vendor
    THEN slide generator is run with default title
    """
    monkeypatch.setattr(cli, "slide_generator_wrapper", lambda *args: None)

    title = "New Arrivals"
    vendor_code = "AWESOME_VENDOR"
    sheet_id = "TEST_SHEET_ID"
    worksheet = "TEST_WORKSHEET"

    runner = CliRunner()
    result = runner.invoke(
        cli.cli, ["generate", s_option, worksheet, vendor_code, sheet_id]
    )

    assert result.exit_code == 0
    assert (
        f"Running slide generator to create slide deck '{title}' for '{vendor_code}'"
        in result.output
    )
    assert f"using tab: '{worksheet}' of id: '{sheet_id}'..." in result.output


def test_generate_no_title_no_worksheet(monkeypatch):
    """
    GIVEN cli
    WHEN the generate sub-command is called without a title
    AND without a worksheet
    AND with a vendor
    THEN slide generator is run with default title
    AND default worksheet
    """

    def mock_method(*args):
        pass

    monkeypatch.setattr(cli, "slide_generator_wrapper", mock_method)

    title = "New Arrivals"
    vendor_code = "AWESOME_VENDOR"
    sheet_id = "TEST_SHEET_ID"

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["generate", vendor_code, sheet_id])

    assert result.exit_code == 0
    assert (
        f"Running slide generator to create slide deck '{title}' for '{vendor_code}'"
        in result.output
    )
    assert f"using tab: 'None' of id: '{sheet_id}'..." in result.output


def test_generate_no_vendor(monkeypatch):
    """
    GIVEN cli
    WHEN the generate sub-command is called without a vendor
    THEN an error exit code occurs
    AND usage text is displayed
    """
    monkeypatch.setattr(cli, "slide_generator_wrapper", lambda *args: None)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["generate"])

    assert result.exit_code != 0
    assert "Try 'cli generate --help'" in result.output


@pytest.mark.parametrize("option", ("-s", "--worksheet"))
def test_sheet_image(option, monkeypatch):
    """
    GIVEN cli
    WHEN the sheet-image sub-command is called with a vendor argument
    AND a workbook
    AND a worksheet
    THEN sheet-image is run with given workbook and worksheet
    """
    expected_path = os.path.join("foo", "bar")
    monkeypatch.setattr(cli, "sheet_image_wrapper", lambda *args: None)
    monkeypatch.setitem(cli.CFG["asg"]["data"]["dir"], "images", expected_path)

    vendor_code = "AWESOME_VENDOR"
    workbook = "myWorkBook"
    worksheet = "myWorkSheet"
    runner = CliRunner()
    result = runner.invoke(
        cli.cli, ["sheet-image", option, worksheet, vendor_code, workbook]
    )

    assert result.exit_code == 0
    assert (
        f"Running sheet-image on '{workbook}/{worksheet}' for '{vendor_code}'"
        in result.output
    )
    assert f"with images from '{expected_path}/thumbnails'" in result.output
    assert " saving to 'out.xlsx'..." in result.output


def test_sheet_image_no_worksheet(monkeypatch):
    """
    GIVEN cli
    WHEN the sheet-image sub-command is called with a vendor argument
    AND a workbook
    AND without a worksheet
    THEN sheet-image is run with given workbook
    """
    expected_path = os.path.join("foo", "bar")
    monkeypatch.setattr(cli, "sheet_image_wrapper", lambda *args: None)
    monkeypatch.setitem(cli.CFG["asg"]["data"]["dir"], "images", expected_path)

    vendor_code = "AWESOME_VENDOR"
    workbook = "myWorkBook"
    runner = CliRunner()
    result = runner.invoke(cli.cli, ["sheet-image", vendor_code, workbook])

    assert result.exit_code == 0
    assert (
        f"Running sheet-image on '{workbook}/None' for '{vendor_code}'" in result.output
    )
    assert f"with images from '{expected_path}/thumbnails'" in result.output
    assert " saving to 'out.xlsx'..." in result.output


def test_mkthumbs(monkeypatch, target_directory):
    """
    GIVEN cli
    WHEN the mkthumbs sub-command is called
    THEN mkthumbs is run
    """
    monkeypatch.setattr(cli, "mkthumbs", lambda *args: None)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["mkthumbs", "--image-directory", target_directory])

    image_directory = target_directory
    assert result.exit_code == 0
    assert f"Running mkthumbs on images in '{image_directory}'..." in result.output


@pytest.mark.parametrize("option", ("-s", "--worksheet"))
def test_order(option, monkeypatch):
    """
    GIVEN cli
    WHEN the order sub-command is called with a vendor argument
    AND a workbook
    AND a worksheet
    THEN order is run for the given vendor with given workbook
    AND spreadsheet.get_order_items is called
    """
    item_id = "foo"
    qty = "42"
    vendor_code = "gj"
    workbook = "myWorkBook"
    worksheet = "myWorkSheet"
    expected_msg = (
        f"Running order on '{workbook}/{worksheet}' for '{vendor_code}'"
        f"Adding items to cart..."
    )

    mock_spreadsheet = Mock(name="mock_spreadsheet")
    mock_scraper = Mock(name="mock_scraper")
    mock_spreadsheet.get_order_items.return_value = [(item_id, qty)]
    monkeypatch.setattr(cli, "spreadsheet", mock_spreadsheet)
    monkeypatch.setattr(cli, "scraper", mock_scraper)
    monkeypatch.setattr(cli, "countdown", lambda *args: None)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["order", option, worksheet, vendor_code, workbook])

    mock_spreadsheet.get_order_items.assert_called()
    mock_scraper.GJScraper().load_item_page.assert_any_call(item_id)
    mock_scraper.GJScraper().add_to_cart.assert_called_with(qty)
    assert expected_msg in result.output
    assert result.exit_code == 0


def test_order_without_worksheet(monkeypatch):
    """
    GIVEN cli
    WHEN the order sub-command is called with a vendor argument
    AND a workbook
    AND without a worksheet
    THEN order is run for the given vendor with given workbook
    AND spreadsheet.get_order_items is called
    """
    item_id = "foo"
    qty = "42"
    vendor_code = "gj"
    workbook = "myWorkBook"
    expected_msg = (
        f"Running order on '{workbook}/None' for '{vendor_code}'"
        f"Adding items to cart..."
    )

    mock_spreadsheet = Mock(name="mock_spreadsheet")
    mock_scraper = Mock(name="mock_scraper")
    mock_spreadsheet.get_order_items.return_value = [(item_id, qty)]
    monkeypatch.setattr(cli, "spreadsheet", mock_spreadsheet)
    monkeypatch.setattr(cli, "scraper", mock_scraper)
    monkeypatch.setattr(cli, "countdown", lambda *args: None)

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["order", vendor_code, workbook])

    mock_spreadsheet.get_order_items.assert_called()
    mock_scraper.GJScraper().load_item_page.assert_any_call(item_id)
    mock_scraper.GJScraper().add_to_cart.assert_called_with(qty)
    assert expected_msg in result.output
    assert result.exit_code == 0


@pytest.mark.parametrize("option", ("-s", "--worksheet"))
def test_order_with_email(option, monkeypatch):
    """
    GIVEN cli
    WHEN the order sub-command is called with a vendor argument
    AND a workbook
    AND a worksheet
    AND an email
    THEN order is run for the given vendor with given workbook and worksheet and email
    AND spreadsheet.get_order_items is called
    """
    item_id = "foo"
    qty = "42"
    email = "foo@example.org"
    vendor_code = "tb"
    workbook = "myWorkBook"
    worksheet = "myWorkSheet"
    expected_msg = (
        f"Running order on '{workbook}/{worksheet}' for '{vendor_code}'"
        f"Adding items to cart..."
    )

    mock_spreadsheet = Mock(name="mock_spreadsheet")
    mock_scraper = Mock(name="mock_scraper")
    mock_spreadsheet.get_order_items.return_value = [(item_id, qty)]
    monkeypatch.setattr(cli, "spreadsheet", mock_spreadsheet)
    monkeypatch.setattr(cli, "scraper", mock_scraper)
    monkeypatch.setattr(cli, "countdown", lambda *args: None)

    runner = CliRunner()
    result = runner.invoke(
        cli.cli, ["order", "--email", email, option, worksheet, vendor_code, workbook]
    )

    mock_spreadsheet.get_order_items.assert_called()
    mock_scraper.TBScraper().impersonate.assert_called_with(email)
    mock_scraper.TBScraper().add_to_cart.assert_called_with(qty)
    assert expected_msg in result.output
    assert result.exit_code == 0
