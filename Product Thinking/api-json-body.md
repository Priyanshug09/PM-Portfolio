# API JSON Body Thinking

## User Action
Rider taps "Confirm Ride"

## Backend Needs to Know
- Who is requesting the ride?
- Where is the pickup?
- Where is the destination?
- What ride type is selected?
- How will the rider pay?
- When was the request made?

## Example JSON Body

```json
{
  "request_id": "REQ_98765",
  "rider_id": "R123",
  "session_id": "S456",
  "pickup": {
    "lat": 28.6139,
    "lng": 77.2090,
    "address": "Noida Sector 62 Metro",
    "accuracy_meters": 12
  },
  "drop": {
    "lat": 28.5355,
    "lng": 77.3910,
    "address": "DLF Mall of India"
  },
  "ride_type": "UberGo",
  "payment_method": "UPI",
  "estimated_fare": {
    "amount": 260,
    "currency": "INR"
  },
  "requested_at": "2026-06-08T20:00:00+05:30"
}
