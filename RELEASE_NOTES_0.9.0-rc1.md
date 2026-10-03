# Media Downloader 0.9.0-rc1

Internal Release Candidate. Product polish and local technical validation do not authorize public distribution.

Technical Release Gate: PASS
Clean Machine Gate: NOT TESTED
Public Distribution Gate: NEEDS LEGAL REVIEW

## Capabilities

Save the media quality actually available from the source, with separate audio selection and stream-copy merge.
Dynamic quality options include verified 1080P/4K/8K, 8K60 and HDR metadata; there is no fixed 4K/8K ceiling.
Audio Only, partial-download resume, Cancel/Retry, cookies.txt, HTTP/SOCKS5/SOCKS5H remain supported.
The Windows Portable and Installer bundle yt-dlp, FFmpeg/FFprobe and QuickJS.

The candidate provides English and Simplified Chinese throughout the product interface,
light/dark/system themes, a short first-launch setup, local About/Help, clearer errors and codec compatibility hints.
Version information uses app/version.py. Third-party attribution, license texts and source/relink materials remain supplied.

## Known limitations

1. Chrome/Edge browser cookie extraction on Windows is experimental; cookies.txt is the supported authentication path. Firefox is best effort.
2. YouTube upstream behavior may cause HTTP 403 or authentication/challenge failures. Runtime support does not guarantee access.
3. Some older media players do not support AV1/VP9/Opus. The application does not silently lower quality.
4. Independent clean Windows Portable/Installer acceptance is pending. Development-host checks do not substitute for it.
5. Public distribution licensing review remains pending, including the previously recorded Qt/PySide6/Microsoft terms and separate Inno commercial review.

Do not share cookies.txt. Only download content you have the right to save or use.
No telemetry or automatic log upload is added. This candidate is unsigned and is not a stable v1.0 release.
