# Quick Vertex Color

A lightweight Blender add-on for quickly assigning color attributes to selected mesh vertices.

## Features

- Quick color picker in the 3D View sidebar.
- Preset buttons for **Black**, **White**, **Red**, **Green**, and **Blue**.
- Assign the selected color to currently selected vertices in Edit Mode.
- Automatically create the target color attribute when it does not exist.
- Supports **CORNER** and **POINT** color attribute domains.
- Supports **BYTE_COLOR** and **FLOAT_COLOR** storage.
- Designed for Blender **4.2+**.

## Installation

1. Download this repository.
2. Zip the `quick_vertex_color_addon` folder itself if needed.
3. In Blender, open **Edit > Preferences > Add-ons**.
4. Choose **Install from Disk...** and select the add-on ZIP.
5. Enable **Quick Vertex Color**.

## Usage

1. Select a mesh object and enter **Edit Mode**.
2. Open **3D View > Sidebar > Vertex Color**.
3. Choose a color with the picker or use a preset button.
4. Select the vertices you want to edit.
5. Click **Assign to Selected**.

If the named color attribute does not exist, the add-on creates it using the selected domain and storage type.

## Version

Current version: **1.0.1**

### 1.0.1

- Added Red / Green / Blue quick color preset buttons below Black / White.

## Repository layout

```text
quick-vertex-color-addon/
├── quick_vertex_color_addon/
│   └── __init__.py
├── .gitignore
└── README.md
```
