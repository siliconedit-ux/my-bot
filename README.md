# CS Web – Dust II (onlayn)
1. Node.js o'rnating (nodejs.org), keyin shu papkada:  npm install  →  npm start
2. Brauzerda http://localhost:3000 oching. Telefon/do'stlar bir xil Wi‑Fi'da bo'lsa: http://KOMPYUTER_IP:3000
3. Internetga chiqarish: papkani GitHub'ga yuklab, Render.com / Railway.app da "Web Service" qiling (Build: npm install, Start: npm start). GitHub Pages ishlamaydi – server kerak.
Offlayn (botlar bilan) o'yin: public/index.html ni to'g'ridan-to'g'ri ochsangiz ham bo'ladi.

## Netlify + Render
Netlify faqat statik sayt (server ishlamaydi). Serverni Render.com ga qo'ying, keyin public/config.js ichiga wss://SIZNING-APP.onrender.com yozib, public papkani Netlify'ga yuklang.
Netlify'ga faqat `public` papka ichidagi fayllarni yuklang (index.html ildizda bo'lsin).
