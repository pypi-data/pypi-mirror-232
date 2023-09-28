#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
from time import sleep

import click
from selenium.common.exceptions import NoSuchWindowException

import artemis_sg.scraper as scraper
import artemis_sg.spreadsheet as spreadsheet
from artemis_sg.config import CFG

MODULE = os.path.splitext(os.path.basename(__file__))[0]

v_skip = "{}: skipping due to lack of VENDOR"
b_skip = "{}: skipping due to lack of WORKBOOK"


@click.group(chain=True)
@click.option("-V", "--verbose", is_flag=True, help="enable verbose mode")
@click.option("-D", "--debug", is_flag=True, help="enable debug mode")
@click.option("-v", "--vendor", default=None, help="Vendor code")
@click.option(
    "-b", "--workbook", default=None, help="Workbook (Sheets Doc ID or Excel File)"
)
@click.option("-s", "--worksheet", default=None, help="Worksheet within Sheets Doc")
@click.pass_context
def cli(ctx, verbose, debug, vendor, workbook, worksheet):
    """artemis_sg is a tool for processing product spreadsheet data.
    Its subcommands are designed to be used to facilitate the follow primary endpoint conditions:

        \b
        * A Google Slide Deck of products
        * An enhanced Excel spreadsheet
        * A website order

    The subcommands can be combined into desired workflows.

    Example of Google Slide Deck workflow:

        $ artemis_sg -v sample -b tests/data/test_sheet.xlsx \\
                scrape download upload generate -t "Cool Deck"

    Example of Sheet Image workflow:

        $ artemis_sg -v sample -b tests/data/test_sheet.xlsx \\
                scrape download mkthumbs sheet-image -o "NewFile.xlsx"
    """
    namespace = f"{MODULE}.cli"
    if debug:
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
        logging.debug(f"{namespace}: Debug mode enabled.")

    elif verbose:
        logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
        logging.info(f"{namespace}: Verbose mode enabled.")
    else:
        logging.basicConfig(format="%(levelname)s: %(message)s")

    # load up context object (ctx)
    ctx.ensure_object(dict)
    ctx.obj["VENDOR"] = vendor
    ctx.obj["WORKBOOK"] = workbook
    ctx.obj["WORKSHEET"] = worksheet


@cli.command()
@click.pass_context
def scrape(ctx):
    """
    Scrape web data for vendor from workbook:worksheet
    """
    cmd = "scrape"
    if ctx.obj["VENDOR"]:
        if ctx.obj["WORKBOOK"]:
            sdb = CFG["asg"]["data"]["file"]["scraped"]
            msg = (
                f"Scraping web data for '{str(ctx.obj['VENDOR'] or '')}' "
                f"using '{str(ctx.obj['WORKBOOK'] or '')}':'{str(ctx.obj['WORKSHEET'] or '')}', "
                f"saving data to '{sdb}'..."
            )
            click.echo(msg)
            scraper_wrapper(
                ctx.obj["VENDOR"], ctx.obj["WORKBOOK"], ctx.obj["WORKSHEET"], sdb
            )
        else:
            click.echo(b_skip.format(cmd), err=True)
    else:
        click.echo(v_skip.format(cmd), err=True)


@cli.command()
def download():
    """
    Download scraped images
    """
    namespace = f"{MODULE}.download"

    download_path = CFG["asg"]["data"]["dir"]["images"]
    click.echo("Downloading images...")
    logging.debug(f"{namespace}: Download path is: {download_path}")

    img_downloader_wrapper()


@cli.command()
def upload():
    """
    Upload local images to Google Cloud Storage Bucket
    """
    namespace = f"{MODULE}.upload"

    upload_source = CFG["asg"]["data"]["dir"]["upload_source"]
    click.echo("Uploading images to Google Cloud...")
    logging.debug(f"{namespace}: Upload source path is: {upload_source}")

    gcloud_wrapper()


@cli.command()
@click.option("-t", "--title", default="New Arrivals", help="Slide deck title")
@click.pass_context
def generate(ctx, title):
    """
    Generate a Google Slide Deck
    """
    cmd = "generate"
    namespace = f"{MODULE}.{cmd}"

    sdb = CFG["asg"]["data"]["file"]["scraped"]
    msg = (
        f"Creating Google Slides deck '{title}' for '{str(ctx.obj['VENDOR'] or '')}' "
        f"using '{str(ctx.obj['WORKBOOK'] or '')}':'{str(ctx.obj['WORKSHEET'] or '')}'..."
    )
    click.echo(msg)
    logging.debug(f"{namespace}: Scraped Items Database is: {sdb}")

    try:
        slide_generator_wrapper(
            ctx.obj["VENDOR"], ctx.obj["WORKBOOK"], ctx.obj["WORKSHEET"], sdb, title
        )
    except Exception as e:
        click.echo(f"Could not generate slide deck:{e}", err=True)
        if not ctx.obj["VENDOR"]:
            click.echo("\tVENDOR not provided", err=True)
        if not ctx.obj["WORKBOOK"]:
            click.echo("\tWORKBOOK not provided", err=True)


