import unittest

from backend.video_url import INVALID_VIDEO_URL_MESSAGE, normalize_video_url


class VideoUrlNormalizationTest(unittest.TestCase):
    def test_keeps_clean_url_unchanged(self) -> None:
        url = "https://v.douyin.com/IgmR0ntdXbY/"
        self.assertEqual(normalize_video_url(url), url)

    def test_strips_mailto_suffix_from_shortcut_share_text(self) -> None:
        raw_url = "https://v.douyin.com/Xz6xQlScdQA/mailto:N@w.sr"
        self.assertEqual(
            normalize_video_url(raw_url),
            "https://v.douyin.com/Xz6xQlScdQA/",
        )

    def test_extracts_url_from_douyin_share_copywriting(self) -> None:
        raw_url = "https://v.douyin.com/Q61HfJgDQmw/ :6pm 08/11 lPk:/ P@k.CU "
        self.assertEqual(
            normalize_video_url(raw_url),
            "https://v.douyin.com/Q61HfJgDQmw/",
        )

    def test_rejects_invalid_non_url_payload(self) -> None:
        with self.assertRaisesRegex(ValueError, INVALID_VIDEO_URL_MESSAGE):
            normalize_video_url("1")


if __name__ == "__main__":
    unittest.main()
