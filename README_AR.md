# مواقع ليبيا للمطورين 🇱🇾

Dataset مفتوح ومهيأ للاستخدام البرمجي يحتوي على **بلديات ومدن ليبيا** بأسماء عربية وإنجليزية، مع Slugs ثابتة، وملفات JSON وCSV، وLaravel Seeders وأمثلة API.

[English README](README.md)

## لماذا هذا المشروع؟

في مشاريع ليبية كثيرة نحتاج نفس البيانات: قائمة البلديات أو المدن في التسجيل، العناوين، التوصيل، المتاجر، الأنظمة المصرفية، الخدمات الحكومية وغيرها. بدل ما كل مطور يعيد كتابة القائمة من الصفر، الهدف هنا يكون عندنا مصدر تقني واضح وقابل للمساهمة والتحقق.

## المحتوى

| البيانات | العدد | الصيغ |
| --- | ---: | --- |
| البلديات | 141 | JSON + CSV + Laravel Seeder |
| المدن | 50 | JSON + CSV + Laravel Seeder |

كل سجل يحتوي على:

```json
{
  "id": 94,
  "slug": "tripoli-center",
  "name_ar": "طرابلس المركز",
  "name_en": "Tripoli Center",
  "type": "municipality"
}
```

## الملفات

- [`data/municipalities.json`](data/municipalities.json)
- [`data/municipalities.csv`](data/municipalities.csv)
- [`data/cities.json`](data/cities.json)
- [`data/cities.csv`](data/cities.csv)
- [`data/manifest.json`](data/manifest.json)

## مصدر بيانات البلديات

الأسماء العربية للبلديات مجمعة من دليل البلديات المنشور لدى **وزارة الحكم المحلي الليبية**، وتمت مراجعته لهذا الإصدار بتاريخ **2026-09-07**:

https://www.lgm.gov.ly/municipalities

الأسماء الإنجليزية في المشروع هي Transliteration/Display Names للاستخدام البرمجي، ولا ندّعي أنها تهجئة إنجليزية رسمية معتمدة من جهة حكومية.

قائمة المدن الحالية مبنية على قائمة `CitySeeder.php` الأصلية التي كانت موجودة في هذا المستودع، وتم تحويلها إلى Dataset منظمة وإضافة أسماء إنجليزية وSlugs لها. وهي ليست ادعاء بأنها قائمة رسمية شاملة لكل المدن والقرى والمحلات في ليبيا.

للتفاصيل راجعي [`DATA_SOURCES.md`](DATA_SOURCES.md).

## الاستخدام مع Laravel

بعد نسخ مجلد `data` والـSeeders إلى مشروع Laravel:

```bash
php artisan db:seed --class=LibyaMunicipalitySeeder
php artisan db:seed --class=LibyaCitySeeder
```

الـSeeders تستخدم `upsert` لذلك يمكن تشغيلها أكثر من مرة بدون تكرار السجلات ذات نفس `slug`.

يوجد مثال Migration جاهز هنا:

[`examples/laravel-migrations.php`](examples/laravel-migrations.php)

ومثال API هنا:

[`examples/laravel-api.php`](examples/laravel-api.php)

مثلاً:

```http
GET /api/libya/municipalities?lang=ar
GET /api/libya/municipalities?lang=en
GET /api/libya/cities?lang=ar
```

## Frontend / JavaScript

يمكن قراءة JSON مباشرة من GitHub أو تنزيله داخل المشروع. مثال جاهز:

[`examples/javascript-fetch.js`](examples/javascript-fetch.js)

## التحقق من جودة البيانات

GitHub Actions يتحقق آليًا من:

- صحة JSON وUTF-8؛
- عدم تكرار IDs أو Slugs؛
- وجود الحقول المطلوبة؛
- تطابق JSON مع CSV؛
- صحة نوع السجل `city` أو `municipality`؛
- تطابق الأعداد مع `manifest.json`.

ويمكن تشغيل الفحص محليًا:

```bash
python3 scripts/validate_data.py
```

## المساهمة

أي تصحيح في اسم أو Transliteration مرحب به، والأفضل إرفاق مصدر موثوق. لو تغير فقط شكل الاسم المعروض، نحاول عدم تغيير `slug` لأن تطبيقات قد تعتمد عليه.

راجع [`CONTRIBUTING.md`](CONTRIBUTING.md).

## مبادئ المشروع

- العربي جزء أساسي من البيانات، مش إضافة ثانوية.
- البلدية والمدينة مفهومين مختلفين ونحتفظ بهم في Dataset منفصلة.
- الـSlugs هدفها الاستقرار للاستخدام في APIs وقواعد البيانات.
- أي تحديث إداري مهم لازم يكون موثق بمصدر.
- المشروع لا يحتوي على أي بيانات شخصية أو بيانات عملاء.

## المطورة

**Aya Aljaidi** — Laravel / Full-Stack Developer — Tripoli, Libya  
GitHub: [@ayagaidi](https://github.com/ayagaidi)

## الترخيص

الكود والتوثيق الأصلي في المشروع تحت ترخيص [MIT](LICENSE). تفاصيل مصادر البيانات موجودة في [`DATA_SOURCES.md`](DATA_SOURCES.md).
