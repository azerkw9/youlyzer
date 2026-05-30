from urllib.request import urlopen
from urllib.error import URLError

from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib import messages

from .forms import YouTubeURLForm, ContactForm
from .models import Ad
from .utils import (
    detect_url_type,
    fetch_video_info,
    fetch_channel_info,
)


def home(request):
    """Landing page with YouTube URL input form and ads."""
    form = YouTubeURLForm()
    home_ads = Ad.objects.filter(is_active=True, position='home')[:6]

    return render(request, 'home.html', {
        'form': form,
        'ads': home_ads,
    })


def analyze(request):
    """Process submitted YouTube URL and redirect to appropriate results page."""
    if request.method != 'POST':
        return redirect('home')

    form = YouTubeURLForm(request.POST)
    if not form.is_valid():
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, error)
        return redirect('home')

    url = form.cleaned_data['url']
    url_type = detect_url_type(url)

    if url_type == 'video':
        request.session['video_url'] = url
        return redirect('video_results')
    elif url_type == 'channel':
        request.session['channel_url'] = url
        return redirect('channel_results')
    else:
        messages.error(request, 'Could not determine if this is a video or channel URL. Please try again.')
        return redirect('home')


def video_results(request):
    """Display video analysis results: info, thumbnails."""
    url = request.GET.get('url') or request.session.get('video_url')
    if not url:
        messages.error(request, 'No YouTube URL provided.')
        return redirect('home')

    # Fetch video info
    video_data = fetch_video_info(url)

    if 'error' in video_data:
        messages.error(request, video_data['error'])
        return redirect('home')

    sidebar_ads = Ad.objects.filter(is_active=True, position='sidebar')[:4]

    return render(request, 'results.html', {
        'video': video_data,
        'url': url,
        'sidebar_ads': sidebar_ads,
    })


def channel_results(request):
    """Display channel info and latest videos."""
    url = request.GET.get('url') or request.session.get('channel_url')
    if not url:
        messages.error(request, 'No YouTube channel URL provided.')
        return redirect('home')

    channel_data = fetch_channel_info(url)

    if 'error' in channel_data:
        messages.error(request, channel_data['error'])
        return redirect('home')

    sidebar_ads = Ad.objects.filter(is_active=True, position='sidebar')[:4]

    return render(request, 'channel_results.html', {
        'channel': channel_data,
        'url': url,
        'sidebar_ads': sidebar_ads,
    })


def download_thumbnail(request):
    """Proxy download for YouTube thumbnails."""
    thumb_url = request.GET.get('url', '')
    filename = request.GET.get('filename', 'thumbnail.jpg')

    if not thumb_url:
        raise Http404

    try:
        response_data = urlopen(thumb_url, timeout=10)
        image_data = response_data.read()
        content_type = response_data.headers.get('Content-Type', 'image/jpeg')

        response = HttpResponse(image_data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except (URLError, Exception):
        raise Http404('Could not download thumbnail.')


def privacy(request):
    """Privacy policy page."""
    return render(request, 'privacy.html')


def about(request):
    """About us page."""
    return render(request, 'about.html')


def contact(request):
    """Contact page with form."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully! We\'ll get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


def compare(request):
    """Compare two YouTube videos side-by-side."""
    video1 = None
    video2 = None
    comparison = None
    url1 = ''
    url2 = ''

    if request.method == 'POST':
        url1 = request.POST.get('url1', '').strip()
        url2 = request.POST.get('url2', '').strip()

        if not url1 or not url2:
            messages.error(request, 'Please enter both video URLs.')
            return render(request, 'compare.html', {'url1': url1, 'url2': url2})

        # Fetch both videos
        video1 = fetch_video_info(url1)
        video2 = fetch_video_info(url2)

        if 'error' in video1:
            messages.error(request, f'Video 1: {video1["error"]}')
            return render(request, 'compare.html', {'url1': url1, 'url2': url2})

        if 'error' in video2:
            messages.error(request, f'Video 2: {video2["error"]}')
            return render(request, 'compare.html', {'url1': url1, 'url2': url2})

        # Compute engagement rates
        def _engagement_rate(video_data):
            views = video_data.get('view_count_raw')
            likes = video_data.get('like_count_raw')
            if views and likes and views > 0:
                return round((likes / views) * 100, 2)
            return None

        eng1 = _engagement_rate(video1)
        eng2 = _engagement_rate(video2)
        video1['engagement_rate'] = eng1
        video2['engagement_rate'] = eng2

        # Build comparison metrics
        def _winner(val1, val2, higher_is_better=True):
            """Return 1, 2, or 0 (tie/unknown)."""
            if val1 is None or val2 is None:
                return 0
            if val1 == val2:
                return 0
            if higher_is_better:
                return 1 if val1 > val2 else 2
            return 1 if val1 < val2 else 2

        comparison = {
            'views': _winner(video1.get('view_count_raw'), video2.get('view_count_raw')),
            'likes': _winner(video1.get('like_count_raw'), video2.get('like_count_raw')),
            'engagement': _winner(eng1, eng2),
        }

    return render(request, 'compare.html', {
        'video1': video1,
        'video2': video2,
        'comparison': comparison,
        'url1': url1,
        'url2': url2,
    })
