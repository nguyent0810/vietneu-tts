# Nghiên cứu: chủ đề, hook, thumbnail + tiêu đề (26/10/2026)

**Vì sao làm.** Kênh MIMCK thử thư viện và thấy 3/4 khuôn thua của họ thua vì chủ đề hoặc CTR, nhưng thư viện chỉ có thẻ kỹ thuật hình (epic #37). Phần nghiên cứu do Muse làm theo đề của Lead. Lead đọc lại hai trang YouTube Help chính, rồi chuyển kết quả thành 26 thẻ:

| Nhóm | Số thẻ | Tiền tố id |
|---|---|---|
| Chủ đề | 8 | `chude_*` |
| Hook | 8 | `hook_*` |
| Thumbnail + tiêu đề | 10 | `thumb_*` |

## Bốn mức bằng chứng (trường `muc_bang_chung` của thẻ)
| Mức | Nghĩa | Dùng thế nào |
|---|---|---|
| YouTube Help | Tài liệu chính thức. Phần lớn chỉ nói cơ chế, không cho ngưỡng. | Tin được về cơ chế. |
| Đo được ngoài YouTube | Dataset hoặc đo lớn (1of10, NexTech Ads). Là tương quan, không phải nhân quả cho kênh mình. | Làm hướng đi, rồi kiểm trên kênh. |
| Tâm lý học gốc | Thí nghiệm về trí nhớ, tò mò (Rogers 1977, Loewenstein 1994, Zeigarnik 1927, Sadoski 2000, Lippmann 2019). Không đo CTR YouTube. | Chỉ để giải thích cơ chế. |
| Truyền miệng | Creator tự báo, không có đối chứng. | Chỉ là giả thuyết để thử. |

## Lead đã kiểm lại (26/10)
- [YouTube Help 12340300](https://support.google.com/youtube/answer/12340300):
  - nguyên văn "90% of the best-performing videos have custom thumbnails";
  - tiêu đề nên ngắn, từ quan trọng đặt gần đầu.
- [YouTube Help 16391400](https://support.google.com/youtube/answer/16391400), A/B Test & Compare:
  - thử tối đa 3 tiêu đề, thumbnail hoặc cặp; chọn theo watch time, không theo CTR;
  - Shorts không thử được; Live đã hẹn và Premiere đang hẹn cũng không;
  - xong trong 2 tuần; kết quả là Winner, Performed Same hoặc Inconclusive;
  - không có bản thắng thì bản tải lên đầu tiên được dùng.

## Đính chính và giới hạn
- Muse bỏ con số "3.200 thumbnail, tương phản tăng 38%" ghi ngày 24/10, vì không tìm lại được nguồn đủ tin. Thay bằng quy tắc kiểm ở 120–168 px có nguồn 1of10.
- **Điểm rơi giây 4–6** không phải ngưỡng YouTube công bố. Quan sát BUD (4,4–5,4 giây) chỉ có n=6.
- **Ngưỡng Shorts** "70–79% là ổn, 80%+ là mạnh" là số cộng đồng tự quan sát, không phải chuẩn.
- Chuẩn so sánh đáng tin nhất vẫn là "typical performance" của chính kênh trong Studio.
- **Mặt người trên thumbnail:** các nguồn mâu thuẫn nhau.
  - NexTech Ads phân tích lại hơn 300.000 video: có mặt và không mặt ngang nhau về trung bình.
  - Các phân tích A/B khác: mặt biểu cảm hơn vật thể 25–30% CTR.
  - Vì vậy đây là giả thuyết cần thử, chưa phải luật.
- Ví dụ kênh tiếng Việt chỉ có dữ liệu nội bộ. Muse không dùng số của kênh Việt khác vì không kiểm chứng được.

## Nguồn
```
rogers, kuiper & kirker 1977 | https://psycnet.apa.org/record/2000-07436-008
loewenstein 1994 (tổng quan) | https://psychology.town/motivation-emotion/understanding-curiosity-role-exploration/
lippmann và cộng sự 2019 | https://psycnet.apa.org/record/2018-62145-001
sadoski, goetz & rodriguez 2000 | https://psycnet.apa.org/record/2000-03003-007
zeigarnik (tổng quan) | https://www.renascence.io/behavioral-biases/zeigarnik-effect
youtube help - thumbnail & title tips | https://support.google.com/youtube/answer/12340300
youtube help - key moments for audience retention | https://support.google.com/youtube/answer/9314415
youtube help - a/b test titles & thumbnails | https://support.google.com/youtube/answer/16391400
1of10 - youtube shorts analytics | https://1of10.com/blog/youtube-shorts-analytics/
1of10 - best youtube thumbnails | https://1of10.com/blog/best-youtube-thumbnails/
nextech ads - face in thumbnails | https://nextechads.com/should-you-use-your-face-in-youtube-thumbnails-heres-what-the-data-actually-says-2026/
scihub101 - shorts strategy | https://scihub101.com/technology/how-to-create-a-youtube-shorts-strategy-that-works
retensis - shorts metrics | https://retensis.com/blog/youtube-shorts-analytics-metrics-explained
```

## Cách thẻ vào `pick`
- Mỗi thẻ có `chua_duoc`, chọn trong `chu_de`, `hook`, `ctr`, `nhip`. Khuôn khai `ly_do_thua` trùng với lý do nào thì nhận thẻ chữa lý do đó.
- 11 thẻ đã đánh `dung_that`, vì FS/BUD đang làm theo, nên `pick` của FS/BUD không gợi ý lại. Với kênh ngoài thì vẫn được gợi ý.
- Số đo thật của từng thẻ (A/B test, ô thử) ghi vào `bang_chung` khi có.
