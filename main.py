from email.message import EmailMessage
import ssl
import smtplib
import os
import openai
import datetime
import time
import schedule

# Sender email
email_sender = os.getenv('EMAIL_SENDER')
# App password for sender email. Create one here: https://myaccount.google.com/apppasswords
email_password = os.getenv('EMAIL_PASS')

# Email receiver
email_receiver = os.getenv('MAIL_RECEIVER')

# OpenAI API key. Create one here: https://platform.openai.com/account/api-keys
openai.api_key = os.getenv('OPEN_API_KEY')


### Prompt sent to the GPT-3 model
prompt = """

Rewrite this email, and let the overall message stay the same but make sound {frustattion_level}% frustated, but make sure to NOT step too fare and make it sound threating or personally insulting in any way or form.

```
Dear OpenAI Support Team,

I am writing to you regarding a recent issue that I have been experiencing with my OpenAI account. I had attempted to upgrade to ChatGPTPlus, but encountered an issue where the HTTP Response status code 500 was returned multiple times over several days. Despite this, I decided to wait for a resolution and eventually upgraded my account when the issue was fixed.

However, during this time, I had also attempted to delete my account through the chatbot and was informed that it could take several working days. Subsequently, my account was disabled, and I was unable to create a new account using the same email or phone number.

As a result, I have been unable to use the service for the entire month and have continued to be charged for the subscription. I would like to request either the reactivation of my account or the complete deletion of it to allow me to create a new one. Additionally, I would appreciate a refund for the month in which I have been unable to use the service.

I understand that these issues may have been caused by technical difficulties on your end, and I am willing to work with you to resolve this situation as quickly and amicably as possible.

Thank you for your time and attention to this matter.

Sincerely,

INSERT NAME HERE
```
"""


# Generates the mail body using the GPT-3 model
def generate_mail_body():
  # Calculate the days passed since the starting date
  starting_date = datetime.datetime(2023, 5, 8)
  today = datetime.datetime.now()
  days_passed = (today - starting_date).days

  # Create the full prompt with the parameters
  full_prompt = prompt.format(frustattion_level=days_passed)




  # Get the completion from the GPT-3 model
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {
        "role": "user",
        "content": prompt
      }
    ]
  )

  result = completion.choices[0].message.content

  # ChatGPT keep giving a random frustation level here, so I just added this section as a suffix
  suffix = "\n\n----\nThis email has been writing with {frustattion_level}% frustation and has been written with ChatGPT. The amount of frustation increases 1% every day.\nI just want to use my own account again, thanks!".format(frustattion_level=days_passed)

  result = result + suffix

  return  result

def send_mail():
  body = generate_mail_body()

  em = EmailMessage()
  em['Subject'] = 'Deer OpenAI Support Team'
  em['From'] = email_sender
  em['To'] = email_receiver
  em.set_content(body)

  with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ssl.create_default_context()) as smtp:
      smtp.login(email_sender, email_password)
      smtp.sendmail(email_sender, email_receiver, em.as_string())

  print("Mail has been sent to: ", email_receiver)
  print("Mail body: ", body)


print(" --- Starting mail bot --- ")

# Want to send message at a different time checkout https://schedule.readthedocs.io/en/stable/
schedule.every().day.at("08:00").do(send_mail)

while True:
  schedule.run_pending()
  time.sleep(1)

