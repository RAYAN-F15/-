import os
import re
import yt_dlp
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from keep_alive import keep_alive

# تحميل التوكن من ملف .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# دالة الترحيب
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "أهلاً بك! 🎬\n"
        "أرسل لي أي رابط من تيك توك (TikTok) وسأقوم بتحميل المقطع وإرساله لك فوراً."
    )

# دالة معالجة الروابط وتحميل الفيديو
# دالة معالجة الروابط وتحميل الفيديو
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    chat_id = update.message.chat_id
    message_id = update.message.message_id # استخراج رقم الرسالة لجعله اسماً فريداً

    # التحقق مما إذا كانت الرسالة تحتوي على رابط تيك توك
    if "tiktok.com" in text or "vm.tiktok.com" in text:
        # استخراج الرابط الصحيح وتجاهل أي مسافات
        url = re.search(r"(?P<url>https?://[^\s]+)", text).group("url")
        
        status_message = await update.message.reply_text("⏳ جاري تحميل المقطع، يرجى الانتظار...")

        # 1. إعطاء كل فيديو اسماً فريداً حتى لا يتكرر المقطع السابق
        file_name = f"video_{chat_id}_{message_id}.mp4"
        
        # 1. التعديل الأول: إعدادات التحميل
        ydl_opts = {
            'outtmpl': file_name,
            # إجبار المكتبة على جلب صيغة MP4 بترميز H.264 المدعوم كلياً في تليجرام
            'format': 'best[ext=mp4][vcodec^=avc]/best[ext=mp4]/best', 
            'quiet': True,
            'no_warnings': True,
            'overwrites': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # 2. التعديل الثاني: أمر الإرسال لتليجرام
            await context.bot.send_video(
                chat_id=chat_id,
                video=open(file_name, 'rb'),
                caption="📥 تم التحميل بنجاح!",
                reply_to_message_id=message_id,
                supports_streaming=True  # 🟢 هذا السطر يمنع التقطيع داخل مشغل تليجرام
            )
            await status_message.delete()

        except Exception as e:
            await status_message.edit_text(f"❌ عذراً، فشل التحميل.\nالخطأ: {e}")

        finally:
            # التأكد من إغلاق الملف وحذفه من جهازك
            try:
                if os.path.exists(file_name):
                    os.remove(file_name)
            except Exception as cleanup_error:
                print(f"لم يتم حذف الملف: {cleanup_error}")
    else:
        await update.message.reply_text("⚠️ يرجى إرسال رابط صحيح من تيك توك.")
def main() -> None:
    if not TELEGRAM_TOKEN:
        print("❌ الرجاء التأكد من وضع TELEGRAM_TOKEN في ملف .env")
        return

    # بناء التطبيق
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # ربط الدوال بالأحداث
    application.add_handler(CommandHandler("start", start))
    # التقاط أي رسالة نصية ليست أمراً (Command)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ بوت تحميل تيك توك يعمل الآن...")
    keep_alive() # تشغيل الخادم الوهمي
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    

if __name__ == '__main__':
    main()