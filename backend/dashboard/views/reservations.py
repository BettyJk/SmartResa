# dashboard/views/reservations.py
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from ..models import Seat, Reservation

def seat_selection(request):
    # Get all seats and reservations
    seats = Seat.objects.all().order_by('number')
    reservations = Reservation.objects.filter(
        end_time__gte=timezone.now()
    )
    
    # Mark reserved seats
    reserved_seat_ids = [r.seat.id for r in reservations]
    
    context = {
        'seats': seats,
        'reserved_seat_ids': reserved_seat_ids,
    }
    return render(request, 'reservations/seat_selection.html', context)
# dashboard/views/reservations.py
from django.shortcuts import get_object_or_404
from ..forms import ReservationForm

def create_reservation(request, seat_id):
    seat = get_object_or_404(Seat, id=seat_id)
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.seat = seat
            
            # Validate reservation duration
            duration = reservation.end_time - reservation.start_time
            max_hours = {
                '3A': 2, '4A': 6, '5A': 8
            }.get(request.user.year, 0) if request.user.role == 'student' else 8
            
            if duration.total_seconds() / 3600 > max_hours:
                form.add_error('end_time', 
                    f"Max reservation time: {max_hours} hours for your account")
                return render(request, 'reservations/create.html', {'form': form})
            
            # Check for existing reservations
            overlapping = Reservation.objects.filter(
                seat=seat,
                start_time__lt=reservation.end_time,
                end_time__gt=reservation.start_time
            ).exists()
            
            if overlapping:
                form.add_error(None, "This seat is already reserved during selected time")
            else:
                reservation.save()
                seat.status = 'reserved'
                seat.save()
                return redirect('student_dashboard')
    
    else:
        form = ReservationForm()
    
    return render(request, 'reservations/create.html', {'form': form, 'seat': seat})