import os
import time
import shutil
import itertools
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Optional imports
try:
    import pyzipper
except ImportError:
    pyzipper = None

try:
    import py7zr
except ImportError:
    py7zr = None

# Enter your bot token here (Generated via @BotFather)
BOT_TOKEN = "8989123740:AAH9ozlBJyFoE_FiOiyMTqAgzRE0ZHavSNU"
bot = telebot.TeleBot(BOT_TOKEN)

# Directory Setup
DOWNLOAD_DIR = "bot_downloads"
EXTRACT_DIR_ZIP = os.path.join(DOWNLOAD_DIR, "_extract_temp_zip")
EXTRACT_DIR_7Z = os.path.join(DOWNLOAD_DIR, "_extract_temp_7z")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Dictionary to track user states
user_states = {}

# ======================================================
#                   SHARED HELPERS & CORES
# ======================================================

def get_char_set_by_choice(choice):
    if choice == '1':
        return [chr(i) for i in range(65, 91)], "Capital Letters (A-Z)"
    elif choice == '2':
        return [chr(i) for i in range(97, 123)], "Small Letters (a-z)"
    elif choice == '3':
        return [chr(i) for i in range(48, 58)], "Numbers (0-9)"
    elif choice == '4':
        chars = [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)] + [chr(i) for i in range(48, 58)]
        return chars, "Alphanumeric (Letters + Numbers)"
    return None, ""

# ======================================================
#                   ZIP CRACKING LOGIC
# ======================================================

def try_password_zip(zf, pwd):
    zf.setpassword(pwd.encode('utf-8'))
    try:
        zf.testzip()
        return True
    except (RuntimeError, pyzipper.BadZipFile):
        return False

def run_secure_brute_zip(chat_id, status_message_id, zip_path, chars, length):
    start_time = time.time()
    attempts = 0
    try:
        with pyzipper.AESZipFile(zip_path) as zf:
            for guess in itertools.product(chars, repeat=length):
                pwd = "".join(guess)
                attempts += 1
                
                if attempts % 5000 == 0:
                    try:
                        bot.edit_message_text(f"⏳ ZIP Cracking in progress...\nAttempts: {attempts}\nCurrent check: `{pwd}`", chat_id, status_message_id, parse_mode="Markdown")
                    except:
                        pass

                if try_password_zip(zf, pwd):
                    on_success(chat_id, status_message_id, pwd, attempts, start_time, EXTRACT_DIR_ZIP, zf, is_zip=True)
                    return True
        return False
    except Exception as e:
        bot.send_message(chat_id, f"[-] ZIP File Error: {e}")
        return False

def run_auto_brute_numeric_zip(chat_id, status_message_id, zip_path):
    start_time = time.time()
    attempts = 0
    try:
        with pyzipper.AESZipFile(zip_path) as zf:
            for number in range(0, 10000000):
                pwd = str(number)
                attempts += 1

                if attempts % 5000 == 0:
                    try:
                        bot.edit_message_text(f"⏳ ZIP Auto Mode running...\nAttempts: {attempts}\nCurrent check: `{pwd}`", chat_id, status_message_id, parse_mode="Markdown")
                    except:
                        pass

                if try_password_zip(zf, pwd):
                    on_success(chat_id, status_message_id, pwd, attempts, start_time, EXTRACT_DIR_ZIP, zf, is_zip=True)
                    return True
        return False
    except Exception as e:
        bot.send_message(chat_id, f"[-] ZIP File Error: {e}")
        return False

def run_auto_brute_leading_zeros_zip(chat_id, status_message_id, zip_path):
    start_time = time.time()
    attempts = 0
    try:
        with pyzipper.AESZipFile(zip_path) as zf:
            for length in range(1, 8):
                max_value = 10 ** length
                for number in range(0, max_value):
                    pwd = str(number).zfill(length)
                    attempts += 1

                    if attempts % 5000 == 0:
                        try:
                            bot.edit_message_text(f"⏳ ZIP Auto Mode (Leading Zeros) running...\nLength: {length}\nAttempts: {attempts}", chat_id, status_message_id)
                        except:
                            pass

                    if try_password_zip(zf, pwd):
                        on_success(chat_id, status_message_id, pwd, attempts, start_time, EXTRACT_DIR_ZIP, zf, is_zip=True)
                        return True
        return False
    except Exception as e:
        bot.send_message(chat_id, f"[-] ZIP File Error: {e}")
        return False

# ======================================================
#                   7Z CRACKING LOGIC
# ======================================================

