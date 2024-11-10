# data/texts.py
import random

# Function to select a random message from a list
def get_random_message(options):
    """Returns a random message from the provided list of options."""
    return random.choice(options)


# List of welcome messages
welcome_messages = [
    "💼 Welcome to the MoveMe Group family! \nWe're so glad you're here. 🥳\n\n"
    "If you're already part of our amazing team,\nlet's get you registered in just a few steps:\n\n"
    "1️⃣ Pick your department\n"
    "2️⃣ Enter your details (don’t worry, we’ll guide you!)\n"
    "3️⃣ Click 'Confirm' to join the team chat!\n\n"
    "When you're set, just tap below to get started! 👇",

    "🎉 Welcome to MoveMe Group! We're thrilled to have you here! \n\n"
    "If you’re part of our incredible team, let’s get you registered:\n\n"
    "1️⃣ Choose your department\n"
    "2️⃣ Fill in your details (we’ll walk you through it!)\n"
    "3️⃣ Confirm to join the team chat!\n\n"
    "When you’re ready, tap below to begin! 👇",

    "🚀 Welcome to the MoveMe Group family! We’re so excited to have you join us! 🎊\n\n"
    "Already part of the team? Let’s get your registration completed in three simple steps:\n\n"
    "1️⃣ Select your department\n"
    "2️⃣ Enter your details (we’ll make it easy!)\n"
    "3️⃣ Tap 'Confirm' to join our team chat!\n\n"
    "Ready to roll? Just tap below to start! 👇",

    "👋 Welcome aboard the MoveMe Group family! We're excited to have you with us! 🎉\n\n"
    "If you’re a part of our team, let's set you up in just a few steps:\n\n"
    "1️⃣ Pick your department\n"
    "2️⃣ Enter your details (we’ll guide you!)\n"
    "3️⃣ Hit 'Confirm' to jump into the team chat!\n\n"
    "All set? Tap below to begin! 👇"
]

name_error_messages = [
    "⚠️ Oops! That name format isn’t valid. Please enter your full name correctly. 👤",
    "🚫 Uh-oh! The name format seems incorrect. Could you please enter your full name accurately? ✍️",
    "😅 Hmm, that doesn’t look quite right! Please make sure to enter your full name correctly. ✅",
    "❗Oops! It seems like the name format is off. Kindly re-enter your full name as required. 📋"
]

dob_error_messages = [
    "🤔 Hmm, that doesn’t look like a valid date of birth. Please use the format **DD/MM/YYYY**. 📅",
    "⚠️ Oops! The date format seems incorrect. Please enter your date of birth in **DD/MM/YYYY** format. 📆",
    "🧐 That doesn’t look right! Make sure to use the **DD/MM/YYYY** format for your date of birth. 📅",
    "😅 Hmm, something seems off with the date. Could you please re-enter it in the format **DD/MM/YYYY**? ✅"
]

phone_error_messages = [
    "📱 Hmm, that number doesn’t seem right. Please make sure it’s correct and try again. 🔄",
    "🚫 Oops! That phone number doesn’t look correct. Could you double-check and try again? 📞",
    "🤔 Hmm, that number seems a bit off. Please verify it and enter it again. ✅",
    "📲 That doesn’t look like a valid number. Make sure it’s correct, and give it another try! 🔄"
]

name_prompt_messages = [
    "✍️ Please enter your full name:",
    "👤 Could you type in your full name?",
    "📝 Enter your full name as it appears on official documents:",
    "🔍 Please provide your full name:",
    "📛 What’s your full name? Please enter it below:"
]

dob_prompt_messages = [
    "📅 Enter your date of birth:\nPlease use the **DD/MM/YYYY** format.",
    "🎂 Could you enter your date of birth?\nUse the **DD/MM/YYYY** format, please.",
    "📆 Please type in your date of birth:\n**Format: DD/MM/YYYY**",
    "🗓️ What’s your date of birth?\nMake sure to enter it in **DD/MM/YYYY** format.",
    "🔢 Enter your date of birth (format: **DD/MM/YYYY**):"
]

phone_prompt_messages = [
    "📱 Enter your Uzbekistan phone number:\nPlease use the format **+998 XX XXX XXXX**.",
    "📞 Could you enter your Uzbekistan phone number?\nFormat: **+998 XX XXX XXXX**",
    "🔢 Please type in your Uzb phone number:\n**Format: +998 XX XXX XXXX**",
    "📲 What’s your phone number in Uzbekistan?\nMake sure it’s in **+998 XX XXX XXXX** format.",
    "☎️ Enter your phone number using this format: **+998 XX XXX XXXX**"
]

under_development_messages = [
    "🚧 Registration for this department is currently under development 🚧\n\n"
    "👨‍💻 For more information, please reach out to the admin on Telegram: @iamurod. He’ll be happy to assist you! 📬",

    "⚠️ This department's registration is still in progress! ⚠️\n\n"
    "💬 If you have any questions, feel free to contact our admin on Telegram at @iamurod. He’s here to help! 📩",

    "🚧 Hold tight! Registration for this department is under development. 🚧\n\n"
    "For assistance, you can message the admin on Telegram: @iamurod. He’ll gladly answer any questions! 📬",

    "⚙️ Registration for this department is being set up! ⚙️\n\n"
    "📲 Reach out to our admin at @iamurod on Telegram if you need more information. He’s happy to help! 💬"
]

