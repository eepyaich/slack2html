### This project is a wrapper on top of [`slack-export-viewer`](https://github.com/hfaran/slack-export-viewer)

# `slack2html`

Export and view your entire team's Slack history (even on a free plan)
as HTML (in channels)!
![Preview](screenshot.png)

## Usage

### 1) Grab your Slack team's export

* Visit [https://my.slack.com/services/export](https://my.slack.com/services/export)
* Create an export
* Wait for it to complete
* Refresh the page and download the export (.zip file) into whatever directory

### 2) Point `slack2html` to it

Point slack2html to the .zip file and let it do its magic

```bash
./slack2html.py -z /path/to/export/zip -o /path/to/output/dir
```

If everything went well, your archive will have been extracted, processed, and browser window will have opened showing your *#general* channel from the export.

## Storing local files

By default, the exported data will still reference files held on Slack.  In some cases (for example, you are leaving Slack)
you may want to take local copies of each file.

Using the ```--local``` option, the script will parse each channel's HTML file and download any files and thumnbnails referenced on files.slack.com.  The script creates a separate version of each channel's index.html file (index_local.html) with the local references.

```bash
./slack2html.py -z /path/to/export/zip -o /path/to/output/dir --no-browser --local --channels channel1,channel2
```

## Notes
- Channel list must be passed in with no spaces
- The output channel directories will be overwritten for each run of the script, so specify a new output folder if you don't want to lose data.
