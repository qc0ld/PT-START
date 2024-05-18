import logging
import re
import paramiko
import psycopg2
import os
import subprocess
from dotenv import load_dotenv
from psycopg2 import sql
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

load_dotenv()

host = os.getenv('HOST')
port = os.getenv('PORT')
username = os.getenv('USER')
password = os.getenv('PASSWORD')

usernamedb=os.getenv('DBUSER')
passworddb=os.getenv('DBPASSWORD')
hostdb=os.getenv('DBHOST')
portdb=os.getenv('DBPORT')
database=os.getenv('DBNAME')

TOKEN = os.getenv('TOKEN')

logging.basicConfig(filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def ssh_connect(command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=port)

    stdin, stdout, stderr = ssh.exec_command(command)
    info = stdout.read().decode()
    ssh.close()
    return info

logger = logging.getLogger(__name__)

def write_email_to_db(update: Update, context):
    connection = psycopg2.connect(user=usernamedb,
                                    password=passworddb,
                                    host=hostdb,
                                    port=portdb, 
                                    database=database)
    cursor = connection.cursor()

    data = context.user_data['emails']
    emails = re.findall(r'\b[A-Za-z0-9]+@[A-Za-z0-9]+\.[A-Za-z]{2,}\b', data)

    for email in emails:
        try:
            cursor.execute("INSERT INTO emails (email) VALUES ('" + email + "');")
            connection.commit()
        except Exception as e:
            update.message.reply_text("Error while writing to database: " + str(e))
            cursor.close()
            connection.close()
            return ConversationHandler.END
    update.message.reply_text("Successfully writed to database")
    cursor.close()
    connection.close()
    return ConversationHandler.END

def findEmails(update: Update, context):
    user_input = update.message.text
    emails = ''
    
    emailRegex = re.compile(r'\b[A-Za-z0-9]+@[A-Za-z0-9]+\.[A-Za-z]{2,}\b')
    
    matches = emailRegex.finditer(user_input)
    
    count = 0
    for match in matches:
        emails += str(count + 1) + ". " + str(match.group()) + "\n"
        count += 1

    if count == 0:
        update.message.reply_text("Emails not found")
        return ConversationHandler.END

    context.user_data['emails'] = emails
    update.message.reply_text(emails + '\nDo you want to add found emails to database? "Yes" or "No"')
    return 'getUserResponseEmails'

def getUserResponseEmails(update: Update, context):
    user_input = update.message.text
    if user_input.lower() == "yes":
        write_email_to_db(update, context)
    elif user_input.lower() == "no":
        update.message.reply_text("Not writing to database")
    else:
        update.message.reply_text("Invalid input")
    return ConversationHandler.END

def getUserResponsePhoneNumbers(update: Update, context):
    user_input = update.message.text
    if user_input.lower() == "yes":
        write_phone_number_to_db(update, context)
    elif user_input.lower() == "no":
        update.message.reply_text("Not writing to database")
    else:
        update.message.reply_text("Invalid input")
    return ConversationHandler.END

def write_phone_number_to_db(update: Update, context):
    connection = psycopg2.connect(user=usernamedb,
                                    password=passworddb,
                                    host=hostdb,
                                    port=portdb, 
                                    database=database)
    cursor = connection.cursor()

    data = context.user_data['phone_numbers']
    phone_numbers = []
    for line in data.split('\n'):
        number = re.sub(r'^\d+\.\s*', '', line)
        number = re.sub(r'\+7', '8', number)
        number = re.sub(r'\+7|[-()\s]', '', number)
        if number:
            phone_numbers.append(number)
    for phone_number in phone_numbers:
        try:
            cursor.execute("INSERT INTO phone_numbers (phone_number) VALUES ('" + str(phone_number) + "');")
            connection.commit()
        except Exception as e:
            update.message.reply_text("Error while writing to database: " + str(e))
            cursor.close()
            connection.close()
            return ConversationHandler.END
    update.message.reply_text("Successfully writed to database")
    cursor.close()
    connection.close()
    return ConversationHandler.END


def findPhoneNumbers(update: Update, context):
    user_input = update.message.text
    phoneNumbers = ''
    
    phoneNumRegex = re.compile(r'((8|\+7) \(\d{3}\) \d{3}-\d{2}-\d{2}|(8|\+7)\d{10}|(8|\+7)\(\d{3}\)\d{7}|(8|\+7) \d{3} \d{3} \d{2} \d{2}|(8|\+7) \(\d{3}\) \d{3} \d{2} \d{2}|(8|\+7)-\d{3}-\d{3}-\d{2}-\d{2})')
    matches = phoneNumRegex.finditer(user_input)
    
    count = 0
    for match in matches:
        phoneNumbers += str(count + 1) + ". " + str(match.group()) + "\n"
        count += 1

    if count == 0:
        update.message.reply_text("Phone numbers not found")
        return ConversationHandler.END

    context.user_data['phone_numbers'] = phoneNumbers
    update.message.reply_text(phoneNumbers + '\nDo you want to add found phone_numbers to database? "Yes" or "No"')
    return 'getUserResponsePhoneNumbers'

def get_emails(update: Update, context):
    connection = psycopg2.connect(user=usernamedb,
                                    password=passworddb,
                                    host=hostdb,
                                    port=portdb, 
                                    database=database)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM emails;")
    emails = cursor.fetchall()
    response = ""
    for email in emails:
        response += str(email[0]) + ". " + str(email[1]) + "\n"
    update.message.reply_text(response)
    connection.close()
    cursor.close()
    return ConversationHandler.END

def get_phone_numbers(update: Update, context):
    connection = psycopg2.connect(user=usernamedb,
                                    password=passworddb,
                                    host=hostdb,
                                    port=portdb, 
                                    database=database)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM phone_numbers;")
    phone_numbers = cursor.fetchall()
    response = ""
    for phone_number in phone_numbers:
        response += str(phone_number[0]) + ". " + str(phone_number[1]) + "\n"
    update.message.reply_text(response)
    connection.close()
    cursor.close()
    return ConversationHandler.END

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Hello {user.full_name}!')

def helpCommand(update: Update, context):
    update.message.reply_text('Help!')

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Enter text for searching phone numbers: ')
    return 'findPhoneNumbers'

def findEmailCommand(update: Update, context):
    update.message.reply_text('Enter text for searching emails: ')
    return 'findEmails'

def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Enter a passowrd to verify: ')
    return 'verifyPassword'

def verifyPassword(update: Update, context):
    user_input = update.message.text

    if len(user_input) < 8:
        update.message.reply_text('Password is simple')
        return ConversationHandler.END

    if not re.search(r'[A-Z]', user_input):
        update.message.reply_text('Password is simple')
        return ConversationHandler.END

    if not re.search(r'[a-z]', user_input):
        update.message.reply_text('Password is simple')
        return ConversationHandler.END

    if not re.search(r'[0-9]', user_input):
        update.message.reply_text('Password is simple')
        return ConversationHandler.END

    if not re.search(r'[@$!%*?&]', user_input):
        update.message.reply_text('Password is simple')
        return ConversationHandler.END

    update.message.reply_text('Password is hard')
    return ConversationHandler.END

def get_release(update: Update, context):
    update.message.reply_text(ssh_connect('lsb_release -a'))
    return ConversationHandler.END

def get_uname(update: Update, context):
    update.message.reply_text(ssh_connect('uname -a'))
    return ConversationHandler.END

def get_uptime(update: Update, context):
    update.message.reply_text(ssh_connect("uptime"))
    return ConversationHandler.END

def get_df(update: Update, context):
    update.message.reply_text(ssh_connect('df -h'))
    return ConversationHandler.END

def get_free(update: Update, context):
    update.message.reply_text(ssh_connect('free -h'))
    return ConversationHandler.END

def get_mpstat(update: Update, context):
    update.message.reply_text(ssh_connect('mpstat'))
    return ConversationHandler.END

def get_w(update: Update, context):
    update.message.reply_text(ssh_connect('w'))
    return ConversationHandler.END

def get_auths(update: Update, context):
    update.message.reply_text(ssh_connect('last -n 10'))
    return ConversationHandler.END

def get_critical(update: Update, context):
    update.message.reply_text(ssh_connect('journalctl -p 2 -n 5'))
    return ConversationHandler.END

def get_ps(update: Update, context):
    update.message.reply_text(ssh_connect('ps ax | head -n 25'))
    return ConversationHandler.END

def get_ss(update: Update, context):
    update.message.reply_text(ssh_connect('ss -tuln'))
    return ConversationHandler.END

def get_services(update: Update, context):
    update.message.reply_text(ssh_connect('systemctl list-units --type=service --state=running | head -n 20'))
    return ConversationHandler.END

def get_repl_logs(update: Update, context):
    try:
        result = subprocess.run("cat /var/log/postgresql/postgresql.log | grep repl | tail -n 25", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            update.message.reply_text("Error while openning log file")
        else:
            update.message.reply_text(result.stdout.decode().strip('\n'))
    except Exception as e:
        update.message.reply_text("Error: " + str(e))
    return ConversationHandler.END

def get_apt_list_command(update: Update, context):
    update.message.reply_text('Enter "all" to list packages or "search" to search for a package')
    return 'get_apt_list_option'

def get_apt_list_option(update: Update, context):
    user_input = update.message.text.lower()
    if user_input == 'all':
        return get_apt_list_all(update, context)
    elif user_input == 'search':
        update.message.reply_text('Enter the package name: ')
        return 'get_apt_list_search'
    else:
        update.message.reply_text('Invalid option')
        return ConversationHandler.END

def get_apt_list_all(update: Update, context):
    update.message.reply_text(ssh_connect('apt list --installed | head -n 20'))
    return ConversationHandler.END

def get_apt_list_search(update: Update, context):
    update.message.reply_text(ssh_connect('apt list --installed | grep ' + str(update.message.text)))
    return ConversationHandler.END


def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('findPhoneNumbers', findPhoneNumbersCommand)],
        states={
            'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'getUserResponsePhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, getUserResponsePhoneNumbers)],
        },
        fallbacks=[]
    )
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('findEmails', findEmailCommand)],
        states={
            'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            'getUserResponseEmails': [MessageHandler(Filters.text & ~Filters.command, getUserResponseEmails)],
        },
        fallbacks=[]
    )
    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verifyPassword', verifyPasswordCommand)],
        states={
            'verifyPassword': [MessageHandler(Filters.text & ~Filters.command, verifyPassword)],
        },
        fallbacks=[]
    )
    convHandlerGetAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list_command)],
        states={
            'get_apt_list_option': [MessageHandler(Filters.text & ~Filters.command, get_apt_list_option)],
            'get_apt_list_search': [MessageHandler(Filters.text & ~Filters.command, get_apt_list_search)],
        },
        fallbacks=[]
    )

    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerGetAptList)


    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))

    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))

    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
