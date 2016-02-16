//
//  AppDelegate.h
//  PythonistaAppTemplate
//
//  Created by Ole Zorn on 15/02/16.
//  Copyright © 2016 omz-software. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface PAAppDelegate : UIResponder <UIApplicationDelegate>

@property (strong, nonatomic) UIWindow *window;

@end

@interface PythonInterpreter : NSObject

+ (id)sharedInterpreter;
- (void)run:(NSString *)script asFile:(NSString *)scriptPath;

@end

@interface PAEExtensionContext : NSObject

@property (retain) UIViewController *rootViewController;
@property (retain) UIApplication *app;
+ (instancetype)sharedContext;

@end
