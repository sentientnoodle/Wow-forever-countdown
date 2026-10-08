1# Wow-forever-countdown
cnt
 WoW Forever Discord countdown

Target: November 4, 2026 at 6 PM EST (23:00 UTC).
This small custom bot uses Discord's REST API, so it needs no always-on server.
GitHub Actions starts a short job approximately every five minutes. Each job
updates the message five times, sleeping 60 seconds between updates. Jobs can be
delayed or dropped; this is not a second-by-second live image. The Discord
relative timestamp beside it updates in the client between image refreshes.
The image displays days, hours, and minutes only, and labels its last update time and approximate one-minute refresh interval.

## Free hosting setup

1. Create a **public GitHub repository** and upload the contents of this folder,
   including `.github/workflows/countdown.yml`. Standard Actions runners are free
   for public repositories. A private repo uses your limited included allowance.
2. Create an application at https://discord.com/developers/applications and add a
   bot. Invite it to your server using the OAuth2 `bot` scope. Grant View Channel,
   Send Messages, Send Messages in Threads, and Attach Files. Add it to private
   threads if needed. Keep the target thread active/unarchived.
3. In Discord enable Settings → Advanced → Developer Mode. Right-click the
   **target thread** and Copy Channel ID.
4. In GitHub → Settings → Secrets and variables → Actions, add the bot token as
   a **secret** named `DISCORD_BOT_TOKEN`. Never commit or share the token.
   Under **Variables**, add `DISCORD_CHANNEL_ID` with the thread ID.
5. Open Actions → WoW Forever Countdown → Run workflow. Check `bootstrap` once.
   The run posts one message. Copy the `DISCORD_MESSAGE_ID` printed in the run log
   and add it as a repository Actions **variable** of the same name.
6. Run again with bootstrap unchecked to verify editing. All scheduled runs edit
   that same message and replace the image, rather than posting new messages.
   Don't bootstrap again unless you deliberately want a new message.

Public scheduled workflows can disable after 60 days without repository activity.
This launch is less than 60 days away. The script stops editing one day after launch;
disable the workflow then to stop running jobs entirely. No deployment has been
performed by creating this package.

## Artwork and colors

The replacement logo is included with its existing transparent background.
Cinzel Bold is included under the accompanying SIL Open Font License.
Background #0F172A; boxes #182839; bronze borders #8B693D; gold #D4AF67;
parchment digits #F3E6C8; icy blue labels #8ECADD. These implement the earlier
gold/bronze/parchment/blue recommendation; earlier exact custom hex values were
not present in the supplied conversation (the screenshot showed default colors).

For the faint Azeroth background, place your desired artwork at `assets/azeroth.png`.
The full scene spans the entire counter, resized to the canvas, at up to 35% opacity on the left and fading to transparent on the right.
Your supplied village artwork is included as the fading background.
The 1000 × 480 format gives the logo and countdown enough room to read in Discord.

## Local preview (optional; hosting doesn't depend on your computer)

    pip install -r requirements.txt
    python countdown.py --preview

Open preview.png. Deployment requires your own GitHub account and bot secret.

## One-minute updates

The scheduler itself has a five-minute minimum, so each job runs five updates.
API/render time adds a little drift. Scheduling delays can leave gaps; this is
not a guaranteed uninterrupted one-minute service. Overlapping jobs cancel the
older job to avoid building a queue. Each image shows its latest successful
update time. Keep the repository public to use standard runners for free.
