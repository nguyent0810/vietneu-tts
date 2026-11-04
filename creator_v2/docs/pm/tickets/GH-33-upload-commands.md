# GH-33 · Lệnh upload pilot (chủ kênh chạy, cần YT_CREDS_DIR trong env)

Tất cả upload ở chế độ private + publishAt. Mỗi khối chạy `--dry` trước để xem có trùng lịch không, rồi mới bỏ `--dry`.

## 1. CK: 6 Short vào slot trống 03–05/11

```
python motion/stier/upload_one.py ck-binance-63-ty-rut-36-ty            "2026-11-03 12:00" --channel CK --dry
python motion/stier/upload_one.py ck-vang-sjc-140-trieu-chenh-14-trieu  "2026-11-03 19:00" --channel CK --dry
python motion/stier/upload_one.py ck-thue-xang-0-giam-1804              "2026-11-04 12:00" --channel CK --dry
python motion/stier/upload_one.py ck-lai-giam-05-tien-gui-80-ngan-han   "2026-11-04 19:00" --channel CK --dry
python motion/stier/upload_one.py ck-dien-giam-44-dong-20-nam           "2026-11-05 12:00" --channel CK --dry
python motion/stier/upload_one.py ck-ho-kinh-doanh-giam-30-thue         "2026-11-05 19:00" --channel CK --dry
```
Nếu giờ nào trùng với bài đã hẹn, dời sang slot trống gần nhất trong cùng ngày.

## 2. MIM: gỡ lịch 6 bài yếu (về private, không xóa), rồi dùng lại đúng giờ đó

```
python scripts/unschedule.py --channel MIM --slug mim-nam-hang-sap-nhap-1893 --slug mim-nhan-ma-2005 --slug mim-watson-ca-benh-gia-dinh --slug mim-con-ngua-da-con-ngua-da --slug mim-hoc-bang-hoi-tiec --slug mim-to-bip-bang-toan
```
(Lệnh trên không có `--apply` nên chỉ in danh sách. Xem đúng 6 bài rồi chạy lại kèm `--apply`.)

MIM không đi qua `upload_one.py`, vì script này chỉ nhận CL/CK. Đưa bài vào kho bằng `enqueue_mim.py`, rồi `publish_batch` upload private + publishAt:

```
python motion/stier/enqueue_mim.py mim-binance-20-phut-6-3-ty "2026-11-04 11:30" mim-android-20-tin-nhan-tu-than "2026-11-06 19:00" mim-cam-nhap-dien-thoai-cu-2027 "2026-11-08 17:00" mim-9-tren-10-ai-tu-lay-otp "2026-11-08 21:30" mim-sam-altman-ram-5-phan-tram "2026-11-09 17:00" mim-ve-tinh-google-4-chip-tpu "2026-11-09 19:00"
python scripts/publish_batch.py check --channel MIM
python scripts/publish_batch.py run --wait --channel MIM
```

## Đo
Đo mỗi bài ở mốc 24 h, 72 h và 7 ngày. Đánh giá cả đợt vào khoảng 12/11.
