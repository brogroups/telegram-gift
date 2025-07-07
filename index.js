const { TelegramClient } = require('telegram');
const { StringSession } = require('telegram/sessions');

const apiId = 9306780; // my.telegram.org dan olingan
const apiHash = 'cc50c40ba0f16685e4b5fbe1001edf43'; // my.telegram.org dan olingan
const stringSession = new StringSession('1AgAOMTQ5LjE1NC4xNjcuNDEBu5Fyu9C8VVcxNaJV93jzl71VtY2th7eGPGrJ9NqQ/sbmJSoQxlU/rl9HGwWQ8nGbvxkScnfVf7lC2WaC1kPUG/eaugZEaovjO4Y58sh1UPxMxwF8Pq4MmtDQrmWOKV0/ff6+Z4xH8SCV3RwpUbEA/Wa3O2QpElFc12+4UZ29btHg81onIQZDapHUWE+kW24tFzwywg8Fg6DQUrdWwGxeeDpmkwOamHli/dY6Wbn5o19nhNOtjZDXuF2zgYu8s5pGYVyDzaRRiG4Iuj7UeKu6B3XEnAZhqUE4/Ql8aD3TRfwMsaB8tUDq74OfiZ+CyGgr4TWN2MckbO6mt9CQxQW9nM0='); 

(async () => {
    console.log('🔑 Telegram User API ga ulanmoqda...');
    const client = new TelegramClient(stringSession, apiId, apiHash, {
        connectionRetries: 5,
    });

    await client.connect();
    console.log('✅ Kirildi! Username:', (await client.getMe()).username);

 
    try {
        const result = await client.invoke(
            new client.api.payments.GetStarGifts({
                hash: 0
            })
        );

        if (result.gifts.length === 0) {
            console.log('❌ Hozircha hech qanday gift yo‘q.');
        } else {
            console.log('🎁 Mavjud giftlar:');
            result.gifts.forEach((gift, i) => {
                console.log(`\n#${i + 1}`);
                console.log('📝 Nomi:', gift.title);
                console.log('💲 Narxi:', gift.price);
                console.log('🆔 Gift ID:', gift.id);
            });
        }
    } catch (err) {
        console.error('⚠️ API xatosi:', err.message);
    }

    await client.disconnect();
})();
