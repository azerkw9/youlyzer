"""
Utility functions for YouTube data fetching via the official YouTube Data API v3.
Requires a YOUTUBE_API_KEY in settings (from .env).
"""
import re
import logging
import isodate
from datetime import datetime

from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


def _get_youtube_client():
    """Build and return a YouTube Data API v3 client."""
    return build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)


def detect_url_type(url):
    """
    Determine if a YouTube URL points to a video or a channel.
    Returns 'video', 'channel', or None.
    """
    video_patterns = [
        r'(https?://)?(www\.)?youtube\.com/watch\?v=([\w-]+)',
        r'(https?://)?(www\.)?youtube\.com/shorts/([\w-]+)',
        r'(https?://)?(www\.)?youtu\.be/([\w-]+)',
    ]
    channel_patterns = [
        r'(https?://)?(www\.)?youtube\.com/(channel|c|user|@)([\w/-]+)',
    ]

    for pattern in video_patterns:
        if re.match(pattern, url):
            return 'video'

    for pattern in channel_patterns:
        if re.match(pattern, url):
            return 'channel'

    return None


def extract_video_id(url):
    """Extract the video ID from a YouTube URL."""
    patterns = [
        r'(?:v=|/shorts/|youtu\.be/)([\w-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def extract_channel_identifier(url):
    """
    Extract channel identifier from a YouTube URL.
    Returns a tuple (id_type, identifier) where id_type is 'id', 'forUsername', or 'handle'.
    """
    # Channel ID: /channel/UC...
    match = re.search(r'youtube\.com/channel/(UC[\w-]+)', url)
    if match:
        return ('id', match.group(1))

    # Handle: /@handle
    match = re.search(r'youtube\.com/@([\w.-]+)', url)
    if match:
        return ('handle', match.group(1))

    # Legacy /user/username
    match = re.search(r'youtube\.com/user/([\w.-]+)', url)
    if match:
        return ('forUsername', match.group(1))

    # Legacy /c/customname
    match = re.search(r'youtube\.com/c/([\w.-]+)', url)
    if match:
        return ('handle', match.group(1))

    return (None, None)


def _format_duration(iso_duration):
    """Convert ISO 8601 duration (PT4M13S) to human-readable (4:13)."""
    try:
        delta = isodate.parse_duration(iso_duration)
        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        if hours > 0:
            return f'{hours}:{minutes:02d}:{seconds:02d}'
        else:
            return f'{minutes}:{seconds:02d}'
    except Exception:
        return iso_duration or 'N/A'


def _format_count(count):
    """Format a numeric count with commas, or return N/A."""
    if count is None:
        return 'N/A'
    try:
        return f'{int(count):,}'
    except (ValueError, TypeError):
        return str(count)


def _format_date(date_str):
    """Format an ISO date string (2009-10-25T06:57:33Z) to YYYY/MM/DD."""
    if not date_str:
        return 'Unknown'
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y/%m/%d')
    except Exception:
        return date_str[:10] if len(date_str) >= 10 else date_str


def fetch_video_info(url):
    """
    Fetch comprehensive video information using the YouTube Data API v3.
    Returns a dict with video metadata, channel info, and thumbnail URLs.
    """
    video_id = extract_video_id(url)
    if not video_id:
        return {'error': 'Could not extract video ID from the URL.'}

    try:
        youtube = _get_youtube_client()

        # Fetch video details
        video_response = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id,
        ).execute()

        items = video_response.get('items', [])
        if not items:
            return {'error': 'Video not found. It may be private or unavailable.'}

        video = items[0]
        snippet = video.get('snippet', {})
        content_details = video.get('contentDetails', {})
        statistics = video.get('statistics', {})

        # Duration
        duration_formatted = _format_duration(content_details.get('duration', ''))

        # Upload date
        upload_date = _format_date(snippet.get('publishedAt', ''))

        # Counts
        view_count = statistics.get('viewCount')
        like_count = statistics.get('likeCount')

        # Build thumbnail list with all available qualities
        thumbnails_data = snippet.get('thumbnails', {})
        quality_order = [
            ('default', 'Default'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('standard', 'Standard'),
            ('maxres', 'Max Resolution'),
        ]
        thumbnails = []
        for key, label in quality_order:
            thumb = thumbnails_data.get(key)
            if thumb:
                w = thumb.get('width', '?')
                h = thumb.get('height', '?')
                thumbnails.append({
                    'url': thumb['url'],
                    'quality': f'{label} ({w}×{h})',
                    'key': key,
                })

        # Channel info — fetch channel details for avatar and subscriber count
        channel_id = snippet.get('channelId', '')
        channel_name = snippet.get('channelTitle', 'Unknown')
        channel_avatar = None
        channel_follower_count = None
        channel_created_date = None
        channel_video_count = None
        channel_view_count = None

        if channel_id:
            try:
                ch_response = youtube.channels().list(
                    part='snippet,statistics',
                    id=channel_id,
                ).execute()
                ch_items = ch_response.get('items', [])
                if ch_items:
                    ch = ch_items[0]
                    ch_snippet = ch.get('snippet', {})
                    ch_stats = ch.get('statistics', {})
                    channel_avatar = ch_snippet.get('thumbnails', {}).get('default', {}).get('url')
                    channel_follower_count = ch_stats.get('subscriberCount')
                    channel_created_date = _format_date(ch_snippet.get('publishedAt', ''))
                    channel_video_count = ch_stats.get('videoCount')
                    channel_view_count = ch_stats.get('viewCount')
            except Exception as e:
                logger.warning(f'Could not fetch channel details: {e}')

        result = {
            'type': 'video',
            'video_id': video_id,
            'title': snippet.get('title', 'Unknown Title'),
            'description': (snippet.get('description', '') or '')[:500],
            'duration': duration_formatted,
            'view_count': _format_count(view_count),
            'view_count_raw': int(view_count) if view_count else None,
            'like_count': _format_count(like_count),
            'like_count_raw': int(like_count) if like_count else None,
            'upload_date': upload_date,
            'tags': snippet.get('tags', []) or [],
            'categories': [],  # Would need a separate categoryId lookup
            'channel_name': channel_name,
            'channel_id': channel_id,
            'channel_url': f'https://www.youtube.com/channel/{channel_id}' if channel_id else '',
            'channel_follower_count': channel_follower_count,
            'channel_avatar': channel_avatar,
            'channel_created_date': channel_created_date,
            'channel_video_count': channel_video_count,
            'channel_view_count': channel_view_count,
            'thumbnails': thumbnails,
        }

        # Fetch category name if categoryId is present
        category_id = snippet.get('categoryId')
        if category_id:
            try:
                cat_response = youtube.videoCategories().list(
                    part='snippet',
                    id=category_id,
                ).execute()
                cat_items = cat_response.get('items', [])
                if cat_items:
                    result['categories'] = [cat_items[0]['snippet']['title']]
            except Exception:
                pass

        return result

    except HttpError as e:
        logger.error(f'YouTube API error: {e}')
        status = e.resp.status if hasattr(e, 'resp') else 0
        if status == 403:
            return {'error': 'YouTube API quota exceeded. Please try again later.'}
        elif status == 404:
            return {'error': 'Video not found.'}
        else:
            return {'error': 'Could not fetch video data. Please check the URL and try again.'}
    except Exception as e:
        logger.error(f'Error fetching video info: {e}')
        return {'error': 'Could not fetch video data. Please check the URL and try again.'}


def fetch_channel_info(url):
    """
    Fetch channel information and latest videos using the YouTube Data API v3.
    Returns a dict with channel metadata and recent video list.
    """
    id_type, identifier = extract_channel_identifier(url)
    if not identifier:
        return {'error': 'Could not extract channel identifier from the URL.'}

    try:
        youtube = _get_youtube_client()

        # Step 1: Resolve channel ID
        channel_id = None

        if id_type == 'id':
            channel_id = identifier
        elif id_type == 'forUsername':
            ch_response = youtube.channels().list(
                part='id',
                forUsername=identifier,
            ).execute()
            items = ch_response.get('items', [])
            if items:
                channel_id = items[0]['id']
        elif id_type == 'handle':
            # Use search to resolve handle to channel ID
            search_response = youtube.search().list(
                part='snippet',
                q=f'@{identifier}',
                type='channel',
                maxResults=1,
            ).execute()
            items = search_response.get('items', [])
            if items:
                channel_id = items[0]['snippet']['channelId']

        if not channel_id:
            return {'error': 'Channel not found. Please check the URL.'}

        # Step 2: Fetch channel details
        ch_response = youtube.channels().list(
            part='snippet,statistics,contentDetails',
            id=channel_id,
        ).execute()

        ch_items = ch_response.get('items', [])
        if not ch_items:
            return {'error': 'Channel not found.'}

        channel = ch_items[0]
        ch_snippet = channel.get('snippet', {})
        ch_stats = channel.get('statistics', {})

        # Format subscriber count
        sub_count_raw = ch_stats.get('subscriberCount')
        if sub_count_raw is not None:
            sub_count = int(sub_count_raw)
            if sub_count >= 1_000_000:
                sub_formatted = f'{sub_count / 1_000_000:.1f}M'
            elif sub_count >= 1_000:
                sub_formatted = f'{sub_count / 1_000:.1f}K'
            else:
                sub_formatted = f'{sub_count:,}'
        else:
            sub_count = None
            sub_formatted = 'Hidden'

        # Channel avatar
        avatar = ch_snippet.get('thumbnails', {}).get('medium', {}).get('url')
        if not avatar:
            avatar = ch_snippet.get('thumbnails', {}).get('default', {}).get('url')

        # Total videos
        total_videos = ch_stats.get('videoCount', 'N/A')

        # Step 3: Fetch latest videos from the channel's uploads playlist
        videos = []
        uploads_playlist_id = (
            channel.get('contentDetails', {})
            .get('relatedPlaylists', {})
            .get('uploads')
        )

        if uploads_playlist_id:
            try:
                playlist_response = youtube.playlistItems().list(
                    part='snippet',
                    playlistId=uploads_playlist_id,
                    maxResults=12,
                ).execute()

                video_ids = []
                for item in playlist_response.get('items', []):
                    vid_id = item['snippet']['resourceId']['videoId']
                    video_ids.append(vid_id)

                # Fetch video details for duration and view counts
                if video_ids:
                    videos_response = youtube.videos().list(
                        part='snippet,contentDetails,statistics',
                        id=','.join(video_ids),
                    ).execute()

                    for vid in videos_response.get('items', []):
                        vid_id = vid['id']
                        vid_snippet = vid.get('snippet', {})
                        vid_stats = vid.get('statistics', {})
                        vid_content = vid.get('contentDetails', {})

                        # Parse duration to seconds for template filter
                        duration_secs = None
                        try:
                            delta = isodate.parse_duration(vid_content.get('duration', ''))
                            duration_secs = int(delta.total_seconds())
                        except Exception:
                            pass

                        vid_view_count = vid_stats.get('viewCount')

                        videos.append({
                            'id': vid_id,
                            'title': vid_snippet.get('title', 'Untitled'),
                            'url': f'https://www.youtube.com/watch?v={vid_id}',
                            'thumbnail': vid_snippet.get('thumbnails', {}).get('medium', {}).get('url',
                                         f'https://img.youtube.com/vi/{vid_id}/mqdefault.jpg'),
                            'duration': duration_secs,
                            'view_count': int(vid_view_count) if vid_view_count else None,
                        })

            except Exception as e:
                logger.warning(f'Could not fetch channel videos: {e}')

        result = {
            'type': 'channel',
            'channel_name': ch_snippet.get('title', 'Unknown'),
            'channel_id': channel_id,
            'channel_url': f'https://www.youtube.com/channel/{channel_id}',
            'description': (ch_snippet.get('description', '') or '')[:500],
            'subscriber_count': sub_formatted,
            'subscriber_count_raw': sub_count,
            'total_videos': total_videos,
            'avatar': avatar,
            'videos': videos,
        }

        return result

    except HttpError as e:
        logger.error(f'YouTube API error: {e}')
        status = e.resp.status if hasattr(e, 'resp') else 0
        if status == 403:
            return {'error': 'YouTube API quota exceeded. Please try again later.'}
        elif status == 404:
            return {'error': 'Channel not found.'}
        else:
            return {'error': 'Could not fetch channel data. Please check the URL and try again.'}
    except Exception as e:
        logger.error(f'Error fetching channel info: {e}')
        return {'error': 'Could not fetch channel data. Please check the URL and try again.'}
