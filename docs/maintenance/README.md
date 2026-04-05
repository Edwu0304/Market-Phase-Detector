# 維運手冊總覽

本資料夾是這個專案的維運入口，目的是讓後續接手的人不用先把整個專案讀完，仍能快速理解系統怎麼運作、資料從哪裡來、程式各自負責什麼，以及從抓資料到上線 UI 的完整流程。

## 建議閱讀順序

1. [`系統總覽與程式碼地圖.md`](/D:/repo/python/Market%20Phase%20Detector/.worktrees/strategy-map-redesign/docs/maintenance/系統總覽與程式碼地圖.md)
2. [`指標與API資料來源.md`](/D:/repo/python/Market%20Phase%20Detector/.worktrees/strategy-map-redesign/docs/maintenance/指標與API資料來源.md)
3. [`資料流程與上線流程.md`](/D:/repo/python/Market%20Phase%20Detector/.worktrees/strategy-map-redesign/docs/maintenance/資料流程與上線流程.md)

## 這個專案目前在做什麼

- 每月整理台灣與美國的總體資料
- 先產生「網站總相位」
- 再用三個獨立鏡頭分別產生三位作者的判讀
- 輸出成靜態資料檔與靜態網站
- 透過 Cloudflare Pages 對外提供首頁、台灣頁、美國頁

## 目前系統的關鍵原則

- 首頁顯示的是「網站總相位」，不是任何一位作者的結論
- 三位作者各自獨立判讀，不共用相位、不共用時間軸
- 歷史資料只顯示台灣與美國都能對齊的真實月份
- UI 不是即時查 API，而是讀取專案產出的 `data/*.json`

## 維運時最常用的三個命令

```bash
pytest -q
python -m market_phase_detector.cli
npx wrangler pages deploy dist --project-name market-phase-detector
```
