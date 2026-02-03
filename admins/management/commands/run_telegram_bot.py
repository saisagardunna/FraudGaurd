import logging
import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings
from users.models import UserRegistrationModel
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from asgiref.sync import sync_to_async
import webbrowser

# Constants
TOKEN = '8394032591:AAG_9Kitz0j1A00mvD3iBVgWlJe9as6Oix8'

# Configure Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs the Telegram Bot for FraudGuard Admin'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Telegram Bot...'))
        
        application = ApplicationBuilder().token(TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler('help', self.help_command))
        application.add_handler(CommandHandler('pending', self.pending_users))
        application.add_handler(CommandHandler('menu', self.menu))
        application.add_handler(CommandHandler('links', self.links))
        
        # Handle Buttons
        application.add_handler(CallbackQueryHandler(self.button_handler))
        
        # Handle Menu Text (if they type the menu options)
        application.add_handler(MessageHandler(filters.Regex('^(PENDING USERS|LINKS|STATS)$'), self.menu_handler))

        # Run
        application.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            ["PENDING USERS", "LINKS"],
            ["STATS"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "🤖 *Welcome to FraudGuard Bot!*\n\n"
            "I can help you manage your application directly from Telegram.\n\n"
            "🔹 *Approve Users*: Get notified and activate new registrations.\n"
            "🔹 *Quick Links*: Access your Admin and User portals.\n"
            "🔹 *Stats*: See system status.\n\n"
            "Use the menu below or type /help.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "📋 *Available Commands:*\n\n"
            "/start - Main Menu\n"
            "/pending - List users waiting for activation\n"
            "/links - Get direct links to your app pages\n"
            "/stats - View application statistics\n"
            "/menu - Show the keyboard menu",
            parse_mode='Markdown'
        )
        
    async def menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.start(update, context)

    async def menu_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        if text == "PENDING USERS":
            await self.pending_users(update, context)
        elif text == "LINKS":
            await self.links(update, context)
        elif text == "STATS":
            await self.stats(update, context)

    async def pending_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        users = await sync_to_async(list)(UserRegistrationModel.objects.filter(status='waiting'))
        
        if not users:
            await update.message.reply_text("✅ No pending user registrations found.")
            return

        await update.message.reply_text(f"found {len(users)} pending users:")
        
        for user in users:
            keyboard = [
                [
                    InlineKeyboardButton("✅ Activate", callback_data=f"activate_{user.id}"),
                    InlineKeyboardButton("❌ Delete", callback_data=f"delete_{user.id}"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = (
                f"👤 *Registration Request*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"**Name:** {user.name}\n"
                f"**ID:** `{user.loginid}`\n"
                f"**Email:** {user.email}\n"
                f"**Mobile:** {user.mobile}\n"
                f"**Locality:** {user.locality}"
            )
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')



    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        total_users = await sync_to_async(UserRegistrationModel.objects.count)()
        active_users = await sync_to_async(UserRegistrationModel.objects.filter(status='activated').count)()
        pending_users = await sync_to_async(UserRegistrationModel.objects.filter(status='waiting').count)()
        
        text = (
            "📊 *System Statistics*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"**Total Users:** {total_users}\n"
            f"**Active:** {active_users}\n"
            f"**Pending:** {pending_users}\n"
        )
        await update.message.reply_text(text, parse_mode='Markdown')

    async def links(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("🖥 Open Admin (Host)", callback_data="open_admin")],
            [InlineKeyboardButton("🖥 Open User Login (Host)", callback_data="open_user")],
            [InlineKeyboardButton("� Open Registration (Host)", callback_data="open_register")],
            [InlineKeyboardButton("🖥 Open Home (Host)", callback_data="open_home")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = (
            "� *Remote Control Links*\n"
            "Click below to open these pages **on your laptop/server**."
        )
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        base_url = "http://127.0.0.1:8000"
        
        match data:
            case "open_admin":
                webbrowser.open(f"{base_url}/admins/AdminLoginCheck/")
                await query.edit_message_text("✅ Opened **Admin Login** on host machine.", parse_mode='Markdown')
                return
            case "open_user":
                webbrowser.open(f"{base_url}/users/UserLoginCheck/")
                await query.edit_message_text("✅ Opened **User Login** on host machine.", parse_mode='Markdown')
                return
            case "open_register":
                webbrowser.open(f"{base_url}/UserRegisterForm")
                await query.edit_message_text("✅ Opened **Registration** on host machine.", parse_mode='Markdown')
                return
            case "open_home":
                webbrowser.open(f"{base_url}/")
                await query.edit_message_text("✅ Opened **Home Page** on host machine.", parse_mode='Markdown')
                return

        # Handle User Actions (Activate/Delete)
        try:
            action, user_id = data.split('_')
            user_id = int(user_id)
            
            user = await sync_to_async(UserRegistrationModel.objects.get)(id=user_id)
            
            if action == 'activate':
                user.status = 'activated'
                await sync_to_async(user.save)()
                await query.edit_message_text(text=f"✅ User *{user.name}* has been **ACTIVATED**.", parse_mode='Markdown')
            elif action == 'delete':
                await sync_to_async(user.delete)()
                await query.edit_message_text(text=f"❌ User *{user.name}* has been **DELETED**.", parse_mode='Markdown')
                
        except UserRegistrationModel.DoesNotExist:
            await query.edit_message_text(text="⚠️ User not found (might have been processed already).")
        except Exception as e:
            await query.edit_message_text(text=f"⚠️ Error: {str(e)}")
