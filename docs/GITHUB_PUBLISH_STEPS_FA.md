# راهنمای انتشار پروژه در GitHub (گام‌به‌گام)

این پوشه یک پروژه آماده بارگذاری است. هنوز Repository عمومی در حساب شخصی GitHub ساخته نشده؛ برای ساخت لینک عمومی باید خودت وارد حساب شوی.

## گام ۱: دانلود و استخراج

1. فایل ZIP پروژه را از ChatGPT دانلود کن.
2. در Windows روی فایل راست‌کلیک کن و **Extract All…** را بزن.
3. پوشه `glassdollar-corporate-technology-intelligence-demo` را باز کن. داخل آن باید `README.md` و پوشه‌های `data`، `src`، `tests`، `sql` و `docs` را ببینی.

## گام ۲: ساخت Repository

1. به https://github.com برو و وارد حساب خودت شو.
2. از علامت `+` بالا سمت راست، گزینه **New repository** را انتخاب کن.
3. در Repository name بنویس: `glassdollar-corporate-technology-intelligence-demo`
4. توضیح (Description) را وارد کن: `Synthetic portfolio prototype for company-technology relationship intelligence, data quality and evidence-based review.`
5. گزینه **Public** را انتخاب کن تا استخدام‌کننده بتواند پروژه را ببیند.
6. گزینه‌های Add a README، .gitignore و License را انتخاب نکن؛ این فایل‌ها از قبل داخل پوشه پروژه هستند.
7. روی **Create repository** کلیک کن.

## گام ۳: بارگذاری فایل‌ها از طریق مرورگر

1. در Repository تازه‌ساخته‌شده، روی **Add file** کلیک کن.
2. **Upload files** را انتخاب کن.
3. محتویات پوشه `glassdollar-corporate-technology-intelligence-demo` را انتخاب کن؛ خود پوشه والد را به‌صورت تودرتو آپلود نکن. فایل‌ها و پوشه `.github` را هم بفرست. اگر انتخاب فایل مخفی دشوار بود، `.github/workflows/tests.yml` را بعداً جداگانه اضافه کن.
4. فایل‌ها را به ناحیه Drag & Drop بکش.
5. صبر کن تا بارگذاری کامل شود.
6. در قسمت Commit changes بنویس: `Add Corporate Technology Intelligence portfolio prototype`
7. روی **Commit changes** کلیک کن.

## گام ۴: بررسی Repository

1. مطمئن شو `README.md` در صفحه اصلی نمایش داده می‌شود.
2. پوشه‌های `data`، `src`، `tests`، `sql` و `docs` دیده می‌شوند.
3. وارد تب **Actions** شو؛ Workflow تست‌های Python را اجرا می‌کند.
4. اگر سبز شد، تست‌های خودکار با موفقیت اجرا شده‌اند.

## گام ۵: کپی لینک برای فرم GlassDollar

1. آدرس Repository را از نوار آدرس مرورگر کپی کن. شکل آن باید مانند زیر باشد:
   `https://github.com/YOUR-USERNAME/glassdollar-corporate-technology-intelligence-demo`
2. به فرم GlassDollar برگرد.
3. لینک را در فیلد **Please share a link to your GitHub, portfolio or a data project you've built** قرار بده.
4. لینک را در یک پنجره ناشناس باز کن تا مطمئن شوی بدون ورود به GitHub قابل مشاهده است.

## گام ۶: اجرای پروژه روی Windows (اختیاری ولی برای مصاحبه مفید)

1. Python 3.10 یا جدیدتر نصب باشد.
2. در پوشه پروژه، روی نوار آدرس File Explorer کلیک کن، `cmd` بنویس و Enter بزن.
3. دستورها را یکی‌یکی اجرا کن:

```bat
py -3 --version
py -3 src\validate_and_score.py --as-of 2026-11-13
py -3 src\build_dashboard.py
py -3 -m unittest discover -s tests -v
```

4. فایل `output\report.html` را با دوبار کلیک در مرورگر باز کن.

## نکات مهم برای درخواست شغلی

- داده‌های پروژه ساختگی‌اند؛ این موضوع را پنهان نکن.
- این نمونه را به‌عنوان **Self-initiated portfolio prototype** معرفی کن.
- ادعا نکن پروژه شامل scraping واقعی، LLM extraction یا داده‌های واقعی GlassDollar است؛ این نسخه چنین قابلیت‌هایی ندارد.
- اگر در مصاحبه درباره کار خودت پرسیدند، مدل داده، کنترل کیفیت، تشخیص خطا، امتیازدهی توضیح‌پذیر، human review و منطق تجاری را توضیح بده.
- نام کاربری و رمز GitHub را در چت یا فایل پروژه وارد نکن.
