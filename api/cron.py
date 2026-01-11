from django.core.mail import send_mail
from django.db.models import Max
from django.conf import settings
from datetime import date
from .models import Item, Bid


def process_auction_winners():
    """
    Cron job to process auction winners for auctions ending today.

    For each auction ending today:
    - Finds the highest bid
    - Updates the item with the auction winner
    - Sends an email to the winner
    """
    today = date.today()

    # Find all auctions ending today that don't have a winner assigned yet
    ending_auctions = Item.objects.filter(
        auction_end_date=today, auction_winner__isnull=True
    )

    for item in ending_auctions:
        # Get the highest bid amount for this item
        highest_bid_amount = Bid.objects.filter(item=item).aggregate(Max("bid_amount"))[
            "bid_amount__max"
        ]

        # Skip if no bids were placed
        if highest_bid_amount is None:
            continue

        # Get the winning bid (first one in case of ties)
        winning_bid = (
            Bid.objects.filter(item=item, bid_amount=highest_bid_amount)
            .order_by("created_at")
            .first()
        )

        # Ensure we have a valid winner
        if not winning_bid or not winning_bid.bidder:
            continue

        # Update the item with the auction winner
        item.auction_winner = winning_bid.bidder
        item.save()

        # Send email to winner
        winner_email = winning_bid.bidder.email

        try:
            # Use positional arguments like the working test version
            send_mail(
                f"Congratulations! You won {item.title}",
                "Login to your account to check shipping details.",
                settings.EMAIL_HOST_USER,
                [winner_email],
            )
        except Exception as e:
            # Log the error but continue processing other auctions
            print(
                f"Failed to send email to {winner_email} for item {item.id}: {str(e)}"
            )