approval_request_messages = [
    "📨 Your registration request has been sent to the admin for approval.\nPlease wait for the response. ⏳",

    "✅ Registration request submitted!\nThe admin is reviewing it now. Please hold tight for a response! 📬",

    "📩 Your request is on its way to the admin!\nHang tight—approval is in progress. You’ll hear back soon! ⏱️",

    "🚀 Your registration request has been sent for admin approval.\nPlease wait a moment; you’ll receive a response shortly! ⏳",

    "📬 Request sent! The admin will review your registration soon.\nPlease be patient while waiting for the response. ⏱️"
]

approval_success_messages = [
    "✅ Your registration has been approved!\nWelcome to MoveMe Group! 🎉",

    "🎉 Congratulations! Your registration is approved!\nWelcome aboard MoveMe Group! We’re excited to have you. 🚀",

    "✅ Approved! You’re now part of the MoveMe Group family!\nWe’re thrilled to have you with us. 🥳",

    "🌟 Your registration is successful!\nWelcome to MoveMe Group! Let’s get started on this journey together. 🎊",

    "🎊 You’re officially in! Your registration has been approved.\nWelcome to the MoveMe Group team! 🎉"
]

denial_messages = [
    "❌ Your registration has been denied.\nPlease contact support for more information: @iamurod.",

    "⚠️ Registration Denied\nFor more details, please reach out to support on Telegram: @iamurod. They’ll be happy to assist you! 📞",

    "❌ We're sorry, but your registration was not approved.\nIf you need further information, contact support at @iamurod. 📬",

    "🚫 Registration Unsuccessful\nPlease get in touch with our support team for assistance: @iamurod. They’re here to help! 💬",

    "❗ Your registration request was denied.\nFor assistance or clarification, reach out to support at @iamurod. 📩"
]

department_prompt_messages = [
    "🏢 Pick your department:",
    "🗂️ Please select your department from the options below:",
    "📋 Choose your department to proceed:",
    "🔍 Which department are you joining? Select below:",
    "🏛️ Pick the department you belong to:"
]

approval_sheet_messages = [
    "✅ User approved, and data successfully written to Google Sheets!",
    "📊 Approval complete! The user has been approved, and their details are now saved in Google Sheets.",
    "✅ User approved! Their data has been securely recorded in Google Sheets. 🎉",
    "📋 Approval successful! User data has been added to Google Sheets for future reference.",
    "🎉 User approved! Their information is now safely stored in Google Sheets.",
    "💾 Data saved! The user is approved, and their details are now available in Google Sheets. ✅"
]

denial_confirmation_messages = [
    "❌ User denied.",
    "🚫 User request denied.",
    "❗ User registration has been denied.",
    "⚠️ User was not approved.",
    "📛 Registration denied for the user.",
    "❌ The user has been denied access."
]

denial_messages = [
    "🚫 Unfortunately, the admin didn’t approve your registration request. If you believe this was an error, please contact @iamurod for assistance.",

    "😔 Your registration wasn’t approved by the admin. If you’re truly part of MoveMe Group, please reach out to the bot admin @iamurod.",

    "❌ We’re sorry, but your registration for MoveMe Group wasn’t approved. If you’re part of our team, connect with the bot admin @iamurod for help.",

    "💔 It looks like your registration for MoveMe Group didn’t go through. If you’re really part of our team, please reach out to the bot admin @iamurod for further assistance.",

    "📩 The admin hasn’t approved your registration request. If you’re a true member of MoveMe Group, connect with the bot admin @iamurod to sort this out.",

    "🚫 Sadly, your registration for MoveMe Group wasn’t approved. If you’re sure you belong to the MoveMe family, please message the bot admin @iamurod for clarification.",

    "❓ Your registration request was denied. If you’re a MoveMe Group team member, please reach out to our bot admin @iamurod to get this resolved.",

    "😕 We couldn’t approve your registration for MoveMe Group. If you believe this was an error and you’re part of the team, contact bot admin @iamurod for help.",

    "📢 Unfortunately, your registration wasn’t approved by the admin. If you’re part of MoveMe Group, please reach out to the bot admin @iamurod to confirm your membership.",

    "🚷 Your registration for MoveMe Group was not approved. If you’re a member of our team, please get in touch with the bot admin @iamurod for assistance.",

    "😔 It seems your registration request was denied. If you belong to the MoveMe Group family, feel free to reach out to our bot admin @iamurod to address this.",

    "🛑 Your registration wasn’t accepted. If you’re indeed part of MoveMe Group, kindly contact the bot admin @iamurod for support.",

    "❗️ It appears your registration approval was declined. If you’re with MoveMe Group, connect with our bot admin @iamurod to get this sorted out.",

    "⚠️ The admin did not approve your registration. If you’re a genuine member of MoveMe Group, please message the bot admin @iamurod for clarification.",

    "📝 Your registration wasn’t approved this time. If you’re really part of MoveMe Group, reach out to the bot admin @iamurod to get things cleared up.",

    "🤔 Your registration request didn’t pass approval. If you’re a member of MoveMe Group, connect with the bot admin @iamurod for further help.",

    "🚫 Unfortunately, your registration didn’t receive approval. If you’re part of the MoveMe Group family, please reach out to the bot admin @iamurod to resolve this."
]

