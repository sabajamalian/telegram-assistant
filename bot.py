import os
import logging
import json
import tempfile
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from voice_processor import VoiceProcessor

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get the token from environment variable
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Initialize voice processor
voice_processor = VoiceProcessor()

def log_message_metadata(update: Update):
    """Log all metadata from the incoming message."""
    message = update.message
    metadata = {
        "message_id": message.message_id,
        "date": message.date.isoformat(),
        "chat": {
            "id": message.chat.id,
            "type": message.chat.type,
            "title": message.chat.title if message.chat.title else None,
            "username": message.chat.username,
            "first_name": message.chat.first_name,
            "last_name": message.chat.last_name
        },
        "from_user": {
            "id": message.from_user.id,
            "is_bot": message.from_user.is_bot,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "username": message.from_user.username,
            "language_code": message.from_user.language_code
        }
    }
    
    # Add message type and content
    if message.text:
        metadata["type"] = "text"
        metadata["content"] = message.text
    elif message.photo:
        metadata["type"] = "photo"
        metadata["content"] = f"Photo with {len(message.photo)} sizes"
    elif message.voice:
        metadata["type"] = "voice"
        metadata["content"] = f"Voice message: {message.voice.duration}s"
    elif message.document:
        metadata["type"] = "document"
        metadata["content"] = f"Document: {message.document.file_name}"
    elif message.sticker:
        metadata["type"] = "sticker"
        metadata["content"] = f"Sticker: {message.sticker.emoji}"
    else:
        metadata["type"] = "unknown"
        metadata["content"] = "Unsupported message type"
    
    logger.info(f"Message metadata: {json.dumps(metadata, indent=2)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    log_message_metadata(update)
    await update.message.reply_text('Hello! I am your echo bot. Send me any message and I will echo it back!')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message."""
    log_message_metadata(update)
    if update.message.text:
        await update.message.reply_text(f"Echo: {update.message.text}")
    else:
        await update.message.reply_text("I can only echo text messages!")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages by transcribing, translating, and executing tasks."""
    log_message_metadata(update)
    
    try:
        # Get the voice file
        voice = await update.message.voice.get_file()
        
        # Create a temporary file to store the voice message
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
            # Download the voice file
            await voice.download_to_drive(temp_file.name)
            
            # Process the voice file and execute the task
            task_type, task_response = await voice_processor.process_voice(temp_file.name)
            
            # Send the task response back to the user
            if task_response["status"] == "success":
                await update.message.reply_text(
                    f"Task: {task_type}\n"
                    f"Status: {task_response['message']}\n"
                    f"Content: {task_response['content']}"
                )
            else:
                await update.message.reply_text(
                    f"Error: {task_response['message']}\n"
                    f"Please try again with a clearer instruction."
                )
            
    except Exception as e:
        logger.error(f"Error processing voice message: {str(e)}")
        await update.message.reply_text("Sorry, I couldn't process your voice message. Please try again.")

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 