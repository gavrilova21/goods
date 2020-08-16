import asyncio
import aio_pika
import aiosmtplib
from email.message import EmailMessage
import json


async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        email_message = EmailMessage()
        message = json.loads(message.body.decode("utf-8"))
        email_message["From"] = "sender email"
        email_message["To"] = message["to"]
        email_message["Subject"] = "No subject"
        email_message.set_content(message["text"])

        await aiosmtplib.send(email_message, hostname="mail", port=25)
        await asyncio.sleep(1)


async def listener(loop):
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@rabbit/", loop=loop, port=5672
    )

    queue_name = "mail"
    channel = await connection.channel()
    queue = await channel.declare_queue(queue_name)
    await queue.consume(process_message)
