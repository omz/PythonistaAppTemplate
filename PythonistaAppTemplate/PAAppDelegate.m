//
//  AppDelegate.m
//  PythonistaAppTemplate
//
//  Created by Ole Zorn on 15/02/16.
//  Copyright © 2016 omz-software. All rights reserved.
//

#import "PAAppDelegate.h"
#import "PAAppViewController.h"

@interface PAAppDelegate () <UIGestureRecognizerDelegate>

@end

@implementation PAAppDelegate


- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions
{
	NSString *scriptPath = [self copyScriptResourcesIfNeeded];
	
	self.window = [[UIWindow alloc] initWithFrame:[[UIScreen mainScreen] bounds]];
	self.window.rootViewController = [[PAAppViewController alloc] initWithScriptPath:scriptPath];
	[self.window makeKeyAndVisible];
	
	//This gesture recognizer suppresses the two-finger swipe-down gesture that can be used to dismiss
	//ui views without title bar in the main app. In a standalone app, this behavior is usually not desirable.
	UISwipeGestureRecognizer *swipeRecognizer = [[UISwipeGestureRecognizer alloc] initWithTarget:nil action:nil];
	swipeRecognizer.numberOfTouchesRequired = 2;
	swipeRecognizer.direction = UISwipeGestureRecognizerDirectionDown;
	swipeRecognizer.delegate = self;
	[self.window addGestureRecognizer:swipeRecognizer];
	
	//This is required for the ui module to work correctly:
	[[PAEExtensionContext sharedContext] setApp:application];
	[[PAEExtensionContext sharedContext] setRootViewController:self.window.rootViewController];
	
	//Run the main script:
	if (scriptPath) {
		NSString *script = [NSString stringWithContentsOfFile:scriptPath encoding:NSUTF8StringEncoding error:NULL];
		if (script) {
			[[PythonInterpreter sharedInterpreter] run:script asFile:scriptPath];
		} else {
			NSLog(@"Could not load main.py (make sure its encoding is UTF-8)");
		}
	} else {
		NSLog(@"Could not find main.py");
	}
	return YES;
}

- (NSString *)copyScriptResourcesIfNeeded
{
	//Copy files from <Main Bundle>/Scripts to ~/Library/Application Support/PythonistaScript.
	//Files that are already there (and up-to-date) are skipped.
	
	//The script is not run directly from the main bundle because its directory wouldn't be writable then,
	//which would require changes in scripts that produce files.
	NSString *bundledScriptDirectory = [[[NSBundle mainBundle] resourcePath] stringByAppendingPathComponent:@"Script"];
	NSString *appSupportDirectory = [NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory, NSUserDomainMask, YES) firstObject];
	NSString *writableScriptDirectory = [appSupportDirectory stringByAppendingPathComponent:@"PythonistaScript"];
	NSFileManager *fm = [NSFileManager defaultManager];
	[fm createDirectoryAtPath:writableScriptDirectory withIntermediateDirectories:YES attributes:nil error:NULL];
	
	NSArray *scriptResources = [fm contentsOfDirectoryAtPath:bundledScriptDirectory error:NULL];
	for (NSString *filename in scriptResources) {
		NSString *fullPath = [bundledScriptDirectory stringByAppendingPathComponent:filename];
		NSString *destPath = [writableScriptDirectory stringByAppendingPathComponent:filename];
		NSDate *srcModificationDate = [[fm attributesOfItemAtPath:fullPath error:NULL] fileModificationDate];
		NSDate *destModificationDate = [[fm attributesOfItemAtPath:destPath error:NULL] fileModificationDate];
		if (![destModificationDate isEqual:srcModificationDate]) {
			[fm removeItemAtPath:destPath error:NULL];
			[fm copyItemAtPath:fullPath toPath:destPath error:NULL];
		}
	}
	NSString *mainScriptFile = [writableScriptDirectory stringByAppendingPathComponent:@"main.py"];
	if (![fm fileExistsAtPath:mainScriptFile]) {
		//If there is no main.py, find the first *.py file...
		mainScriptFile = nil;
		for (NSString *filename in [fm contentsOfDirectoryAtPath:writableScriptDirectory error:NULL]) {
			if ([[[filename pathExtension] lowercaseString] isEqualToString:@"py"]) {
				mainScriptFile = [writableScriptDirectory stringByAppendingPathComponent:filename];
				break;
			}
		}
	}
	return mainScriptFile;
}

- (BOOL)gestureRecognizer:(UIGestureRecognizer *)gestureRecognizer shouldBeRequiredToFailByGestureRecognizer:(UIGestureRecognizer *)otherGestureRecognizer
{
	if ([otherGestureRecognizer isKindOfClass:[UISwipeGestureRecognizer class]]) {
		UISwipeGestureRecognizer *otherSwipeRecognizer = (UISwipeGestureRecognizer *)otherGestureRecognizer;
		if (otherSwipeRecognizer.numberOfTouchesRequired == 2 && otherSwipeRecognizer.direction == UISwipeGestureRecognizerDirectionDown) {
			return YES;
		}
	}
	return NO;
}

@end
