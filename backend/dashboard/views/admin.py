# dashboard/views/admin.py
from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import TruncHour
from django.shortcuts import render
from django.http import HttpResponse
import csv
from ..models import Seat, Reservation

def admin_dashboard(request):
    # Seat statistics using aggregation
    seat_stats = Seat.objects.aggregate(
        total=Count('id'),
        available=Count('id', filter=Q(status='available')),
        reserved=Count('id', filter=Q(status='reserved')),
        occupied=Count('id', filter=Q(status='occupied')),
        blocked=Count('id', filter=Q(status='blocked')),
    )

    # Current reservations
    current_reservations = Reservation.objects.filter(
        end_time__gte=timezone.now()
    ).order_by('-created_at')[:10]

    # Busiest hours analysis
    busiest_hours = Reservation.objects.annotate(
        hour=TruncHour('start_time')
    ).values('hour').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    # Recent reservations (last 7 days)
    recent_reservations = Reservation.objects.filter(
        start_time__gte=timezone.now() - timezone.timedelta(days=7)
    ).order_by('-start_time')

    context = {
        **seat_stats,
        'current_reservations': current_reservations,
        'busiest_hours': busiest_hours,
        'recent_reservations': recent_reservations[:10],  # Last 10
    }
    
    return render(request, 'dashboards/admin.html', context)

def export_reservations_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reservations.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['User', 'Seat', 'Start Time', 'End Time', 'Status'])
    
    for res in Reservation.objects.all().select_related('user', 'seat'):
        writer.writerow([
            res.user.email,
            res.seat.number,
            res.start_time.strftime("%Y-%m-%d %H:%M"),
            res.end_time.strftime("%Y-%m-%d %H:%M"),
            res.seat.status
        ])
    
    return response