# Fragrance Collection Organizer

A desktop app built with Python and PySide6 for organizing your fragrance collection.

![Header](https://i.imgur.com/rFVv2zI.png)

## Features

### Collection Management
- Add, edit, or delete fragrances with all the key details
- Rate seasonality, longevity, and sillage with familiar sliders
- Track notes, house, type, and clones/replicas
- Mark favorites for easy access
- Expand or collapse entries to view more or less info
- Copy fragrance details to your clipboard with a click

### Search & Filter
- Search by name or house
- Filter by season, performance, notes, or favorites
- Sort by any attribute: longevity, sillage, name, season, etc.
- House list that populates based on your collection
- Collapse the filter panel to maximize space

### Built-in Suggestions
- Suggests autocompletions for notes and houses
- Suggestions grow as you make new additions to your collection
- 50+ houses and 200+ notes as a starting base

### Collection Stats & Insights
- Get a quick overview of your total fragrances and houses
- Discover your most common notes and houses
- See season rankings based on your collection
- Copy stats to the clipboard for sharing

### Customizable UI
- Choose from 7 themes:
  - Dark Elegance (default)
  - Light Elegance
  - Monochrome
  - Light Monochrome
  - Emerald Veil
  - Midnight Blue
  - Violet Dream
- Responsive layout that adjusts to window size
- Theme choice is saved between sessions
- Export your collection to CSV with flexible field selection

### Themes

![Themes](https://i.imgur.com/rySPa1L.png)

## ⚠️ Disclaimer on Manual Entry

This app requires you to enter your fragrances manually. If you already own hundreds of fragrances, be prepared—it may take time to enter everything. But once it’s in, managing everything becomes much easier.

## Saved Data

All your collection info is stored locally in a SQLite database (`fragrances.db`). It will be created when you first run the application—just keep it in the same folder as the `.exe`, or in the project root if running from source.

## 🔗 Download

Download a pre-built `.exe` or the full source:
[Download the latest release here](https://github.com/Fro5ty/Fragrance-Collection-Organizer/releases/latest)

Both archives include the license file. If using the `.exe`, just extract and run.

## How to Run or Build It From Source

### Requirements
- Python 3.8+
- PySide6

### Option 1: Run from Source
```bash
pip install -r requirements.txt
python main.py
```

### Option 2: Build a Windows Executable
```bash
python build.py
```
Then run the `.exe` from the `dist` folder that was created.

## License
This project is licensed under the [GNU GPL v3.0](LICENSE).

## Thanks To
- [PySide6](https://doc.qt.io/qtforpython/) - UI Framework
- [Fragrantica](https://www.fragrantica.com/) - Ratings Design Inspiration