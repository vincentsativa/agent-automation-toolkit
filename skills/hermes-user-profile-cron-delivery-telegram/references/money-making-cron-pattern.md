# Money-Making Opportunities Cron Pattern

A cron job that reads daily data files and finds actionable low-budget money-making opportunities. Inspired by the PayPal origin story: the feature that took the least effort became the product.

## Concept

The daily data pipeline (tensorfeed, ironpulse, blogwatcher, 20 AI news stories) generates a firehose of information. This cron is the signal extractor — it reads all of today's data and finds the one stupid little thing nobody else noticed that could be the next PayPal.

## Configuration

- **Schedule:** Daily at 6:00 PM ET (after all four data collection jobs complete)
- **Delivery:** Telegram notification only — the actual content goes to email
- **Skills loaded:** `email-sender` (for attaching the text file)

## Prompt Structure

```
You are a scrappy opportunity scout. Your job is to read today's daily data files and find specific, actionable, low-budget money-making opportunities.

IMPORTANT: This is NOT a tutorial or article writing job. Do NOT write tutorials, articles, or educational content. You are finding real opportunities to make money.

Steps:
1. Read all data files from /mnt/c/Users/<user>/OneDrive/Desktop/TODAYS DATA FILES/
2. Identify specific, actionable money-making opportunities from the data — things like affiliate programs, product launches, service gaps, freelance gigs, arbitrage plays, or any concrete way to make money with low upfront cost
3. Write the findings to a text file at /mnt/c/Users/<user>/OneDrive/Desktop/MONEY MAKING OPPORTUNITIES/money-making-opportunities-YYYY-MM-DD.txt (create the folder if it doesn't exist)
4. Email that text file as an attachment to [REDACTED_EMAIL] with subject "Money Making Opportunities - YYYY-MM-DD"
5. Send me a Telegram message saying "Email sent with today's money-making opportunities" — nothing more, nothing less
```

## Key Rules

- **Not a tutorial/Article writer.** This cron is explicitly NOT the tutorial pipeline. It finds opportunities, not content ideas.
- **Email the text file as attachment.** The Telegram message is just a notification. The content lives in the email.
- **Brief Telegram notification.** "Email sent with today's money-making opportunities" — nothing more. No summary, no preview, no "here's what I found."
- **Create the output folder.** The folder `MONEY MAKING OPPORTUNITIES` on the desktop should be created by the cron job if it doesn't exist.

## The Philosophy

This cron exists because of the PayPal origin story: Elon Musk spent months building a financial hub, then added a "send money to email" feature in a few hours. The last-minute throwaway feature became the entire company. The months of infrastructure work was scrapped.

The daily data pipeline is the infrastructure. This cron is looking for the email-money-transfer moment — the one stupid little thing in today's noise that could be the actual product.
