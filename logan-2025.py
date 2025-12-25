import smtplib
import os
import requests
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
from datetime import datetime

# Set emails
RECEIVING = "eura.nofshin@gmail.com"
RECEIVING2 = "logan.nofshin@gmail.com"
APP_PASSWORD = os.getenv('APP_PASSWORD')


# Get the top post from the last 24 hours
def get_image_url(post):
    # 1. Gallery posts (multiple images)
    if post.get("is_gallery"):
        media_id = post["gallery_data"]["items"][0]["media_id"]
        meta = post["media_metadata"][media_id]
        return meta["s"]["u"].replace("&amp;", "&")

    # 2. Reddit-hosted preview image
    preview = post.get("preview")
    if preview and "images" in preview:
        return preview["images"][0]["source"]["url"].replace("&amp;", "&")

    # 3. Direct image URL
    url = post.get("url", "")
    if url.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
        return url

    return None


def send_email_with_embedded_image(
    receiving,
    subject,
    body_text,
    image_url,
    sender = "eura.nofshin@gmail.com",
    password = None,
    smtp_server="smtp.gmail.com",
    smtp_port=465,
):
    # Download image
    headers = {"User-Agent": "email-image-embedder/1.0"}
    headers = {"User-Agent": "PoetryEmailBot/0.1 by u/machinesyall"}
    response = requests.get(image_url, headers=headers)
    response.raise_for_status()
    image_bytes = response.content

    # Guess image subtype
    subtype = image_url.split(".")[-1].split("?")[0]

    # Create CID
    image_cid = make_msgid(domain="example.com")

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = receiving
    msg["Subject"] = subject

    # Plain-text fallback
    msg.set_content(body_text)

    # HTML version with embedded image
    msg.add_alternative(
        f"""
        <html>
          <body>
            <p>{body_text}</p>
            <img src="cid:{image_cid[1:-1]}" style="max-width:100%;">
          </body>
        </html>
        """,
        subtype="html",
    )

    # Attach image as related content
    msg.get_payload()[1].add_related(
        image_bytes,
        maintype="image",
        subtype=subtype,
        cid=image_cid,
        filename="embedded_image",
    )

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

URL = "https://www.reddit.com/r/Poetry/top.json"
HEADERS = {"User-Agent": "poetry-email-script/1.0"}

params = {
    "t": "day",
    "limit": 1
}

response = requests.get(URL, headers=HEADERS, params=params)
response.raise_for_status()

data = response.json()
post = data["data"]["children"][0]["data"]

title = post["title"]
post_url = post["url"]
image_url = get_image_url(post)


# Send an email
print("The date is:", datetime.now().strftime("%B %d, %Y"))

try:
    if image_url: 
        body = f'''
        <p>Original Reddit post: {"https://www.reddit.com" +post['permalink']}</p>

        <p>Happy reading!</p>
        <p>Eur ♡</p>
        '''
        send_email_with_embedded_image(
            RECEIVING,
            f"{title}",
            body,
            image_url,
            password = APP_PASSWORD)
        print("Today's post is sent!")
    else:
        print("No image for today!")
except Exception as e: 
    print(f"Failed to send: {e}")

