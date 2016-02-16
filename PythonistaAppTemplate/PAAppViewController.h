//
//  ViewController.h
//  PythonistaAppTemplate
//
//  Created by Ole Zorn on 15/02/16.
//  Copyright © 2016 omz-software. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface PAAppViewController : UIViewController

@property (nonatomic, copy) NSString *scriptPath;

- (instancetype)initWithScriptPath:(NSString *)scriptPath;

@end

@interface OMTextColorTheme : NSObject

+ (instancetype)themeWithSelectionColor:(UIColor *)color;

@end

@interface OMTextView : UIView

@property (nonatomic, retain) OMTextColorTheme *colorTheme;
@property (nonatomic, retain) OMTextColorTheme *inactiveColorTheme;

@end

@interface PAStandaloneOutputView : UIView

@property (nonatomic, retain) UIColor *standardOutputColor;
@property (nonatomic, retain) UIColor *errorOutputColor;
@property (nonatomic, retain) OMTextView *consoleOutputTextView;
@property (nonatomic, retain) UITextField *promptTextField;
@property (nonatomic, assign) BOOL showsButtonControls;
@property (nonatomic, assign) BOOL shouldLinkifyURLs;
@property (nonatomic, copy) NSString *mainScriptPath;

@end
