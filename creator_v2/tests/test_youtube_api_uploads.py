import pytest

from factory.youtube_api import HttpYouTube, PublishError


class FakeHttpYouTube(HttpYouTube):
    def __init__(self, playlist, search=None, videos=None):
        self.playlist = playlist
        self.search = search or {}
        self.videos = videos or {}
        self.calls = []

    def _json(self, method, path, params, payload=None):
        self.calls.append((path, params.copy()))
        if path == "channels":
            return {"items": [{"id": "channel", "contentDetails": {
                "relatedPlaylists": {"uploads": "uploads"}}}]}
        if path == "playlistItems":
            return self.playlist[params.get("pageToken")]
        if path == "search":
            return self.search.get((params["videoDuration"], params.get("pageToken")), {})
        if path == "videos":
            return {"items": [self.videos[vid] for vid in reversed(params["id"].split(","))
                              if vid in self.videos]}
        raise AssertionError(path)


def playlist(*ids, next_page=None):
    return {"items": [{"contentDetails": {"videoId": vid}} for vid in ids],
            "nextPageToken": next_page}


def search(*ids, next_page=None):
    return {"items": [{"id": {"videoId": vid}} for vid in ids], "nextPageToken": next_page}


def video(vid, duration="PT4M", privacy="public"):
    return {"id": vid, "snippet": {"title": vid}, "status": {"privacyStatus": privacy},
            "contentDetails": {"duration": duration}}


def test_duplicate_ids_across_pages_do_not_consume_limit():
    api = FakeHttpYouTube({None: playlist("a", "b", next_page="p2"),
                           "p2": playlist("b", "c", next_page="p3"),
                           "p3": playlist("d")}, videos={v: video(v) for v in "abcd"})
    assert [v["id"] for v in api.list_uploads(3)] == ["a", "b", "c"]
    assert [p.get("pageToken") for path, p in api.calls if path == "playlistItems"] == [None, "p2"]


def test_end_of_playlist_and_repeated_token():
    api = FakeHttpYouTube({None: playlist("a")}, videos={"a": video("a")})
    assert [v["id"] for v in api.list_uploads(100)] == ["a"]
    assert len([1 for path, _ in api.calls if path == "playlistItems"]) == 1
    cyclic = FakeHttpYouTube({None: playlist("a", next_page="p"), "p": playlist("a", next_page="p")})
    with pytest.raises(PublishError, match="repeated page token"):
        cyclic.list_uploads(100)


def test_merge_paginated_search_and_filter_public_duration():
    api = FakeHttpYouTube(
        {None: playlist("a", "private", "short", "boundary", next_page="p"),
         "p": playlist("a", "missing")},
        {("medium", None): search("a", "b", next_page="next"),
         ("medium", "next"): search("c", "private"), ("long", None): search("c", "d")},
        {"a": video("a"), "private": video("private", privacy="private"),
         "short": video("short", "PT3M"), "boundary": video("boundary", "PT3M1S"),
         "b": video("b", "PT1H"), "c": video("c", "P1DT1S"), "d": video("d", "PT20M1S")})
    assert [v["id"] for v in api.list_long_videos()] == ["a", "boundary", "b", "c", "d"]
    calls = [p for path, p in api.calls if path == "search"]
    assert [(p["videoDuration"], p.get("pageToken")) for p in calls] == [
        ("medium", None), ("medium", "next"), ("long", None)]
    assert all(p["channelId"] == "channel" and p["type"] == "video" for p in calls)
    assert all(p["part"] == "snippet,status,contentDetails" for path, p in api.calls if path == "videos")
