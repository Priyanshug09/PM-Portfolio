# AI Support Bot — Image Upload Drop-off Analysis

## Project Overview

This is a GenAI Product Analyst case study analyzing a failure in an AI customer support bot.

The bot helps e-commerce users report damaged items and request refund or replacement. This case study focuses on a journey failure where users abandon the chatbot after the image upload step.

## Problem Statement

Some users successfully upload the image, but the bot may fail to acknowledge or process it. The bot then asks for the image again, causing frustration and abandonment.

## Objective

Analyze the image upload journey using:

- Product thinking
- User journey mapping
- Event tracking
- SQL analysis
- Product metrics
- GenAI metrics
- Business impact
- AI prototype flow

## User Journey

```text
User opens chat
↓
User describes damaged item
↓
Bot detects damaged item intent
↓
Bot asks for image proof
↓
User uploads image
↓
System analyzes image
↓
Bot offers refund/replacement or fallback
↓
Case closes or escalates
