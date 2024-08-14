# Ulauncher Window Manager

An extension for organizing and controlling your open windows.![App Cover](https://github.com/gnikolaos/ulauncher-window-manager/blob/main/images/wm-cover.jpg?raw=true)

Work in Progress: Expect Frequent Updates.

This extension is currently targeting GNOME. To use it, you need to have the [Window Calls GNOME extension](https://extensions.gnome.org/extension/4724/window-calls/) installed.
As the extension evolves and reaches a stable state, I plan to abstract its functionality to support additional desktop environments.


## Demo
![App Demo](https://github.com/gnikolaos/ulauncher-window-manager/blob/main/images/wm-demo.gif?raw=true)


## Features

- Move and Resize Up/Down/Left/Right: Move the focused window to the edge of the screen in any direction.
- Move and Resize Center/Center Half/Center Three Fourths: Move and Resize the focused window to the center of the screen.
- Move and Resize First Fourth/First Three Fourths/Last Fourth/Last Three Fourths: Move and Resize the focused window to the sides of the screen.
- Almost Maximize: Resize the focused window to cover 96% of the screen's width and height, leaving a 2% margin around all sides.
- Maximize: Maximize the focused window to fit the screen.
- Unmaximize: Restore the focused window to its previous state.


## How it works (primarily for extension developers)

This paragraph is copied from https://github.com/friday/ulauncher-gnome-settings and modified to apply to this extension.

Ulauncher extensions can add multiple keywords, but not apps.

Keywords and apps have different workflows. Both have searchable names (like "Google Translate"), but triggering it will have different behavior. Triggering an app name will launch the app. Triggering the keyword name will replace your input with the keyword followed by a space, waiting for you to type an argument.

In addition to this, keywords can be typed directly. This skips the fuzzy search step.

To avoid the additional step and "launch" instead, this extension uses default keywords that look like names. That way if you select "Top Half" it will replace your input with "Top Half " (not something else like "disp "). This will show briefly before the KeywordQueryEvent-handler closes Ulauncher and starts the settings app. It looks a lot less hacky this way, and you may not even think about it.

Instead of spaces it's using an untypable blank character with the same width. Keywords can't contain spaces, since space is the separator between the keyword and the arguments. As a bonus, since it can't be typed with a keyboard it can only launch via search (like apps).

Users can override keywords in Ulauncher's preferences (hence the "default" in `default_value`). If you do this, this extension will not work as intended, but you may want to delete keywords completely if you don't want a specific panel to appear in search.


## Contributing

Contributions are always welcome!

