Last verified: 2026-10-26 against the report; Xcode 27.1 (27A9275)

# The April 2027 iPhone Duo screenshot requirement: what Apple said, side by side

Two Apple pages announce the same deadline with different scope. Both quotes are reproduced exactly as captured in the report. Re-check the live pages before quoting them to a user as current; Apple edits these pages without a change log.

## The two statements

| | Apple Developer News, "Prepare and submit your apps for iPhone Duo", October 5, 2026 | App Store Connect Help, "Screenshot specifications" |
|---|---|---|
| URL | https://developer.apple.com/news/?id=kkphp5qo | https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications |
| Verbatim sentence | "Starting April 2027, any apps or games submitted will need to include screenshots for iPhone Duo." | "Starting in April 2027, screenshots will be required for any app using the iOS 27.1 SDK or later." |
| Scope as written | every submission | submissions built with the iOS 27.1 SDK or later |
| Which displays | not stated | not stated |
| Current status | Duo screenshots optional; uploading them earns the badge | Duo not listed under required sizes; required today: "iPhone with Dynamic Island (medium display)" and "iPad 13-inch" if applicable |

One research note recorded the news-post sentence with slightly different wording ("all submitted apps and games must include iPhone Duo screenshots"); the report's wording above is the one to quote, and the difference does not change the scope question.

## What is known

- The month is firm: April 2027 appears on both pages.
- The badge is immediate: "If you submit iPhone Duo screenshots, your App Store product page displays a badge indicating the app is optimized for iPhone Duo" ([news post](https://developer.apple.com/news/?id=kkphp5qo)); "When you submit iPhone Duo screenshots in App Store Connect, your App Store product page will display a badge to let people know your app is optimized for iPhone Duo" ([specs page](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)). The badge is named "Made for iPhone Duo" ([Apple Newsroom, Oct 22 2026](https://www.apple.com/newsroom/2026/10/developers-bring-incredible-new-app-experiences-to-iphone-duo/)).
- The sizes are fixed: outer 1398×2034 / 2034×1398, inner 2007×2853 / 2853×2007 ([specs page](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)).
- App previews are optional on the specs page and are not mentioned in the April 2027 sentences ([ASC app preview specifications](https://developer.apple.com/help/app-store-connect/reference/app-information/app-preview-specifications)).

## What is not known

| Question | State of the evidence |
|---|---|
| Does the rule cover iOS 27.0 SDK or older builds submitted after April 2027? | Conflict between the two pages. A developer asked exactly this on the forums, noting the news post and "October 15 App Store Connect release notes" say all apps while the specs page limits it to iOS 27.1 SDK apps; no Apple reply ([Apple Developer Forums 851106](https://developer.apple.com/forums/thread/851106)). |
| Is the item on Apple's official requirements calendar? | Not yet. The [Upcoming requirements](https://developer.apple.com/news/upcoming-requirements/) page, fetched 2026-10-26, does not list it; its latest entries are September 9, 2026 (iOS 13 minimum target) and April 28, 2026 (Xcode 26 / iOS 26 SDK minimum). |
| Will the inner set, the outer set, or both be required? | Not stated on either page (gap, report Appendix C). |
| Does "submitted" mean new apps only or every update? | Not stated. Press coverage split on this (third-party: [PPC Land](https://ppc.land/apple-forces-developers-to-add-iphone-duo-screenshots-from-april-2027/); [GameBusiness.jp](https://www.gamebusiness.jp/article/2026/10/06/28231.html)). |
| Will App Store Connect block the upload, or will App Review reject? | Not stated. |
| Will Duo move into the "required device sizes" list with a display-scaling fallback like other iPhone sizes? | Not stated; the page gives no fallback or scaling rule for Duo. |
| What does the App Store Review Guidelines text say about Duo screenshots? | The guidelines were not fetched. A forum poster paraphrases 2.3.3 as screenshots must show the app in use on that device, from the running app or simulator, not mockups ([Apple Developer Forums 851106](https://developer.apple.com/forums/thread/851106)). Quote as a paraphrase. |

## How to advise a user (inferred, labelled)

1. Treat the broad reading as the planning assumption. If Apple ends up enforcing "any apps or games submitted", a team that prepared only for the narrow reading is blocked in April; the reverse costs nothing.
2. Produce at minimum both portrait sets, outer 1398×2034 and inner 2007×2853, captured from the running app in the iPhone Duo simulator or on a device. Both sets cover the unanswered inner-versus-outer question, and simulator captures of the two displays land on those sizes exactly (third-party measurement; see `app-store-connect.md` section 8).
3. Upload them before April 2027. This also earns the "Made for iPhone Duo" badge now.
4. Do not upload mockups to beat the deadline; the badge is earned by upload alone (inferred) but Guideline 2.3.3 (paraphrased) requires the real app, and an unoptimized app is visibly letterboxed on the inner display ([Apple: Three steps](https://developer.apple.com/iphone-duo/prepare/) describes the compatibility tiers).
5. Tell the user what to watch: the two Apple pages above, the [Upcoming requirements](https://developer.apple.com/news/upcoming-requirements/) page, and [forum thread 851106](https://developer.apple.com/forums/thread/851106). If any of them changes, update this file's "Last verified" line.

## What not to say

- Do not say "only 27.1 SDK builds need Duo screenshots". That is one of two Apple statements.
- Do not say "every app needs Duo screenshots from April". That is the other one.
- Do not name a day in April; Apple gives only the month.
- Do not say which display's set is required; Apple has not said.
- Do not claim the App Review Guidelines contain Duo wording; they were not checked.
