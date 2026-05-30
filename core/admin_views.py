"""
Custom admin dashboard views for managing ads and contact messages.
Protected by @staff_member_required.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from .models import Ad, ContactMessage
from .forms import AdForm


@staff_member_required(login_url='/admin/login/')
def dashboard(request):
    """Admin dashboard with stats overview."""
    total_messages = ContactMessage.objects.count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    total_ads = Ad.objects.count()
    active_ads = Ad.objects.filter(is_active=True).count()

    recent_messages = ContactMessage.objects.all()[:5]

    return render(request, 'admin/dashboard.html', {
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'total_ads': total_ads,
        'active_ads': active_ads,
        'recent_messages': recent_messages,
    })


# --- Ad Management ---

@staff_member_required(login_url='/admin/login/')
def ads_list(request):
    """List all advertisements."""
    ads = Ad.objects.all()
    return render(request, 'admin/ads_list.html', {'ads': ads})


@staff_member_required(login_url='/admin/login/')
def ad_create(request):
    """Create a new ad."""
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ad created successfully.')
            return redirect('admin_ads_list')
    else:
        form = AdForm()

    return render(request, 'admin/ad_form.html', {
        'form': form,
        'title': 'Create New Ad',
        'is_edit': False,
    })


@staff_member_required(login_url='/admin/login/')
def ad_edit(request, pk):
    """Edit an existing ad."""
    ad = get_object_or_404(Ad, pk=pk)
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ad updated successfully.')
            return redirect('admin_ads_list')
    else:
        form = AdForm(instance=ad)

    return render(request, 'admin/ad_form.html', {
        'form': form,
        'ad': ad,
        'title': f'Edit Ad: {ad.title}',
        'is_edit': True,
    })


@staff_member_required(login_url='/admin/login/')
def ad_delete(request, pk):
    """Delete an ad."""
    ad = get_object_or_404(Ad, pk=pk)
    if request.method == 'POST':
        ad.delete()
        messages.success(request, 'Ad deleted successfully.')
    return redirect('admin_ads_list')


# --- Message Management ---

@staff_member_required(login_url='/admin/login/')
def messages_list(request):
    """List all contact messages."""
    all_messages = ContactMessage.objects.all()
    return render(request, 'admin/messages_list.html', {'contact_messages': all_messages})


@staff_member_required(login_url='/admin/login/')
def message_detail(request, pk):
    """View a single contact message and mark as read."""
    msg = get_object_or_404(ContactMessage, pk=pk)
    if not msg.is_read:
        msg.is_read = True
        msg.save()
    return render(request, 'admin/message_detail.html', {'msg': msg})


@staff_member_required(login_url='/admin/login/')
def message_toggle_read(request, pk):
    """Toggle read/unread status of a message."""
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = not msg.is_read
    msg.save()
    return redirect('admin_messages_list')


@staff_member_required(login_url='/admin/login/')
def message_delete(request, pk):
    """Delete a contact message."""
    msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == 'POST':
        msg.delete()
        messages.success(request, 'Message deleted successfully.')
    return redirect('admin_messages_list')
