# Search

A file search page for macOS and Linux that runs in [HTML Clay](https://htmlclay.com). Type a word and it lists every file under a folder that contains it, or pick a file type and it lists matching filenames. Click a result to reveal it in Finder or your file manager.

The page is one HTML file. The searching is done by a small Python program beside it, `clay-search`, which the page reaches through HTML Clay's document programs. It uses [ripgrep](https://github.com/BurntSushi/ripgrep) for contents and [fd](https://github.com/sharkdp/fd) for filenames.

## Requirements

- macOS, or Linux (tested on Ubuntu)
- [HTML Clay](https://htmlclay.com) 1.10 or later
- Python 3 (`python3`)
- ripgrep and fd

On macOS (Python 3 ships with the Xcode command line tools):

```sh
brew install ripgrep fd
```

On Ubuntu, which names fd `fdfind` (clay-search finds either name); zenity gives you the folder picker:

```sh
sudo apt install ripgrep fd-find zenity
```

`clay-search` finds `rg` and `fd` on the PATH HTML Clay starts it with. Homebrew's and apt's default locations work.

## Set up

1. Clone this repository anywhere you like:

   ```sh
   git clone https://github.com/panphora/clay-search.git ~/clay-search
   ```

2. Double click `search.htmlclay`. HTML Clay asks "Allow document programs?" for the program named `search`.

   `clay-search` runs as you and can read any file you can. Read it before you allow it. It only reads files, and it only opens Finder and the folder picker.

3. Choose "Allow for This Document". When the picker asks for the program for `search`, select `clay-search` in the cloned folder.

The page opens on your Documents folder. Later double clicks open it straight away. The tray's Programs menu manages the approval.

## Search

- **Shortcuts** jumps to Home, Documents, Desktop, Downloads or Dropbox. A location this computer does not have shows as "(not found)".
- **Folder** takes any absolute or `~/` path. **Choose Folder…** opens the system folder picker (zenity or kdialog on Linux).
- **File type** narrows by kind: Images (including camera raw), Video, Audio, Documents, Spreadsheets & data, Presentations, Code, Fonts, Archives, or a custom extension. With a file type and no query, it lists matching filenames.
- Click a result, or press Enter on a focused one, to reveal the file in Finder, or in your file manager on Linux. The arrow keys move between results.

Content search reads plain text. It does not extract text from PDFs, Word documents or media. ripgrep and fd keep their usual rules, so hidden files and anything in a `.gitignore` are skipped. Large result sets are capped with a notice. On macOS, a contents search in Dropbox skips content files that are not downloaded yet. Listing files still reads `.gitignore` and `.ignore` files, which may download those rule files if they are stored only in the cloud.

The page never saves itself. Searching does not mark it unsaved, and reloading never asks to confirm.

## Search a folder from Finder (optional, macOS)

This adds **Search with Clay** to the Services menu when you right click a folder.

```sh
mkdir -p ~/bin ~/Library/Services
ln -s ~/clay-search/clay-search-folder ~/bin/clay-search-folder
cp -R ~/clay-search/"Search with Clay.workflow" ~/Library/Services/
```

Adjust `~/clay-search` if you cloned somewhere else. The workflow runs `~/bin/clay-search-folder`, which starts HTML Clay if needed and opens the page in the folder you picked. It needs the setup above done first, and it needs the cloned folder trusted: in HTML Clay's tray menu, choose Trusted Folders → Trust a Folder… and pick it. Keep only this app in that folder, because every page in a trusted folder can reach the program you allowed.

If the service does not appear, turn on Search with Clay in System Settings → Keyboard → Keyboard Shortcuts → Services.

The launcher also works from a terminal:

```sh
~/bin/clay-search-folder ~/Downloads
```

## Troubleshooting

- **"rg is not installed" or "fd is not installed":** install them with Homebrew, then quit and reopen HTML Clay so it picks up the new PATH.
- **"was not granted that helper":** you denied the program. Use "Forget document permissions" in the tray's Programs menu, then double click `search.htmlclay` again.
- **The page opens but nothing searches:** check that `clay-search` is executable (`chmod +x clay-search`).

## License

MIT No Attribution. See `LICENSE`.

## Checks

Run the cloud-search regression checks with real ripgrep:

```sh
python3 -m unittest discover -s . -p test_clay_search.py -v
```
