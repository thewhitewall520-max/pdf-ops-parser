# pdf-ops-parser Sprint Task Plan

## 階段鎖定

① 架構審計（艾露莎） → ② CI（馬卡羅夫） → ③ Release Readiness（米拉珍） → ④ 驗收（格雷）

## Task 清單

| Task ID | Owner | Phase | 描述 | 依賴 |
|---------|-------|-------|------|------|
| POP-001 | erza | ① 審計 | 架構審計報告 | — |
| POP-002 | makarov | ② CI | GitHub Actions CI pipeline | POP-001（審計無改動，無需等） |
| POP-003 | mirajane | ③ Release | Release readiness checklist | POP-001（審計無改動，無需等） |
| POP-004 | gray | ④ 驗收 | 整合驗收+報告 | POP-002, POP-003 |

## 執行順序

POP-001 + POP-002 + POP-003 可並行
POP-004 在 POP-002 + POP-003 完成後

## 輸出

- 艾露莎 → 架構審計文件
- 馬卡羅夫 → `.github/workflows/ci.yml`
- 米拉珍 → README 更新 + release checklist
- 格雷 → 驗收報告
