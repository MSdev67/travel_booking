from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import random
from datetime import datetime, timedelta
from .models import TravelOption, Booking
from .forms import UserRegisterForm, UserUpdateForm, BookingForm, TravelSearchForm

def home(request):
    form = TravelSearchForm(request.GET or None)
    travel_options = TravelOption.objects.all().order_by('departure_time')[:6]  # Show only 6 latest options
    
    if form.is_valid():
        travel_type = form.cleaned_data.get('travel_type')
        source = form.cleaned_data.get('source')
        destination = form.cleaned_data.get('destination')
        date = form.cleaned_data.get('date')
        
        if travel_type:
            travel_options = travel_options.filter(travel_type=travel_type)
        if source:
            travel_options = travel_options.filter(source__icontains=source)
        if destination:
            travel_options = travel_options.filter(destination__icontains=destination)
        if date:
            travel_options = travel_options.filter(departure_time__date=date)
    
    context = {
        'travel_options': travel_options,
        'form': form,
    }
    return render(request, 'booking_app/home.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'booking_app/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    
    # Get user's booking stats
    total_bookings = Booking.objects.filter(user=request.user).count()
    confirmed_bookings = Booking.objects.filter(user=request.user, status='Confirmed').count()
    cancelled_bookings = Booking.objects.filter(user=request.user, status='Cancelled').count()
    
    context = {
        'form': form,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
    }
    return render(request, 'booking_app/profile.html', context)

@login_required
def travel_list(request):
    form = TravelSearchForm(request.GET or None)
    travel_options = TravelOption.objects.all().order_by('departure_time')
    
    if form.is_valid():
        travel_type = form.cleaned_data.get('travel_type')
        source = form.cleaned_data.get('source')
        destination = form.cleaned_data.get('destination')
        date = form.cleaned_data.get('date')
        
        if travel_type:
            travel_options = travel_options.filter(travel_type=travel_type)
        if source:
            travel_options = travel_options.filter(source__icontains=source)
        if destination:
            travel_options = travel_options.filter(destination__icontains=destination)
        if date:
            travel_options = travel_options.filter(departure_time__date=date)
    
    context = {
        'travel_options': travel_options,
        'form': form,
    }
    return render(request, 'booking_app/travel_list.html', context)

@login_required
def booking_create(request, travel_id):
    travel_option = get_object_or_404(TravelOption, pk=travel_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, travel_option=travel_option)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.travel_option = travel_option
            booking.save()
            
            # Update available seats
            travel_option.available_seats -= booking.number_of_seats
            travel_option.save()
            
            messages.success(request, 'Booking confirmed successfully!')
            return redirect('booking_list')
    else:
        form = BookingForm(travel_option=travel_option)
    
    context = {
        'form': form,
        'travel_option': travel_option,
    }
    return render(request, 'booking_app/booking_form.html', context)

@login_required
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'booking_app/booking_list.html', {'bookings': bookings})

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    
    # Calculate duration of travel
    duration = booking.travel_option.arrival_time - booking.travel_option.departure_time
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes = remainder // 60
    
    context = {
        'booking': booking,
        'duration_hours': int(hours),
        'duration_minutes': int(minutes),
    }
    return render(request, 'booking_app/booking_detail.html', context)

@login_required
def booking_cancel(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    
    if booking.status != 'Cancelled':
        # Restore available seats
        booking.travel_option.available_seats += booking.number_of_seats
        booking.travel_option.save()
        
        # Update booking status
        booking.status = 'Cancelled'
        booking.save()
        
        messages.success(request, 'Booking cancelled successfully!')
    else:
        messages.warning(request, 'Booking is already cancelled.')
    
    return redirect('booking_list')

# AI Assistant Functions
def ai_assistant(request):
    return render(request, 'booking_app/ai_assistant.html')

@csrf_exempt
def ai_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').lower()
            
            # AI Response Logic
            responses = {
                'hello': ["Hello! How can I help you with your travel plans today?", 
                         "Hi there! Ready to plan your next adventure?"],
                'hi': ["Hello! How can I assist you with travel booking?", 
                      "Hi! What can I help you with today?"],
                'help': ["I can help you with: booking travel, checking availability, managing your bookings, and answering travel questions. What do you need help with?"],
                'book': ["To book travel, go to the 'Travel Options' page, choose your preferred option, and click 'Book Now'.", 
                        "I can help you book flights, trains, or buses. What type of travel are you looking for?"],
                'flight': ["We have flights available to various destinations. Check the 'Travel Options' page for current availability.", 
                          "For flights, you can filter by destination and date on our travel search page."],
                'train': ["Train bookings are available! Browse our train options with flexible schedules.", 
                         "We offer comfortable train travel options. Check the travel page for details."],
                'bus': ["Affordable bus travel options are available. Great for short to medium distances!", 
                       "Our bus services provide economical travel. See available routes on the travel page."],
                'cancel': ["To cancel a booking, go to 'My Bookings', find the booking, and click 'Cancel'.", 
                          "You can cancel bookings from your bookings list. Note that cancellation policies may apply."],
                'price': ["Prices vary based on travel type, route, and time. Check the travel options page for current pricing.", 
                         "Our prices are competitive! Browse available options to see specific rates."],
                'availability': ["Check real-time availability on the Travel Options page. You can filter by date and destination.", 
                                "Seat availability updates in real-time. Use our search filters to find available options."],
                'thank': ["You're welcome! Happy to help with your travel needs.", 
                         "My pleasure! Safe travels!", 
                         "Anytime! Let me know if you need anything else."]
            }
            
            # Find the best matching response
            ai_reply = "I'm here to help with your travel booking needs. How can I assist you today?"
            for keyword, reply_options in responses.items():
                if keyword in user_message:
                    ai_reply = random.choice(reply_options)
                    break
            
            # Special cases for complex queries
            if 'cheap' in user_message or 'economy' in user_message:
                ai_reply = "For budget-friendly options, I recommend checking our bus services or booking in advance for better rates!"
            elif 'when' in user_message and 'depart' in user_message:
                ai_reply = "Departure times vary by route. Use the search filters on the Travel Options page to find specific schedules."
            elif 'how many' in user_message and 'seat' in user_message:
                ai_reply = "Seat availability is shown for each travel option. Green numbers indicate available seats!"
            
            return JsonResponse({'response': ai_reply})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)