@cli.command()
@click.option("-o", "--output", "out", default="out.xlsx", help="Output file")
@click.pass_context
def sheet_image(ctx, out):
    """
    Insert item thumbnail images into spreadsheet
    """
    cmd = "sheet-image"
    namespace = f"{MODULE}.sheet_image"

    if ctx.obj["VENDOR"]:
        if ctx.obj["WORKBOOK"]:
            download_path = CFG["asg"]["data"]["dir"]["images"]
            image_directory = os.path.join(download_path, "thumbnails")
            msg = (
                f"Creating image enhanced spreadsheet for '{str(ctx.obj['VENDOR'] or '')}' "
                f"using '{str(ctx.obj['WORKBOOK'] or '')}':'{str(ctx.obj['WORKSHEET'] or '')}', "
                f"saving Excel file to '{out}'..."
            )
            click.echo(msg)
            logging.debug(
                f"{namespace}: Thumbnail Image Directory is: {image_directory}"
            )

            sheet_image_wrapper(
                ctx.obj["VENDOR"],
                ctx.obj["WORKBOOK"],
                ctx.obj["WORKSHEET"],
                image_directory,
                out,
            )
        else:
            click.echo(b_skip.format(cmd), err=True)
    else:
        click.echo(v_skip.format(cmd), err=True)


@cli.command()
@click.option(
    "--image-directory",
    default=CFG["asg"]["data"]["dir"]["images"],
    help="Image directory",
)
def mkthumbs(image_directory):
    """
    Create thumbnails of images in IMAGE_DIRECTORY
    """
    namespace = f"{MODULE}.mkthumbs"

    click.echo(f"Creating thumbnails of images in '{image_directory}'...")
    logging.debug(f"{namespace}: Image Directory is: {image_directory}")

    mkthumbs_wrapper(image_directory)


@cli.command()
@click.option("--email", "email", default="", help="TB Customer email to impersonate")
@click.pass_context
def order(ctx, email):
    """
    Add items to be ordered to website cart of vendor from spreadsheet
    """
    cmd = "order"
    if ctx.obj["VENDOR"]:
        if ctx.obj["WORKBOOK"]:
            msg = (
                f"Creating web order for '{str(ctx.obj['VENDOR'] or '')}' "
                f"using '{str(ctx.obj['WORKBOOK'] or '')}':'{str(ctx.obj['WORKSHEET'] or '')}', "
                f"Adding items to cart..."
            )
            click.echo(msg)

            order_wrapper(
                email, ctx.obj["VENDOR"], ctx.obj["WORKBOOK"], ctx.obj["WORKSHEET"]
            )
        else:
            click.echo(b_skip.format(cmd), err=True)
    else:
        click.echo(v_skip.format(cmd), err=True)


# wrappers to make the cli testable
def slide_generator_wrapper(vendor, sheet_id, worksheet, sdb, title):
    import artemis_sg.slide_generator as slide_generator

    slide_generator.main(vendor, sheet_id, worksheet, sdb, title)


def gcloud_wrapper():
    import artemis_sg.gcloud as gcloud

    gcloud.main()


def img_downloader_wrapper():
    import artemis_sg.img_downloader as img_downloader

    img_downloader.main()


def scraper_wrapper(vendor, sheet_id, worksheet, sdb):
    import artemis_sg.scraper as scraper

    scraper.main(vendor, sheet_id, worksheet, sdb)


def sheet_image_wrapper(vendor, workbook, worksheet, image_directory, out):
    spreadsheet.sheet_image(vendor, workbook, worksheet, image_directory, out)


def mkthumbs_wrapper(image_directory):
    spreadsheet.mkthumbs(image_directory)


def order_wrapper(email, vendor, workbook, worksheet):
    order_items = spreadsheet.get_order_items(vendor, workbook, worksheet)
    if vendor == "tb":
        if not email:
            logging.error(
                f"order: VENDOR '{vendor}' requires the '--email' option to be set."
            )
            sys.exit(1)
        driver = scraper.get_driver()
        scrapr = scraper.TBScraper(driver)
    elif vendor == "gj":
        driver = scraper.get_driver()
        scrapr = scraper.GJScraper(driver)
    elif vendor == "sd":
        driver = scraper.get_driver()
        scrapr = scraper.SDScraper(driver)
    else:
        logging.error(
            f"order: VENDOR '{vendor}' is not supported by the order command."
        )
        sys.exit(1)

    scrapr.load_login_page()
    scrapr.login()
    if vendor == "tb":
        scrapr.impersonate(email)
    for item, qty in order_items:
        if vendor == "tb":
            item = scrapr.search_item_num(item)
            if not item:
                continue
        res = scrapr.load_item_page(item)
        if res:
            scrapr.add_to_cart(qty)
    scrapr.load_cart_page()
    delay = 600
    print("********    USER INPUT REQUIRED    ********")
    print("Locate the selenium controlled browser")
    print("and manually review and complete your order.")
    print("********  WAITING FOR USER INPUT   ********")
    print()
    print(f"WARNING:  The browser session will terminate in {delay} seconds!!!!")
    print("COUNTING DOWN TIME REMAINING...")
    countdown(delay, driver)


def countdown(delay, driver=None):
    while isBrowserAlive(driver) and delay > 0:
        print(delay, end="\r")
        sleep(1)
        delay -= 1


def isBrowserAlive(driver):
    try:
        driver.current_url
        return True
    except (AttributeError, NoSuchWindowException):
        return False


if __name__ == "__main__":
    cli()
