# MANIFEST — провенанс медиа-мастеров «Инструкция к мечте»

> Цель: трассируемость каждого невоспроизводимого медиа-актива (модель, job-id, цена, цепочка производных).
> Вход: журнал решений `_navigator-prisma.md`; выход: этот файл — единственная карта media-source/.
> Правило: мастера write-once, в git не попадают (папка в .gitignore, файл MANIFEST — попадает); вторая копия каждого мастера — `~/_backups/2026-07-04-instrukciya-k-mechte/media-masters/` (md5 сверены 2026-07-04).

## masters/

| Файл | Что это | Происхождение | Производные |
|---|---|---|---|
| `2026-07-03_prisma-landscape_clean_master.png` | Пейзаж 2688×1512 после удаления UI/текста, до апскейла | Higgsfield image cleanup + repair-pass, job `061f4a27-2345-48d9-a8a4-e6edb0ffcab2` (платный) | → upscale-4k мастера |
| `2026-07-03_prisma-landscape_upscale-4k-raw_master.png` | Сырой выход 4K-апскейла 4096×2323 (до кропа 16:9) | Higgsfield 4K upscale, job `4e6cd596-8e5a-49c3-b022-6930ecf0b033`, ~2 кредита | → кроп 16:9 ниже; резерв для вертикалей/соцсетей |
| `2026-07-03_prisma-landscape_upscale-4k_master.png` | КАНОНИЧЕСКИЙ 4K-мастер 4096×2304, точный 16:9; Higgsfield media-id входа `cba4cf30-ae46-44ba-925b-451b0e7661dd` | Кроп raw-версии | → `public/images/prisma-landscape-1920.webp` (cwebp -q 85, 334 КБ, боевой фон); → start image будущих видео-генераций |
| `2026-07-03_prisma-hero_cloud-source_master.mp4` | Оригинальное облачное hero-видео Prisma 1924×1076, ~10 с (референс движения облаков) | Скачан с CloudFront-ссылки (зашита в `lab/2026-07-03_prisma-cloud-loop/prisma-capture.html`); ссылка может протухнуть | → cloud-loop захваты в lab/ |
| `2026-07-04_prisma-hero_higgsfield-user_master.mp4` | **ПОБЕДИВШЕЕ** hero-видео: 1920×1080, 24 fps, ~5 с, живые облака, сцена сохранена | Higgsfield, сгенерировано пользователем вручную (исходно `~/Downloads/hf_20260704_000750_d8ee3c2d-…mp4`, md5 `3622083d…`) | → `public/videos/prisma-hero-landscape-loop.{mp4,webm}` (2× slowdown + ~1.4 с crossfade стыка, ~10.13 с) + `prisma-hero-landscape-poster.jpg` |

## contact-sheets/

Визуальная память итераций (лёгкие jpg): `kling-contact` (отклонён — zoom/push-in, job `636039b4-…`, 7.5 кред.), `seedance-contact` (отклонён — другой пейзаж, job `cf6d9115-…`, 22.5 кред.; первый запуск `0f4dc30d-…` — ложный NSFW), `local-cloud-composite-contact` (локальный ffmpeg-композит, отклонён визуально), `user-video-contact` (победитель), `hero-loop-boundary-contact` (QC стыка цикла — открытая задача приёмки).

## Правила пополнения
1. Новый платный/невоспроизводимый актив → сюда с датой, job-id, ценой и цепочкой производных.
2. Отклонённые генерации: тяжёлые байты не храним, остаются contact sheet + строка с причиной отказа (уроки — в `lab/2026-07-03_prisma-cloud-loop/README.md`).
3. Перед заменой боевого энкода в `public/` — убедиться, что мастер-источник записан здесь и лежит в бэкапе.
