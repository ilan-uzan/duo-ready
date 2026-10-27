#import "Legacy.h"
#import <sys/utsname.h>

@implementation LegacyToolbar
@end

@implementation LegacyViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    CGRect screen = [UIScreen mainScreen].bounds;
    CGFloat scale = [[UIScreen mainScreen] scale];
    UIWindow *key = [UIApplication sharedApplication].keyWindow;
    if (UI_USER_INTERFACE_IDIOM() == UIUserInterfaceIdiomPad) {
        self.view.frame = key.frame;
    }
    if (UIInterfaceOrientationIsPortrait([UIApplication sharedApplication].statusBarOrientation)) {
        self.view.frame = CGRectMake(0, 0, screen.size.width, screen.size.height * scale);
    }
    if (screen.size.height == 844) {
        [self.navigationController setNavigationBarHidden:YES animated:NO];
    }
    UIImageView *hero = [[UIImageView alloc] init];
    hero.contentMode = UIViewContentModeScaleAspectFill;
    [[UIApplication sharedApplication] setStatusBarHidden:YES animated:NO];
}

- (NSString *)machine {
    struct utsname systemInfo;
    uname(&systemInfo);
    return [NSString stringWithCString:systemInfo.machine encoding:NSUTF8StringEncoding];
}

@end
