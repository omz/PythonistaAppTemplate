# Xcode Template for Pythonista

A current version can be found at https://www.dropbox.com/s/dl/5l94m0xjbot5je0/Pythonista3AppTemplate.zip

This template allows you to package Python 2 scripts written in [Pythonista for iOS](http://omz-software.com/pythonista) as standalone apps that can be built using Xcode.  This template does not currently support Python 3.

## Using the Template

First off, you obviously need to download Xcode [from the App Store](https://itunes.apple.com/en/app/xcode/id497799835?mt=12), if you haven't already.

This is enough to build your app for the iOS simulator, but to get it running on an actual device, you need at least an Apple ID (for running on your own device) or a paid Developer Program membership (for distributing through the App Store). The details of how to set up code signing and provisioning profiles are beyond the scope of this document, but they're not different from what you need to do to build any other iOS app, and you can find plenty of information about the process online.

The template just runs a default "Hello World" script by default. To make it run your own script, just put it in the "Script" folder of the template, and rename it to "main.py" if necessary. You can also put additional resources there, e.g. pyui files, images, etc.

## Customization

### Changing the App's Name, Icon, and Launch Screen

Before changing the app's name and icon, you should usually change its *bundle identifier*, so that it is unique:

Open the Xcode project, and select the first entry in the project navigator (PythonistaAppTemplate). Select the "My App" target in the left pane, and enter something unique in the "Bundle Identifier" field. The bundle identifier should be in "reverse domain" notation, e.g. something like com.mycompany.myapp.

To change the name that is shown below the icon on the homescreen, you can simply rename the target ("My App" by default) by double-clicking on it.

To change the app's icon, select Assets.xcassets in the project navigator, then select the "AppIcon" image set and replace the various icon sizes via drag'n'drop from the Finder. Not all the icon sizes are strictly necessary (the Spotlight and Settings icon sizes are optional). If you don't have your own icon in these sizes, you should remove the default icons though.

The app's launch screen is shown during its launch from the home screen (as a placeholder while the app is loading). It is defined in LaunchScreen.storyboard, and you can edit it directly in Xcode, using its Interface Builder.

### Split Screen, Orientations, and Status Bar

When you run the app on an iPad, it will support split-screen multitasking by default.

You may want to turn this off if

* Your custom UI isn't (yet) prepared to adapt to various sizes.
* You've written a game (or something similar) that always requires the full screen.
* You want to lock the orientation of your UI/scene to portrait or landscape – the `orientations` argument for `ui.View.present()` and `scene.run()` is ignored if split-screen support is enabled, and you cannot prevent auto-rotation.

If any of the above applies to you, simply select the target ("My App" by default) and activate the "Requires full screen" checkbox in the "General" tab.

Right above that checkbox are controls for changing the style of the status bar (black/white) and for hiding it entirely.

### Changing Colors

After the app has launched, it shows a white background on which console output etc. will appear.

If your script has its own UI, and doesn't actually rely on console output, you may at least want to change the background color of this view, but you can also change the console's default text colors.

To adjust these colors, you have to edit `PAAppViewController.m`. The code is Objective-C, but even if you don't know anything about that, it should be easy to adjust the RGB values. Just keep in mind that the range for each value is 0.0 to 1.0 (and not 0 to 255 as you may expect).

### Debug Controls

By default, the console output area also contains "Run" and "Clear" buttons. The "Run" button simply restarts your main script after it has finished running. This can be useful for console-based scripts or during development because you don't have to restart the entire app to run your script again. For games, UI-based scripts, and for distribution, you may want to hide these buttons though. To do that, simply set the `showButtons` variable in `PAAppViewController.m` to `NO`.

## Special Considerations for `scene` and `ui` Scripts

When you run a scene or present a UI in Pythonista, the interface contains a *Close* button by default, so that you can continue editing your code without restarting the entire app.

In a standalone app, you typically don't want these buttons though, so there are ways to get rid of them:

When you present a `ui.View`, you can pass `hide_title_bar=True` to the `present()` method. You may also want to pass `animated=False` in a standalone app, which suppresses the sliding animation.

For presenting a `Scene`, don't use the `run` function. Instead, embed a `SceneView` in a regular `ui.View`, and present that using `hide_title_bar=False`. Example:

	from scene import *
	import ui

	class MyScene (Scene):
		pass

	my_scene = MyScene()
	# Instead of...
	# run(MyScene())

	# ..use:
	main_view = ui.View()
	scene_view = SceneView(frame=main_view.bounds, flex='WH')
	main_view.add_subview(scene_view)
	scene_view.scene = my_scene
	main_view.present(hide_title_bar=True, animated=False)

## Reducing the Size of the App

When you build your project from the unmodified template, the resulting app will be quite large, but there are various ways to reduce its footprint easily.

* If your script doesn't use all of Pythonista's built-in images and sound effects, you can remove those you don't need from `PythonistaKit.framework`. The corresponding files are located in the *Media* directory.

* You can remove packages and modules you don't need from the standard library in `PythonistaKit.framework/pylib` and `PythonistaKit.framework/pylib_ext`. For example, by removing `matplotlib` and `sympy` from `pylib_ext`, you can save about 20 MB.