def try_password_7z(archive_path, pwd):
    try:
        with py7zr.SevenZipFile(archive_path, mode='r', password=pwd) as archive:
            archive.testzip()
        return True
    except:
        return False

def run_secure_brute_7z(chat_id, status_message_id, archive_path, chars, length):
    start_time = time.time()
    attempts = 0
    for guess in itertools.product(chars, repeat=length):
        pwd = "".join(guess)
        attempts += 1
        
        if attempts % 200 == 0:
            try:
                bot.edit_message_text(f"⏳ 7Z Cracking in progress...\nAttempts: {attempts}\nCurrent check: `{pwd}`", chat_id, status_message_id, parse_mode="Markdown")
            except:
                pass

        if try_password_7z(archive_path, pwd):
            on_success(chat_id, status_message_id, pwd, attempts, start_time, EXTRACT_DIR_7Z, archive_path=archive_path, is_zip=False)
            return True
    return False

def run_auto_brute_numeric_7z(chat_id, status_message_id, archive_path):
    start_time = time.time()
    attempts = 0
    for number in range(0, 10000000):
        pwd = str(number)
        attempts += 1

        if attempts % 200 == 0:
            try:
                bot.edit_message_text(f"⏳ 7Z Auto Mode running...\nAttempts: {attempts}\nCurrent check: `{pwd}`", chat_id, status_message_id, parse_mode="Markdown")
            except:
                pass

        if try_password_7z(archive_path, pwd):
            on_success(chat_id, status_message_id, pwd, attempts, start_time, EXTRACT_DIR_7Z, archive_path=archive_path, is_zip=False)
            return True
    return False

def run_auto_brute_with_leading_zeros_7z(chat_id, status_message_id, archive_path):
    start_time = time.time()
    attempts = 0
    for length in range(1, 8):
        max_value = 10 ** length
        for number in range(0, max_value):
            pwd = str(number).zfill(length)
            attempts += 1

            if attempts % 200 == 0:
                try:
                    bot.edit_message_text(f"⏳ 7Z Auto Mode (Leading Zeros) running...\nLength: {length}\nAttempts: {attempts}", chat_id, status_message_id)
                except:
                    pass

            if try_password_7z(archive_path, pwd):
                on_success(chat_id, status_message_id, pwd, attempts, start_time, EXTRACT_DIR_7Z, archive_path=archive_path, is_zip=False)
                return True
    return False

# ======================================================
#                   SUCCESS HANDLER
# ======================================================

def on_success(chat_id, status_message_id, pwd, attempts, start_time, extract_dir, zf=None, archive_path=None, is_zip=True):
    os.makedirs(extract_dir, exist_ok=True)
    try:
        if is_zip and zf:
            zf.extractall(path=extract_dir)
        elif not is_zip and archive_path:
            with py7zr.SevenZipFile(archive_path, mode='r', password=pwd) as archive:
                archive.extractall(path=extract_dir)
    except Exception as e:
        print(f"Extraction error: {e}")

    elapsed = time.time() - start_time
    res_text = (
        "========================================\n"
        f"✅ **Password Found!**\n\n"
        f"🔑 **Password:** `{pwd}`\n"
        f"⏱️ **Time Elapsed:** {elapsed:.2f} seconds\n"
        f"📊 **Total Attempts:** {attempts}\n"
        "========================================"
    )
    try:
        bot.edit_message_text(res_text, chat_id, status_message_id, parse_mode="Markdown")
    except:
        bot.send_message(chat_id, res_text, parse_mode="Markdown")
    
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir, ignore_errors=True)

# ======================================================
#                   TELEGRAM BOT INTERFACE
# ======================================================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 **Welcome to Archive Password Cracker Bot!**\n\nPlease send me a password-protected `.zip` or `.7z` file to begin.")

@bot.message_handler(content_types=['document'])
def handle_archive(message):
    file_name = message.document.file_name
    file_ext = os.path.splitext(file_name)[1].lower()

    if file_ext == '.zip' and pyzipper is None:
        bot.reply_to(message, "[-] 'pyzipper' module is not installed on the server.")
        return
    if file_ext == '.7z' and py7zr is None:
        bot.reply_to(message, "[-] 'py7zr' module is not installed on the server.")
        return

    if file_ext not in ['.zip', '.7z']:
        bot.reply_to(message, "❌ Invalid file type! Please send `.zip` or `.7z` archives only.")
        return

    status_msg = bot.reply_to(message, "📥 Downloading your file, please wait...")
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    local_path = os.path.join(DOWNLOAD_DIR, f"{message.chat.id}_{file_name}")
    with open(local_path, 'wb') as f:
        f.write(downloaded_file)

    user_states[message.chat.id] = {
        'file_path': local_path,
        'file_ext': file_ext,
        'status_message_id': status_msg.message_id
    }

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("1. Manual Mode", callback_data="mode_1"))
    markup.add(InlineKeyboardButton("2. Auto Mode ( Only Numbers 0-9999999)", callback_data="mode_2"))
    markup.add(InlineKeyboardButton("3. Auto Mode (With Numbers with good accuracy )                          )", callback_data="mode_3"))

    bot.edit_message_text("⚙️ **Select Cracking Mode:**", message.chat.id, status_msg.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('mode_'))
