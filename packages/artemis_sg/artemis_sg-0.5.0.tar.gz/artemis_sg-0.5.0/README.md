<p>
    <img height="130"
        src=https://images.squarespace-cdn.com/content/v1/6110970ca45ca157a1e98b76/e4ea0607-01c0-40e0-a7c0-b56563b67bef/artemis.png?format=200w)"
        alt="Artemis logo">
</p>

Table of contents
=================

* [What does this do?](#what-does-this-do)
* [Installation](#installation)
  * [Setup Python Environment](#setup-python-environment)
  * [Google API](#google-api)
  * [Google Cloud](#google-cloud)
  * [Setup Configuration](#setup-configuration)
  * [Final Setup Checklist](#final-setup-checklist)
* [How do I run it?](#how-do-i-run-it)
  * [Session setup](#session-setup)
  * [Slide Generator Workflow](#slide-generator-workflow)
  * [Spreadsheet Images Workflow](#spreadsheet-images-workflow)
* [CLI Command Reference](#cli-command-reference)
  * [Artemis_sg scrape](#artemis_sg-scrape)
  * [Artemis_sg download](#artemis_sg-download)
  * [Artemis_sg upload](#artemis_sg-upload)
  * [Artemis_sg generate](#artemis_sg-generate)
  * [Artemis_sg mkthumbs](#artemis_sg-mkthumbs)
  * [Artemis_sg sheet-image](#artemis_sg-sheet-image)
  * [Artemis_sg order](#artemis_sg-order)
* [Testing](#testing)
* [Package Release Process](#package-release-process)


# What does this do
This is a command line python application used to transform spreadsheet data.

Its primary goals are to produce:
* Google Slide decks
* Excel spreadsheets

It is specifically tailored for the item data and business uses of Artemis Book Sales.

# Installation
You need [Python](https://python.org/downloads) 3.7 or greater and the
[pip package management tool](https://pip.pypa.io/en/stable/installation)
installed.

## Setup Python Environment
It is recommended to create a python virtual environment for this application.
You may create this wherever you store python virtual environments on your
system.

If you don't currently manage python virtual environments, make a directory
for them in your $HOME folder.

In Windows Command Shell:
```cmd
cd $HOME
md python_venvs
```

On \*Nix, open the shell of your choice (the commands below use bash) and
execute the following commands to set up the virtual environment.
```bash
cd $HOME
mkdir python_venvs
```

Create a python virtual environment named `venv_artemis` for this
application and then activate it.  With the environment activated,
install the `artemis_sg` package to enable the CLI.

On Windows, open the Command shell or PowerShell
and execute the following commands to set up the
virtual environment.

In Windows Command Shell:
```cmd
cd $HOME\python_venvs
py -m venv venv_artemis
.\venv_artemis\Scripts\activate.bat
python -m pip install --upgrade pip
pip install artemis_sg
```

In Windows PowerShell:
```cmd
cd $HOME\python_venvs
py -m venv venv_artemis
.\venv_artemis\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install artemis_sg
```

On \*Nix, open the shell of your choice (the commands below use bash) and
execute the following commands to set up the virtual environment.
```bash
cd $HOME/python_venvs
python3 -m venv venv_artemis
source venv_artemis/bin/activate
python -m pip install --upgrade pip
pip install artemis_sg
```

## Google API
The Google API client library for Python is required.
See the
[Google Slides API Quickstart](https://developers.google.com/slides/api/quickstart/python)
for instructions on setting up API authorization.

***Important:***
The setup above will produce a `credentials.json` file needed to authenticate
to the Google Slides and Sheet API.
The application will not work as expected unless the `credentials.json`
location is properly defined in the `config.toml` file for the application.
See the instruction under
[Setup Configuration](#setup-configuration)
for defining of this location.


## Google Cloud
Using Google Cloud Storage requires a private service account key as an
authentication mechanism.
Signed URLs will be generated to put the images into the slides.  This
requires a service account and service account key file.

### Enable Google Cloud Storage API
* In the Google Cloud account dashboard, click 'APIs & Services' from the
  navigation menu.
* Click '+ ENABLE APIS AND SERVICES'
* Search for 'cloud storage'
* Enable Google Cloud Storage JSON API
* Enable Google Cloud Storage

### Create Service Account
* In the Google Cloud account dashboard, select 'APIs & Services' from the
  navigation menu.  Then click 'Credentials' in the sub-menu.
* Click '+ CREATE CREDENTIALS'
* Choose 'Service Account' from the drop-down menu.
* Name the account and click 'Create'.
* Choose 'Owner' from the 'Basic' roll in the 'Grant access' section.
* Click 'Continue'
* Click 'Done'

### Create Service Account Key
* Open the service account from the Credentials list in the Google Cloud
  account.
* Click 'KEYS'
* Click 'ADD KEY'
* Click 'CREATE NEW KEY'
* Choose JSON format
* Click 'CREATE'
* Save the key.
* Modify the file permissions on the key to make it READ-ONLY.

***Important:***
The application will not work as expected unless the Google
Cloud key location is properly defined in the `config.toml` file for the application.
See the instructions under
[Setup Configuration](#setup-configuration)
for defining this location.

## Setup Configuration

### Directories
The application uses local user directories to store its configuration and
data.  They are defined by a combination of the Operating System and user.
Here are the patterns that they follow.

On Windows:
```
$user_data_dir='C:\\Users\\USERNAME\\AppData\\Local\\artemis_sg'
$user_config_dir='C:\\Users\\USERNAME\\AppData\\Local\\artemis_sg'
```

On Linux:
```
user_data_dir='/home/USERNAME/.local/share/artemis_sg'
user_config_dir='/home/USERNAME/.config/artemis_sg'
```

### Creating The Configuration Skeleton
When you first run the application, a skeleton of everything you need for
configuration will be created.  Run the following command to set up the
skeleton.

```sh
artemis_sg --help
```

### Update `config.toml`
All of the needed configuration keys have been created for you in the
`$user_config_dir/config.toml` file.  Some of the fields in this file
*must* be updated in order for the application to operate as expected.

Open the `config.toml` file in your favorite plain text editor and update
the fields in the following sections.

*NOTE*: All string values should be contained in double quotes.

#### Update google.cloud
All of the fields in the `[google.cloud]` section need to be updated to
match your Google Cloud Storage account setup.

* `bucket`: The name of the Google Cloud Storage Bucket that the application
  will use to upload/download files.
* `bucket_prefix`: The prefix name within the Google Cloud Storage Bucket
  (a.k.a folder name) that the application will use to upload/download image
  files.
* `key_file`: The local file path of the Google Cloud Key created in the
  [Create Service Account Key](#create-service-account-key) section.  This
  should be the full absolute path to the key file.  By default, this is set
  to be in the `$user_data_dir`.  You can leave this field value as is and
  copy the Google Cloud Service Account Key file to the location defined in
  this field.
* Copy the Google Cloud Service Account Key file to the application data
  directory as shown in the `google.cloud.key_file` field value.
* Modify the file permissions on the key file to make it READ-ONLY.

#### Update google.docs
None of the fields need to be updated.  However, you will now need to copy
the `credentials.json` file created in the [Google API](#google-api) section
to the path shown for the `api_creds_file` field.

* Copy the `credentials.json` file to the application data directory as shown
  in the `api_creds_file` field value.
* Modify the file permissions on the token to make it READ-ONLY.

## Final Setup Checklist
Once you have completed all of the above setup [steps](#installation), run
through the following checklist to make sure you are ready to proceed.

* Google API `credentials.json` is located in the application data directory.
* `config.toml` has been updated with valid values for the following:
    * `google.cloud.bucket` - This should be set to a valid cloud bucket.
    * `google.cloud.bucket_prefix` - This should be set to a valid cloud bucket prefix.
    * `google.cloud.key_file` - This should be set to the name of your Service key file.
* `artemis_sg --help` - results in usage text showing the defined subcommands.

# How do I run it
For each work session, you will need to activate the python virtual environment
prior to executing any commands.  Once the environment is activated, you can
execute the [Slide Generator Workflow](#slide-generator-workflow), the
[Spreadsheet Images Workflow](#spreadsheet-images-workflow) as outlined
below or run any of the commands independently as needed.

## Session Setup
Session setup comprises the following steps:

* Activate the previously created python virtual environment.

On Windows, open the Command shell or PowerShell
and execute the following command to set up the
session.

In Windows Command Shell:
```cmd
$HOME\python_venvs\venv_artemis\Scripts\activate.bat
```

In Windows PowerShell:
```powershell
$HOME\python_venvs\venv_artemis\Scripts\Activate.ps1
```

On \*Nix, open the shell of your choice (the commands below use bash) and
execute the following command to set up the session.
```bash
source $HOME/python_venvs/venv_artemis/bin/activate
```

## Slide Generator Workflow
In order to produce a slide deck, the following workflow is prescribed.
These elements are broken into separate components so that they might be
executed without a defined pipeline if needed.

The package includes a set of subcommands under the unified CLI command
`artemis_sg` once it is installed to facilitate this workflow.  See
the complete [CLI Command Reference](#cli-command-reference) for more
detail on each of these commands.

Steps in the workflow that are a manual task not handled by the software
are highlighted with the *Manual* tag.

* [Create Spreadsheet](#create-spreadsheet) (*Manual*)
* [Add/Update Vendor](#add/update-vendor) (*Manual*)
* [Scrape Data](#scrape-data)
* [Download Images](#download-images)
* [Upload Images to Google Cloud](#upload-images-to-google-cloud)
* [Generate Slide Deck](#generate-slide-deck)

### Create Spreadsheet
*Manual*

Create spreadsheet that includes the field titles in row 1 and the desired
slide records in subsequent rows.  The spreadsheet must include a column for
ISBN numbers.  The ISBN numbers are assumed to be in the
[ISBN-13 format](https://www.isbn.org/about_ISBN_standard).  Make a
note of the location of this spreadsheet in your file system.
You may want to re-use this location in the
[spreadsheet images workflow](#spreadsheet-images-workflow).

### Add/Update Vendor
*Manual*

The vendors are defined in the `[asg.vendors]` field of the `config.toml` file.
They contain three keys:

* `code`: This is the VENDOR code used to reference the VENDOR when using the
  `artemis_sg` command set.
* `name`: This is the full name of the vendor as it will appear on the Google
  Slide Decks created by the `artemis_sg generate` command.
* `isbn_key`:  This is the value used to identify ISBN data columns in
  spreadsheets.

Open `config.toml` in your favorite text editor.  If there is not an existing
record for the vendor, add one with the following pattern, including the field
key used for ISBN numbers.

If there is an existing record, update the appropriate values.

The format is as follows:
```
[asg]
vendors = [
    { code = "sample", name = "Sample Vendor", isbn_key = "ISBN-13" },
]
```

### Scrape Data
Run the `artemis_sg scrape` command to save the item descriptions and image
URLs gathered for each item record in the spreadsheet to the file defined by the
configuration field `[asg.data.file.scraped]`.  The base command needs a valid
vendor code argument to map to the applicable vendor record updated in the
`[asg.vendors]` configuration field in the
[workflow step above](#add/update-vendor).  The base command also needs a valid
WORKBOOK identifier.  The WORKBOOK identifier can be a Google Sheet ID or an
Excel file location in which the item data
resides.

Example:
```shell
artemis_sg --verbose --vendor sample_vendor --workbook MY_GOOGLE_SHEET_ID scrape
```

### Download Images
Download images from the scraped data using the `artemis_sg download` command.

Example:
```shell
artemis_sg --verbose download
```

### Upload Images to Google Cloud
Run the `artemis_sg upload` command to upload previously download images to
Google Cloud.

Example:
```shell
artemis_sg --verbose upload
```

### Generate Slide Deck
Run the `artemis_sg generate` command to create a Google Slide deck of the
items in the spreadsheet including the description and images gathered by the
[scrape workflow step](#scrape-data).  You should set a desired slide title
using the `--title` option.  The base command needs a valid vendor code, and a
valid WORKBOOK (Google Sheet ID or Excel file path) in which the item data
resides.

Example:
```cmd
artemis_sg --verbose --vendor sample_vendor --workbook MY_GOOGLE_SHEET_ID ^
           generate --title "Badass presentation"
```

### Command Chaining
The above `artemis_sg` sub-commands can be "chained" together to perform the
automated steps of the workflow using a single "chained" command.  The command
chain will run in the order specified. The base command needs a valid vendor
code, and a valid WORKBOOK (Google Sheet ID or Excel file path) in which the
item data resides.  The `generate` command can take an optional `--title`.

Example:
```shell
artemis_sg --vendor sample_vendor \
           --workbook MY_GOOGLE_SHEET_ID \
           scrape download upload generate --title "Badass presentation"
```


## Spreadsheet Images Workflow
In order to produce a spreadsheet with thumbnail images added for items, the
following workflow is suggested.

The following steps are shared with the
[slide generator workflow](#slide-generator-workflow).  These steps are linked
to the appropriate step in that workflow rather then duplicating them here.

* [Create Spreadsheet](#create-spreadsheet) (*Manual*)
* [Add/Update Vendor](#add/update-vendor) (*Manual*)
* [Scrape Data](#scrape-data)
* [Download Images](#download-images)

The unique steps for this workflow are:

* [Create Thumbnails](#create-thumbnails)
* [Add Thumbnails to Spreadsheet](#add-thumbnails-to-spreadsheet)

### Create Thumbnails
Create thumbnail images from previously downloaded images using the `artemis_sg
mkthumbs` command.

Example:
```shell
artemis_sg --verbose mkthumbs
```

### Add Thumbnails to Spreadsheet
Create a new Excel spreadsheet containing a thumbnail images column populated
with available thumbnails using the `artemis_sg sheet-image` command.
The base command needs a valid vendor code, and a valid WORKBOOK
(Excel file path) in which the item data resides.
This file path can be noted from
the [Create Spreadsheet](#create-spreadsheet) step.

**NOTE:** Currently, `artemis_sg sheet-image` does not support Google Sheet IDs
as a valid WORKBOOK type.

By default, the new Excel file is saved as "out.xlsx" in the directory from
which the command was run.  The
`--output` option can be used to specify a desired output file.  The
specification for the `--output` file can include either an absolute or
relative path location for the file as well.

Example:
```cmd
artemis_sg --verbose ^
           --vendor sample_vendor ^
           --workbook "C:\Users\john\Documents\spreadsheets\my_spreadsheet.xlsx" ^
           sheet-image
```

Example, specifying output file with an absolute file path:
```cmd
artemis_sg --verbose ^
           --vendor sample_vendor ^
           --workbook "C:\Users\john\Documents\spreadsheets\my_spreadsheet.xlsx" ^
           sheet-image ^
           --output "C:\Users\john\Documents\spreadsheets\my_new_spreadsheet.xlsx"
```

Example, specifying output file with a relative file path:
```cmd
artemis_sg --verbose ^
           --vendor sample_vendor ^
           --workbook "C:\Users\john\Documents\spreadsheets\my_spreadsheet.xlsx" ^
           sheet-image ^
           --output "..\..\my_new_spreadsheet.xlsx" ^
```

### Command Chaining
The above `artemis_sg` sub-commands can be "chained" together to perform the
automated steps of the workflow using a single "chained" command.  The command
chain will run in the order specified. The base command needs a valid vendor
code, and a valid WORKBOOK (Excel file path) in which the
item data resides.  The `sheet-image` command can take an optional `--output`.

Example:
```cmd
artemis_sg --vendor sample_vendor ^
           --workbook "C:\Users\john\Documents\spreadsheets\my_spreadsheet.xlsx" ^
           scrape download mkthumbs sheet-image
           --output "..\..\my_new_spreadsheet.xlsx"
```


# CLI Command Reference
Many of the references below deal with the terms WORKBOOK and WORKSHEET.  These
terms have the following meaning in the context of the artemis_sg project.

* WORKBOOK: A spreadsheet object.  This object is a container that may have one
  or more WORKSHEET objects inside of it.  These objects are expected to be one
  of the following sources.
  * Google Sheet: As identified by a Google Sheet ID string.
  * Excel (xlsx) file: As identified by a file path.
* WORKSHEET: A specific sheet that contains data.  This object is always contained
  within a WORKBOOK.  These objects are identified by a string name.  Both Excel
  and Google Sheets set the default name to the first sheet object as "Sheet1".

The documentation refers to the combination of these identifiers by combining them
with a colon in the format WORKBOOK:WORKSHEET.

## artemis_sg
The Artemis Slide Generator consists of a single `artemis_sg` command with
many subcommands.

Artemis_sg usage: `artemis_sg [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...`

The `artemis_sg` base command provides optional `--verbose` and `--debug` options
to increase the level of feedback provided during execution.

The base command also includes optional `--vendor`, `--workbook`, and `--worksheet`
options.  These are used to pass context information to the subcommands.  Some
subcommands require `--vendor` and `--workbook` values.  These expectations are
noted in the subcommand references below.

A `--help` option is available to display command usage and available subcommands.
```
artemis_sg --help
```

All `artemis_sg` subcommands also provide a `--help` option to display usage
for the given subcommand.

Example:
```
artemis_sg --help
```

### Chaining
The subcommands for `artemis_sg` can be "chained" together.  This allows running
multiple subcommands sequentially without entering additional commands.  The
responsibilities for the arguments and options remains the same as the individually
run commands.

Example:
```cmd
artemis_sg --vendor sample_vendor ^
           --workbook "C:\Users\john\Documents\spreadsheets\my_spreadsheet.xlsx" ^
           scrape download mkthumbs sheet-image
           --output "..\..\my_new_spreadsheet.xlsx"
```


## artemis_sg scrape
The `artemis_sg scrape` command iterates over the item rows in the spreadsheet
provided by the `--workbook`:`--worksheet` values passed by the base command.
For each ISBN in the WORKBOOK:WORKSHEET, it
searches for item descriptions and images in a web browser.  It collects this
information and stores it in the file defined by the configuration field
`[asg.data.file.scraped]`.  If data for an ISBN already exists in the datafile,
the ISBN is skipped and does not result in re-scraping data for that record.

Artemis_sg scrape usage: `artemis_sg --vendor VENDOR --workbook WORKBOOK scrape [OPTIONS]

The command expects a `VENDOR` to be passed to it from the base command.  This is a
vendor code that should match a vendor code in the
configuration field `[asg.vendors]`.  This code is used to look up the
vendor record in `[asg.vendors]` to find the appropriate ISBN_key
associated with the vendor's data in their spreadsheets.

The command also expectes a `WORKBOOK` to be passed to it from the base command.  This
references the WORKBOOK (Google Sheet ID or Excel file path) containing the
WORKSHEET with the item rows on
which to conduct its work.

**NOTE:** Without a defined WORKSHEET, the first sheet in the WORKBOOK will be used.
If the given WORKBOOK contains multiple sheets and the sheet containing the desired
data is not the first sheet in the WORKBOOK, the `--worksheet` will need to be specified
for the base command.

The command utilizes configuration variables stored in `config.toml` to set the vendor
from `[asg.vendors]` and scraped items database from
`[asg.data.file.scraped]`.

The command takes no arguments.  Other then `--help`, no additional options
are available.

## Artemis_sg download
The `artemis_sg download` command iterates over the data records in
the file defined by the configuration field `[asg.data.file.scraped]` For
each record, it downloads the image files associated with the record to a
local directory as defined by the configuration field `[asg.data.dir.images]`.

Artemis_sg download usage: `artemis_sg download [OPTIONS]`

The command takes no arguments.  Other then `--help`, no additional options
are available.

## Artemis_sg upload
The `artemis_sg upload` command uploads the files in the directory defined by
the configuration field `[asg.data.dir.upload_source]` to the Google Cloud bucket defined
by the configuration field `[google.cloud.bucket]`.  Only the first level of the
source directory is uploaded.  Subdirectories of the source directory are not
traversed for the upload.  All uploaded files are prefixed with value defined
by the configuration field `[google.cloud.bucket_prefix]`.

Artemis_sg upload usage: `artemis_sg upload [OPTIONS]`

The command takes no arguments.  Other then `--help`, no additional options
are available.

## Artemis_sg generate
The `artemis_sg generate` command generates a Google Slides document.

The slide deck will be given a title based on the values supplied by the `VENDOR`
and the `--title` option.  The title slide will be in the following format:
```
Artemis Book Sales Presents...
Vendor Name, Title
```

The command expects a `VENDOR` to be passed to it from the base command.  This is a
vendor code that should match a vendor code in the
configuration field `[asg.vendors]`.  This code is used to look up the
vendor record in `[asg.vendors]` to find the appropriate ISBN_key
associated with the vendor's data in their spreadsheets.

The command also expectes a `WORKBOOK` to be passed to it from the base command.  This
references the WORKBOOK (Google Sheet ID or Excel file path) containing the
WORKSHEET with the item rows on
which to conduct its work.

**NOTE:** Without a defined WORKSHEET, the first sheet in the WORKBOOK will be used.
If the given WORKBOOK contains multiple sheets and the sheet containing the desired
data is not the first sheet in the WORKBOOK, the `--worksheet` will need to be specified
for the base command.

The `artemis_sg generate` command iterates over the item rows in the
WORKBOOK:WORKSHEET.  For each row in
the spreadsheet for which it has image data it creates a slide containing the
spreadsheet data, the description saved in the file defined by the configuration
field `[asg.data.file.scraped]`, and the images saved in the
`[google.cloud.bucket]`.  The Google sheet will be saved to the root of the
Google Drive associated with the credentials created during initial
installation.

Artemis_sg generate usage: `artemis_sg generate [OPTIONS]`

The command utilizes configuration fields stored in `config.toml` to set the vendor
from `[asg.vendors]` and scraped items database from
`[asg.data.file.scraped]`.

### Options
The command provides optional options for overriding default
values used during execution.

* `-t` or `--title`: Sets the slide deck title used on the first slide in
  the deck.  This option *should* normally be set to prevent the default
  value of "New Arrivals" from being used.


## Artemis_sg mkthumbs
The `artemis_sg mkthumbs` command creates thumbnail images from images located
in a given directory.  These thumbnail images are saved to a `thumbnails`
subdirectory in the original image directory.  These files are given the same
names as their originals.  By default, the command will use the directory
defined by the configuration field `[asg.data.dir.images]`.  All thumbnails are
130 pixels x 130 pixels in size.

For example, given the default value of `downloaded_images` for
`[asg.data.dir.images]` with a single image in it, running the command would
result in the following layout.
```
$user_data_dir/downloaded_images/
├── 9780228101208.jpg
└── thumbnails
    └── 9780228101208.jpg
```

Artemis_sg mkthumbs usage: `artemis_sg mkthumbs [OPTIONS]`

### Options
The command provides optional options for overriding default
values used during execution.

* `--image-directory`: An alternate image directory to use for generating
  thumbnails should you wish to use it on a set of images other than those in
  the `[asg.data.dir.images]`.

## Artemis_sg sheet-image
The `artemis_sg sheet-image` command modifies a local Excel spreadsheet file to
include thumbnail images in the second column for items in which local
thumbnail image files are available and saves it as a new file.  By default,
the thumbnail images are assumed to be in `[asg.data.dir.images]/thumbnails`.  By
default, the new Excel file is saved as `out.xlsx` in the current working directory.

**NOTE:** Currently, `artemis_sg sheet-image` does not support Google Sheet IDs
as a valid WORKBOOK type.

Artemis_sg sheet-image usage: `artemis_sg sheet-image [OPTIONS]`

The command expects a `VENDOR` to be passed to it from the base command.  This is a
vendor code that should match a vendor code in the
configuration field `[asg.vendors]`.  This code is used to look up the
vendor record in `[asg.vendors]` to find the appropriate ISBN_key
associated with the vendor's data in their spreadsheets.

The command also expectes a `WORKBOOK` to be passed to it from the base command.  This
references the WORKBOOK (Excel file path) containing the
WORKSHEET with the item rows on
which to conduct its work.

**NOTE:** Without a defined WORKSHEET, the first sheet in the WORKBOOK will be used.
If the given WORKBOOK contains multiple sheets and the sheet containing the desired
data is not the first sheet in the WORKBOOK, the `--worksheet` will need to be specified
for the base command.

**NOTE:** Currently, `artemis_sg sheet-image` does not support Google Sheet IDs
as a valid WORKBOOK type.

### Options
The command provides optional options for overriding default
values used during execution.

* `--output FILE`: Write the modified Excel file to a specified output file
  instead of the default `out.xlsx`.

Example:
```cmd
artemis_sg --debug --vendor sample_vendor --workook Test_Spreadsheet.xlsx --worksheet "My Sheet" ^
           sheet-image --output Spreadsheet_with_images.xlsx
```

## Artemis_sg order
The `artemis_sg order` command populates the website cart for a given vendor
with items from a WORKBOOK:WORKSHEET.  The WORKSHEET *must* contain an "Order"
column from which the tool will get the quantity of each item to put into the
cart.

The browser instance with the
populated cart is left open for the user to review and manually complete the
order.  The user will be asked to manually login during the execution of this
command.

Artemis_sg sheet-image usage: `artemis_sg order [OPTIONS]`

The command expects a `VENDOR` to be passed to it from the base command.  This is a
vendor code that should match a vendor code in the
configuration field `[asg.vendors]`.  This code is used to look up the
vendor record in `[asg.vendors]` to find the appropriate ISBN_key
associated with the vendor's data in their spreadsheets.

The command also expectes a `WORKBOOK` to be passed to it from the base command.  This
references the WORKBOOK (Excel file path) containing the
WORKSHEET with the item rows on
which to conduct its work.

**NOTE:** Without a defined WORKSHEET, the first sheet in the WORKBOOK will be used.
If the given WORKBOOK contains multiple sheets and the sheet containing the desired
data is not the first sheet in the WORKBOOK, the `--worksheet` will need to be specified
for the base command.

**NOTE:** Currently, `artemis_sg sheet-image` does not support Google Sheet IDs
as a valid WORKBOOK type.

### Options
The command provides optional options for overriding default
values used during execution.

* `--email EMAIL`: Use the provided email to impersonate a TB customer.

Example:
```cmd
artemis_sg --vendor sample_vendor --workbook Spreadsheet.xlsx --worksheet Sheet1 ^
           order --email foo@example.org
```

**NOTE:** The browser opened by this command is controlled by this command.
The browser will automatically close and the session will be terminated at the
end of the defined waiting period.  If the web order has not been completed by
the end of the waiting period, the cart may be lost depending on how the website
handles its session data.


# Testing
[Pytest](https://docs.pytest.org/en/7.1.x/index.html) is used for testing.
All tests are in the `tests` directory.  The
full test suite can be run with the following command.

```shell
pytest
```

Some of the tests are full integration tests that assume connections to the
internet and a Google Cloud account.  The full integration tests need access to
a Google Sheet.  The sheet for these tests should be defined in `config.toml` using
the following fields.  The Google sheet should also have a small number of
records in it and the ISBN column should use the heading "ISBN-13".  These
tests will generate a slide deck on the authenticated account.  Such slide
decks will need to be manually deleted since the application does not have
permission to do so.

```
asg.test.sheet.id="GOOGLE_SHEET_ID_HERE"
```

The full integration tests are time consuming and can be skipped using the
following command.

```shell
pytest -m 'not integration'
```

## Installing from test.pypi.org
When testing pre-release packages published to test.pypi.org, `pip` needs an
extra index to find them.  The extra index is required because `platformdirs`
is not available from the `test.pypi.org` site.
```
asg_pkg_ver=0.0.0.dev0
pip install -i https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple \
    artemis_sg==$asg_pkg_ver
```

# Package Release Process
The release steps are executed using the [hatch](https://hatch.pypa.io/latest/)
Python project manager.

Hatch will dynamically create the version number.

## Lint
Ensure that the code passes the lint checks with the following command.  The
command should complete with an exit code of `0`.
```
hatch run lint
echo $?  # should be 0
```

## Test
All "not integration" tests must pass before building a package release candidate.
Run the following command and verify that *ALL* tests pass.
```
hatch run test
```

## Build
Build source and built distribution packages and remove previous builds with
the following command.
```
hatch build -c
```

## Publish
This assumes publishing to [pypi.org](https://pypi.org/).
An API token will be necessary to authorize publication.

Publish the build using the following command.
You can set the `user` and `auth` via the environment variables
`HATCH_INDEX_USER` and `HATCH_INDEX_AUTH` respectively if you don't
want to pass them on the command line.
```
hatch publish --user __token__ --auth pypi-<SECRET_TOKEN>
```

If publishing to test.pypi.org add the `--repo test` option to the `publish`
command.
```
hatch publish -r test -u __token__ -a pypi-<SECRET_TOKEN>
```
