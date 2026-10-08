import argparse
import io
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
TARGET = datetime.fromisoformat("2026-11-04T18:00:00-05:00")


def font(size):
    result = ImageFont.truetype(str(ROOT / "Cinzel.ttf"), size)
    result.set_variation_by_name("Bold")
    return result


def render(now):
    canvas = Image.new("RGB", (1000, 480), "#0F172A")

    background = Image.open(ROOT / "azeroth.png").convert("RGB")
    background = background.resize(
        canvas.size, Image.Resampling.LANCZOS
    )

    mask = Image.new("L", canvas.size)
    mask.putdata([
        int(90 * (1 - x / 999) ** 1.3)
        for y in range(480)
        for x in range(1000)
    ])
    canvas.paste(background, (0, 0), mask)

    logo = Image.open(ROOT / "logo.png").convert("RGBA")
    logo.thumbnail((260, 214), Image.Resampling.LANCZOS)
    canvas.paste(logo, ((1000 - logo.width) // 2, 14), logo)

    draw = ImageDraw.Draw(canvas)

    draw.rounded_rectangle(
        (8, 8, 991, 471),
        radius=16,
        outline="#8B693D",
        width=2,
    )

    def text(value, y, size, color, x=500):
        draw.text(
            (x, y),
            value,
            anchor="mt",
            font=font(size),
            fill=color,
        )

    text(
        "NOVEMBER 4, 2026 · 6:00 PM EST",
        230, 19, "#D4AF67",
    )

    seconds = max(0, int((TARGET - now).total_seconds()))
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes = seconds // 60

    for index, (value, label) in enumerate(zip(
        [days, hours, minutes],
        ["DAYS", "HOURS", "MINUTES"],
    )):
        left = 185 + index * 218

        draw.rounded_rectangle(
            (left, 274, left + 194, 391),
            radius=12,
            fill="#182839",
            outline="#8B693D",
            width=2,
        )

        text(f"{value:02d}", 290, 48, "#F3E6C8", left + 97)
        text(label, 353, 16, "#8ECADD", left + 97)

    slogan = "FOR AZEROTH!" if now < TARGET else "THE WAIT IS OVER!"
    text(slogan, 411, 21, "#D4AF67")

    updated = now.strftime("%H:%M UTC")
    text(
        f"REFRESHES ABOUT EVERY MINUTE · UPDATED {updated}",
        448, 11, "#8ECADD",
    )

    output = io.BytesIO()
    canvas.save(output, format="PNG")
    return output.getvalue()


def publish(image, create):
    token = os.environ["DISCORD_BOT_TOKEN"]
    channel = os.environ["DISCORD_CHANNEL_ID"]
    message = os.environ.get("DISCORD_MESSAGE_ID", "")

    if not create and not message:
        raise SystemExit("Set DISCORD_MESSAGE_ID after setup.")

    url = f"https://discord.com/api/v10/channels/{channel}/messages"
    if not create:
        url += f"/{message}"

    timestamp = int(TARGET.timestamp())
    payload = {
        "content": (
            f"Launch: <t:{timestamp}:F> — <t:{timestamp}:R>"
        ),
        "allowed_mentions": {"parse": []},
        "attachments": [
            {"id": 0, "filename": "countdown.png"}
        ],
    }

    for attempt in range(3):
        response = requests.request(
            "POST" if create else "PATCH",
            url,
            headers={"Authorization": f"Bot {token}"},
            data={"payload_json": json.dumps(payload)},
            files={
                "files[0]": (
                    "countdown.png", image, "image/png"
                )
            },
            timeout=30,
        )

        if response.status_code == 429:
            delay = float(response.json().get("retry_after", 1))
            if delay > 30:
                raise SystemExit("Rate limited; retry later.")
            time.sleep(delay)
            continue

        if not response.ok:
            raise SystemExit(
                f"Discord HTTP {response.status_code}: "
                "check your token, IDs, and bot permissions."
            )

        if create:
            print(
                "DISCORD_MESSAGE_ID=" + response.json()["id"],
                flush=True,
            )
        return

    raise SystemExit("Rate limit retries exhausted.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--create", action="store_true")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)

    if now > datetime.fromisoformat("2026-11-05T18:00:00-05:00"):
        print("Countdown complete.")
    else:
        publish(render(now), args.create)
