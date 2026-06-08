# Metrics for Uber Ride Matching

## Core Metric

Match Success Rate = Successfully matched ride requests / Total confirmed ride requests

Example:

If 1,000 riders confirm rides and 700 get matched:

Match Success Rate = 700 / 1,000 = 70%

## Supporting Metrics

| Metric | Meaning |
|---|---|
| Driver Acceptance Rate | Are drivers accepting requests? |
| Request Timeout Rate | Are ride requests failing before match? |
| Average Time to Match | How long does matching take? |
| Average Pickup ETA | How far are drivers from riders? |
| Rider Cancellation Rate | Are riders cancelling before match/start? |
| Driver Cancellation Rate | Are drivers cancelling after accepting? |
| Completed Trip Rate | Are matched rides converting into completed trips? |

## Funnel

App Opened → Destination Entered → Ride Selected → Ride Confirmed → Driver Matched → Driver Arrived → Trip Started → Trip Completed

## Key Learning

Use funnel analysis when you want to know where the journey is breaking.

Use root cause analysis when you want to know why it is breaking.