def handle_mode_selection(call):
    chat_id = call.message.chat.id
    if chat_id not in user_states:
        bot.answer_callback_query(call.id, "No active session found for this file.")
        return

    choice = call.data.split('_')[1]
    state = user_states[chat_id]
    state['mode'] = choice

    if choice == '1':
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("A-Z (Capital Letters)", callback_data="char_1"))
        markup.add(InlineKeyboardButton("a-z (Small Letters)", callback_data="char_2"))
        markup.add(InlineKeyboardButton("0-9 (Numbers)", callback_data="char_3"))
        markup.add(InlineKeyboardButton("Mix (Alphanumeric)", callback_data="char_4"))
        bot.edit_message_text("🔤 **Select Password Character Type:**", chat_id, state['status_message_id'], reply_markup=markup)
    else:
        bot.edit_message_text("⚡ Initializing brute-force cracking structure...", chat_id, state['status_message_id'])
        run_auto_cracking(chat_id, state['status_message_id'])

@bot.callback_query_handler(func=lambda call: call.data.startswith('char_'))
def handle_char_selection(call):
    chat_id = call.message.chat.id
    if chat_id not in user_states: return

    char_choice = call.data.split('_')[1]
    chars, desc = get_char_set_by_choice(char_choice)
    
    user_states[chat_id]['chars'] = chars
    user_states[chat_id]['char_desc'] = desc

    msg = bot.edit_message_text("🔢 Please reply by typing the exact password length (e.g., 3, 4, 5):", chat_id, user_states[chat_id]['status_message_id'])
    bot.register_next_step_handler(msg, handle_length_input)

def handle_length_input(message):
    chat_id = message.chat.id
    if chat_id not in user_states: return

    try:
        length = int(message.text.strip())
        if length <= 0: raise ValueError()
    except ValueError:
        msg = bot.reply_to(message, "❌ Invalid number. Please enter a valid password length again:")
        bot.register_next_step_handler(msg, handle_length_input)
        return

    user_states[chat_id]['length'] = length
    state = user_states[chat_id]
    
    status_msg = bot.send_message(chat_id, f"🚀 Manual Brute-Force Started...\nType: {state['char_desc']}\nLength: {length}")
    
    found = False
    if state['file_ext'] == '.zip':
        found = run_secure_brute_zip(chat_id, status_msg.message_id, state['file_path'], state['chars'], length)
    else:
        found = run_secure_brute_7z(chat_id, status_msg.message_id, state['file_path'], state['chars'], length)

    if not found:
        try:
            bot.edit_message_text("❌ No password found within this configuration range.", chat_id, status_msg.message_id)
        except:
            bot.send_message(chat_id, "❌ No password found within this configuration range.")
        
    clean_session(chat_id)

def run_auto_cracking(chat_id, status_message_id):
    state = user_states[chat_id]
    found = False

    if state['mode'] == '2':
        if state['file_ext'] == '.zip':
            found = run_auto_brute_numeric_zip(chat_id, status_message_id, state['file_path'])
        else:
            found = run_auto_brute_numeric_7z(chat_id, status_message_id, state['file_path'])
    elif state['mode'] == '3':
        if state['file_ext'] == '.zip':
            found = run_auto_brute_leading_zeros_zip(chat_id, status_message_id, state['file_path'])
        else:
            found = run_auto_brute_with_leading_zeros_7z(chat_id, status_message_id, state['file_path'])

    if not found:
        try:
            bot.edit_message_text("❌ No password found within the predefined range (0-9999999).", chat_id, status_message_id)
        except:
            bot.send_message(chat_id, "❌ No password found within the predefined range (0-9999999).")

    clean_session(chat_id)

def clean_session(chat_id):
    if chat_id in user_states:
        file_path = user_states[chat_id].get('file_path')
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        del user_states[chat_id]

# Start Long Polling
if __name__ == "__main__":
    print("[+] Telegram Bot successfully activated on backend...")
    bot.infinity_polling()
#mmm
