# dashboard/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Reservation, Seat, CourseSchedule
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@shared_task
def check_reservation_expiry():
    expired = Reservation.objects.filter(end_time__lte=timezone.now())
    for reservation in expired:
        seat = reservation.seat
        seat.status = 'available'
        seat.save()
        reservation.delete()
        
        # WebSocket update
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "seats",
            {
                "type": "seat.update",
                "number": seat.number,
                "status": seat.status
            }
        )
# dashboard/tasks.py
@shared_task
def auto_block_seats():
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    now = timezone.localtime()
    current_hour = now.time()
    current_day = now.weekday()
    
    active_courses = CourseSchedule.objects.filter(
        day_of_week=current_day,
        start_time__lte=current_hour,
        end_time__gte=current_hour
    )
    
    for course in active_courses:
        course.seats.update(status='blocked', blocked_reason=f"Course: {course.course.name}")