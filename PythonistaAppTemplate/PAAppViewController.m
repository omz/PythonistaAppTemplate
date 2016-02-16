//
//  ViewController.m
//  PythonistaAppTemplate
//
//  Created by Ole Zorn on 15/02/16.
//  Copyright © 2016 omz-software. All rights reserved.
//

#import "PAAppViewController.h"

@implementation PAAppViewController

- (instancetype)initWithScriptPath:(NSString *)scriptPath
{
	self = [super initWithNibName:nil bundle:nil];
	if (self) {
		_scriptPath = [scriptPath copy];
	}
	return self;
}

- (void)viewDidLoad 
{
	[super viewDidLoad];
	
	// === You can customize these colors to change the appearance of the console output:
	UIColor *backgroundColor = [UIColor colorWithRed:1.0 green:1.0 blue:1.0 alpha:1.0];
	UIColor *standardOutputTextColor = [UIColor colorWithRed:0.2 green:0.2 blue:0.2 alpha:1.0];
	UIColor *errorOutputTextColor = [UIColor colorWithRed:0.8 green:0.0 blue:0.0 alpha:1.0];
	UIColor *textSelectionTintColor = [UIColor colorWithRed:0.0 green:0.48 blue:1.0 alpha:1.0];
	UIColor *buttonTintColor = [UIColor colorWithRed:0.0 green:0.48 blue:1.0 alpha:1.0];
	
	// === If you don't want the run/clear buttons to be visible, set this to NO:
	BOOL showButtons = YES;
	
	// === The console output turns URLs into tappable links by default, set to NO to turn this off:
	BOOL linkifyURLs = YES;
	
	// ===
	
	self.view.backgroundColor = backgroundColor;
	PAStandaloneOutputView *outputView = [[PAStandaloneOutputView alloc] initWithFrame:self.view.bounds];
	outputView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
	outputView.standardOutputColor = standardOutputTextColor;
	outputView.errorOutputColor = errorOutputTextColor;
	outputView.consoleOutputTextView.backgroundColor = backgroundColor;
	outputView.promptTextField.backgroundColor = backgroundColor;
	OMTextColorTheme *textColorTheme = [OMTextColorTheme themeWithSelectionColor:textSelectionTintColor];
	outputView.consoleOutputTextView.colorTheme = textColorTheme;
	outputView.consoleOutputTextView.inactiveColorTheme = textColorTheme;
	outputView.tintColor = buttonTintColor;
	outputView.showsButtonControls = showButtons;
	outputView.shouldLinkifyURLs = linkifyURLs;
	outputView.mainScriptPath = self.scriptPath;
	[self.view addSubview:outputView];
}

@end
