# Get Slack attachment files.
Export attachment files in slack service.

# Environment

- OS: Windows 11 23H2
- python: 3.11.1
- pyinstaller: 6.6.0
- requests: 2.31.0
- urllib3: 2.2.1

# Export json file

check for [official site](https://slack.com/intl/ja-jp/help/articles/201658943-%E3%83%AF%E3%83%BC%E3%82%AF%E3%82%B9%E3%83%9A%E3%83%BC%E3%82%B9%E3%81%AE%E3%83%87%E3%83%BC%E3%82%BF%E3%82%92%E3%82%A8%E3%82%AF%E3%82%B9%E3%83%9D%E3%83%BC%E3%83%88%E3%81%99%E3%82%8B).

# How to use

```sh
# argv 1 : API key
# ex.)

$ python getSlackAttachmentFiles.py xoxp-XXXXXXXXXXXXX-XXXXXXXXXXXXX-XXXXXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# files/[msgid]_[file name].jpg
# files/[msgid]_[file name].pptx
# files/[msgid]_[file name].docx

```