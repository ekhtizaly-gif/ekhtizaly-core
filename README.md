# Ekhtizaly Autonomous Core v2.0

نواة برمجية مفتوحة المصدر لأتمتة المهام وإدارة الوكلاء الأذكياء عبر بروتوكول FastMCP وبوابة واجهات برمجية موحدة.

## المكونات الأساسية (Core Architecture)

1. **FastMCP Servers (6 خوادم مخصصة)**:
   - `web`: استخراج ومعالجة بيانات الويب المتقدمة.
   - `browser`: أتمتة تفاعل المتصفح والتقاط لقطات الشاشة.
   - `memory`: ذاكرة دلالية محلية تعتمد على SQLite FTS5 مع خوارزمية BM25.
   - `intelligence`: تحليل الاتجاهات التقنية ومستودعات البرمجيات.
   - `automation`: موصلات الإشعارات (Telegram / Webhooks).
   - `crypto`: تدقيق العقود الذكية وفحص شبكة Base L2.

2. **بوابة الخدمة (REST API Gateway)**:
   - خادم مبني على FastAPI يعمل على المنفذ `8090`.
   - توثيق تفاعلي تلقائي عبر `/docs`.

3. **جدار الحماية والأمان (Sandbox Guard)**:
   - فحص الأوامر ومنع الأوامر التدميرية.
   - حماية من هجمات SSRF وتصفية البيانات الحساسة.

---

## متطلبات التشغيل (Quickstart)

```bash
# 1. تثبيت الحزم المطلوبة
pip install -r requirements.txt

# 2. إعداد المتغيرات البيئية
cp .env.example .env

# 3. تشغيل النظام
./scripts/start.sh
```

- للتحقق من تشغيل النظام: `GET http://localhost:8090/api/status`
- لإيقاف النظام: `./scripts/stop.sh`
- لتشغيل الاختبارات الشاملة: `python3 scripts/test_full_system.py`

---

## الترخيص والتواصل

مشروع حر ومفتوح المصدر للجميع.
- تيليجرام: [https://t.me/Ekhtizaly](https://t.me/Ekhtizaly)
