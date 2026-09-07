# مواقع ليبيا للمطورين 🇱🇾

Dataset مفتوح و**مستقل عن أي لغة أو Framework** يحتوي على بلديات ومدن ليبيا بأسماء عربية وإنجليزية، مع Slugs ثابتة، وملفات JSON وCSV، وLaravel Seeders وأمثلة جاهزة لعدة لغات.

[English README](README.md) · [دليل الربط](docs/INTEGRATION.md) · [الأمثلة](examples/README.md)

> **لا SDK، لا API Key، ولا Laravel مطلوب.** أي لغة تقدر تدير HTTP Request وتقرأ JSON تقدر تستخدم المشروع مباشرة.

## أسرع Integration

رابط ثابت ومحدد بالنسخة:

```text
https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json
```

مثال JavaScript:

```js
const locations = await fetch(
  'https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/municipalities.json'
).then(response => response.json());
```

ونفس الـDataset تشتغل مع:

**JavaScript / TypeScript، Python، PHP، Go، Java، C#/.NET، Dart/Flutter، Swift، Ruby، mobile apps، backend، frontend، scripts وقواعد البيانات.**

راجع [`docs/INTEGRATION.md`](docs/INTEGRATION.md) للشرح الكامل و[`examples/README.md`](examples/README.md) للأمثلة الجاهزة.

## المحتوى

| البيانات | العدد | الصيغ |
| --- | ---: | --- |
| البلديات | 141 | JSON + CSV + Laravel Seeder |
| المدن | 50 | JSON + CSV + Laravel Seeder |

كل سجل يستخدم نفس الـcontract:

```json
{
  "id": 94,
  "slug": "tripoli-center",
  "name_ar": "طرابلس المركز",
  "name_en": "Tripoli Center",
  "type": "municipality"
}
```

وموجود JSON Schema موحد في:

[`schemas/location.schema.json`](schemas/location.schema.json)

## الملفات

- [`data/municipalities.json`](data/municipalities.json)
- [`data/municipalities.csv`](data/municipalities.csv)
- [`data/cities.json`](data/cities.json)
- [`data/cities.csv`](data/cities.csv)
- [`data/endpoints.json`](data/endpoints.json) — يعطي التطبيق الروابط الثابتة والأعداد والنسخة الحالية
- [`data/manifest.json`](data/manifest.json)

## Production وLatest

للـProduction الأفضل تثبيت نسخة:

```text
https://raw.githubusercontent.com/ayagaidi/libyancityseeds/v1.1.0/data/cities.json
```

ولو تبي آخر تحديث على `master`:

```text
https://raw.githubusercontent.com/ayagaidi/libyancityseeds/master/data/cities.json
```

تثبيت Version يخلي تطبيقك ما يتأثرش بتحديثات Dataset بشكل مفاجئ.

## مصدر بيانات البلديات

الأسماء العربية للبلديات مجمعة من دليل البلديات المنشور لدى **وزارة الحكم المحلي الليبية**، وتمت مراجعته لهذا الإصدار بتاريخ **2026-09-07**:

https://www.lgm.gov.ly/municipalities

الأسماء الإنجليزية في المشروع هي Transliteration/Display Names للاستخدام البرمجي، ولا ندّعي أنها تهجئة إنجليزية رسمية معتمدة من جهة حكومية.

قائمة المدن الحالية مبنية على قائمة `CitySeeder.php` الأصلية التي كانت موجودة في هذا المستودع، وتم تحويلها إلى Dataset منظمة وإضافة أسماء إنجليزية وSlugs لها. وهي ليست ادعاء بأنها قائمة رسمية شاملة لكل المدن والقرى والمحلات في ليبيا.

للتفاصيل راجع [`DATA_SOURCES.md`](DATA_SOURCES.md).

## Laravel اختياري

لو مشروعك Laravel، عندك Seeders جاهزة:

```bash
php artisan db:seed --class=LibyaMunicipalitySeeder
php artisan db:seed --class=LibyaCitySeeder
```

الـSeeders تستخدم `upsert` لذلك يمكن تشغيلها أكثر من مرة بدون تكرار السجلات ذات نفس `slug`.

يوجد مثال Migration جاهز هنا:

[`examples/laravel-migrations.php`](examples/laravel-migrations.php)

ومثال API هنا:

[`examples/laravel-api.php`](examples/laravel-api.php)

لكن Laravel مش شرط لاستخدام المشروع؛ JSON/CSV هما الواجهة الأساسية.

## أمثلة لغات جاهزة

موجود أمثلة Copy/Paste لـ:

- JavaScript / TypeScript
- Python
- PHP
- Go
- Java
- C# / .NET
- Dart / Flutter
- Swift

ابدأ من [`examples/README.md`](examples/README.md).

## التحقق من جودة البيانات والـIntegration

GitHub Actions يتحقق آليًا من:

- صحة JSON وUTF-8؛
- عدم تكرار IDs أو Slugs؛
- وجود الحقول المطلوبة؛
- تطابق JSON مع CSV؛
- صحة نوع السجل `city` أو `municipality`؛
- تطابق الأعداد مع `manifest.json`؛
- تطابق `endpoints.json` مع النسخة؛
- تطابق JSON Schema مع شكل السجل؛
- صحة Syntax لمثال Python.

ويمكن تشغيل الفحص محليًا:

```bash
python3 scripts/validate_data.py
```

## المساهمة

أي تصحيح في اسم أو Transliteration مرحب به، والأفضل إرفاق مصدر موثوق. لو تغير فقط شكل الاسم المعروض، نحاول عدم تغيير `slug` لأن تطبيقات قد تعتمد عليه.

راجع [`CONTRIBUTING.md`](CONTRIBUTING.md).

## مبادئ المشروع

- المشروع Language-agnostic من الأساس؛ JSON/CSV هما الواجهة الرئيسية.
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
