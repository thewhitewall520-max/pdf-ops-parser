# pdf-ops-parser — 架構審計報告

> **審計人員：** 艾露莎 ⚔️  
> **審計日期：** 2026-05-20  
> **專案版本：** v0.1.0  
> **專案路徑：** `/Users/aq/.openclaw/workspace/projects/pdf-ops-parser`

---

## 📊 總體評估

| 審計層面 | 評級 | 說明 |
|----------|------|------|
| Parser layer separation | 🟡 良好（有小問題） | 職責基本清晰，但存在代碼重複 |
| API contract consistency | 🟡 良好（有小問題） | Route 定義正確，error handling 覆蓋完整 |
| CLI consistency | 🟠 需改進 | `--template` flag 為死參數，CLI/API 功能不對稱 |
| Test blind spots | 🔴 缺口明顯 | 缺少 multiple parsers、classify、CLI integration 測試 |
| Scope creep risk | 🟢 無風險 | 無 TODO、無 WIP、無超出 MVP 內容 |

**Overall：** 🟡 **不阻塞 public release，但建議處理 CRITICAL 和 HIGH 問題後再發布。**

---

## 🔴 CRITICAL — 必須修復

### C-01：YAML 模板系統為空殼，`--template` 為死參數

| 項目 | 詳細 |
|------|------|
| 位置 | `cli/main.py:34-36`, `cli/main.py:57-65` |
| 嚴重度 | **CRITICAL** |

**問題描述：**

CLI 接受 `--template` 參數（文檔和 help text 均有提及），但模板值僅用於跳過 auto-detect 錯誤提示——**從未被實際載入、解析或應用到任何 parse 邏輯**。

`templates/` 目錄下四個 YAML 文件（`invoice.default.yaml`, `shipping.default.yaml`, `ozon.settlement.yaml`, `wildberries.report.yaml`）定義了欄位 regex patterns，但代碼中：
- 無任何 `import yaml` 或模板載入邏輯
- 所有三個 parser（`parse_invoice.py`, `parse_shipping.py`, `parse_settlement.py`）直接硬編碼 regex patterns
- README 描述為 "Extensible YAML template system" 但實際不存在

**影響：** 文檔誤導使用者；`pyyaml` dependency 無用；模板文件成為 dead code。

**建議修復方案：**

兩個選擇：
1. **短期（推薦）：** 刪除 `--template` 參數、`templates/` 目錄、`pyyaml` dependency；更新 README 移除模板相關描述
2. **長期：** 實現真實的模板引擎——從 `templates/` 載入 YAML，動態註冊解析規則

---

## 🟠 HIGH — 建議在發布前修復

### H-01：parse_settlement 和 parse_invoice 之間的 regex 交叉污染

| 項目 | 詳細 |
|------|------|
| 位置 | `packages/parser/parse_settlement.py:47-49` |
| 嚴重度 | **HIGH** |

**問題描述：**

`parse_settlement` 的 `total_sales` regex 包含 `(?i)(?:total\s+sales|выручка|продажи|total).*?([\d,]+\.?\d*)`，最後一個 alternative `total` 過於寬鬆。當用 settlement parser 解析 invoice PDF 時，會誤捕 "Total: $100.00" 為 `total_sales`。

**實測驗證：**
```
parse_settlement(invoice_pdf) → total_sales = 100.00  # 錯誤！
```

**建議修復方案：**
- 對 `total_sales` regex 中的 `total` 增加上下文限制，如 `(?i)(?:total\s+sales|выручка|продажи)`（移除獨立的 `total`）
- 或增加分類檢查：在 parser 前驗證 `classify()` 結果，不匹配則拒絕

---

### H-02：`_find_first` 和 `_find_decimal` 在多個 parser 中重複定義，行為不一致

| 項目 | 詳細 |
|------|------|
| 位置 | `packages/parser/parse_invoice.py:44-56` / `packages/parser/parse_shipping.py:30-35` / `packages/parser/parse_settlement.py:78-90` |
| 嚴重度 | **HIGH** |

**問題描述：**

三個 parser 各自定義了功能相同但行為不一致的私有輔助函數：

| 函數 | parse_invoice | parse_shipping | parse_settlement |
|------|:---:|:---:|:---:|
| `_find_first` | `group=1`, 無 `re.I` | `group=1`, 有 `re.I` | `group=1`, 無 `re.I` |
| `_find_decimal` | ✅ | ❌ | ✅（不同實現）|
| `_parse_money` | ✅ | ❌ | ❌ |
| `_find_date` | ❌ | ❌ | ✅ |

**建議修復方案：**
- 建立 `packages/parser/_helpers.py`，統一這些函數
- 所有 parser 從同一處導入

---

### H-03：`parse_settlement` 同時處理 Ozon 和 Wildberries，兩者邏輯混合

| 項目 | 詳細 |
|------|------|
| 位置 | `packages/parser/parse_settlement.py` |
| 嚴重度 | **HIGH** |

**問題描述：**

`parse_settlement()` 使用同一套 regex 同時處理 Ozon 和 Wildberries 結算單，通過 `re.search(r"(?i)\bozon\b|озон", text)` 區分平台。但兩個平台的報表格式可能差異很大——Ozon 和 Wildberries 使用不同的俄語術語，欄位名稱不同。

`templates/wildberries.report.yaml` 中的 regex 定義與 `parse_settlement.py` 中的硬編碼不一致：
- Template 中 `total_sales` pattern 為 `(?i)(?:total\s+sales|выручка|продано)`
- Code 中為 `(?i)(?:total\s+sales|выручка|продажи|total)`
- Template 中 seller_id pattern 為 `wb\s*(id|артикул)` 
- Code 中為 `seller\s*(?:id|#|number):?\s*(\S+)`

**建議修復方案：**
- 考慮將 `parse_settlement` 拆分為 `parse_ozon` / `parse_wildberries`，或在內部按 platform 分支加載不同 regex sets
- 使 YAML 模板中的 regex 與 code 保持一致

---

## 🟡 MEDIUM — 發布前建議處理

### M-01：缺少 `__init__.py` 可能導致某些打包工具出錯

| 項目 | 詳細 |
|------|------|
| 位置 | `apps/`, `cli/`, `packages/` (頂層) |
| 嚴重度 | **MEDIUM** |

**問題描述：**

`apps/`、`cli/`、`packages/` 三個頂層目錄缺少 `__init__.py`。Python 3.3+ 支持 implicit namespace packages，但某些打包工具和 older pip 版本可能不兼容。`pyproject.toml` 中使用了 `setuptools.packages.find`，理論上能找到，但在 edge cases（如 editable install）中可能失敗。

**建議修復方案：**
- 添加 `apps/__init__.py`、`cli/__init__.py`、`packages/__init__.py`（空文件即可）

---

### M-02：CLI `parse` 命令中 settlement 解析路徑使用延遲導入

| 項目 | 詳細 |
|------|------|
| 位置 | `cli/main.py:76-78` |
| 嚴重度 | **MEDIUM** |

**問題描述：**

```python
elif resolved_type in (DocType.OZON_SETTLEMENT.value, DocType.WILDBERRIES_REPORT.value):
    from packages.parser.parse_settlement import parse_settlement  # 延遲導入
```

其他分支使用頂層導入，唯獨 settlement 在 if 內部導入，風格不一致。

**建議修復方案：**
- 將 `from packages.parser.parse_settlement import parse_settlement` 移至文件頂部

---

### M-03：API route 中 output_format 使用字串比對而非 Enum

| 項目 | 詳細 |
|------|------|
| 位置 | `apps/api/routes/parse.py:77-81` |
| 嚴重度 | **MEDIUM** |

**問題描述：**

```python
out_fmt = output_format.lower()
out_suffix = {
    OutputFormat.EXCEL.value: ".xlsx",
    OutputFormat.CSV.value: ".csv",
    OutputFormat.JSON.value: ".json",
}.get(out_fmt, ".xlsx")
```

`output_format` 來自 `Form` 參數，默認值為字串 `"excel"`，但 `OutputFormat.EXCEL.value` 是 `"xlsx"`。雖然 dictionary lookup 將兩者視為不同 key，但 `"excel"` 不在映射中會 fallback 到 `.xlsx`——這恰好是對的結果，但依賴巧合而非設計。

**建議修復方案：**
- 使用 `OutputFormat` enum 作為參數類型：`output_format: OutputFormat = Form(OutputFormat.EXCEL)`
- API 默認值應與 Enum 值一致

---

### M-04：API 解析成功後立即刪除輸出文件

| 項目 | 詳細 |
|------|------|
| 位置 | `apps/api/routes/parse.py:92-93` |
| 嚴重度 | **MEDIUM** |

**問題描述：**

```python
finally:
    Path(tmp_path).unlink(missing_ok=True)
    if out_path:
        out_path.unlink(missing_ok=True)
```

`FileResponse` 是 async streaming——可能在文件被刪除時尚未完成傳輸。雖然 FastAPI 通常會在返回後才執行 finally，但這依賴於實現細節。

**建議修復方案：**
- 使用 `FileResponse` 的 `background` 參數或在 response 完成後通過 middleware cleanup
- 或使用 `tempfile` 的 `delete=False` + 定時清理 job

---

## 🔵 LOW — 優化建議

### L-01：`classify_doc.py` 中的 `re.search` 使用未預編譯 regex

| 項目 | 詳細 |
|------|------|
| 位置 | `packages/parser/classify_doc.py:39` |
| 嚴重度 | **LOW** |

`_SIGNATURES` 字典存儲 regex 字串而非預編譯的 `re.compile` 物件，每次 `classify()` 調用會重複編譯。

**建議：** 將 patterns 預編譯或在加載時編譯。

---

### L-02：測試中使用 `fpdf` 動態生成 PDF，增加測試時間

| 項目 | 詳細 |
|------|------|
| 位置 | `tests/test_parse_invoice.py`, `tests/test_parse_settlement.py`, `tests/test_extract_text.py` |
| 嚴重度 | **LOW** |

每個測試案例都動態生成 PDF（通過 `fpdf.FPDF()`），而非使用 `samples/` 目錄中的預生成 PDF。這增加了測試時間且無法測試真實 PDF 場景。

**建議：** 保留動態生成用於 CI，但添加對 `samples/` 的集成測試。

---

### L-03：`normalize.py` 中 `_normalize_settlement` 邏輯冗餘

| 項目 | 詳細 |
|------|------|
| 位置 | `packages/parser/normalize.py:96-107` |
| 嚴重度 | **LOW** |

```python
return rows if len(rows) > 1 else [
    {"type": "summary", ...}
]
```

當 `transactions` 為空且 summary 數據不全時，這會返回一個僅有 summary 的 row，邏輯分支難以閱讀。

**建議：** 重構為更清晰的 if-else 結構。

---

## 📋 Test Blind Spots — 缺失測試覆蓋

### 缺失的測試文件/類別：

| 缺失 | 影響 | 優先級 |
|------|------|--------|
| `test_classify_doc.py` | `classify_doc.py` 完全未被測試 | **HIGH** |
| `test_parse_shipping.py` | `parse_shipping.py` 完全未被測試 | **HIGH** |
| `test_normalize.py` | `normalize.py` 完全未被測試 | **HIGH** |
| `test_export_csv.py` | CSV export 未被測試 | **MEDIUM** |
| `test_export_json.py` | JSON export 未被測試 | **MEDIUM** |
| `test_extract_tables.py` | Table extraction 未被測試 | **MEDIUM** |
| `test_cli.py` | CLI commands 無集成測試 | **MEDIUM** |
| `test_api.py` | API endpoints 無集成測試 | **LOW** |
| `test_cross_parser.py` | 跨 parser 邊界測試（H-01） | **HIGH** |

### 現有測試的缺口：

| 缺失場景 | 相關 parser | 優先級 |
|----------|-------------|--------|
| Invoice with no tables（純文字帳單） | `parse_invoice` | **MEDIUM** |
| Invoice with multi-page tables | `parse_invoice` | **MEDIUM** |
| Shipping with no tracking events | `parse_shipping` | **MEDIUM** |
| Wildberries settlement（僅測試了 Ozon） | `parse_settlement` | **HIGH** |
| Non-PDF filename with `.pdf` extension | `extract_text` | **LOW** |
| Extremely large PDF (>100 pages) | `extract_text` | **LOW** |
| PDF with non-ASCII content (e.g., Cyrillic) | all | **MEDIUM** |

---

## 🔍 附加發現

### A-01：`pyyaml` 依賴未使用

| 項目 | 詳細 |
|------|------|
| 位置 | `pyproject.toml:36` |
| 說明 | `pyyaml>=6.0` 列為依賴但代碼中無任何 `import yaml`。與 C-01 相關聯。 |

### A-02：Dockerfile 安裝 dev dependencies 到 production image

| 項目 | 詳細 |
|------|------|
| 位置 | `Dockerfile:13` |
| 說明 | `RUN pip install --no-cache-dir -e ".[dev]"` 將 pytest、ruff 和 coverage 安裝到生產容器中，不必要的安全攻擊面。 |

### A-03：Dockerfile COPY 順序導致 cache 失效

| 項目 | 詳細 |
|------|------|
| 位置 | `Dockerfile:8-10` |
| 說明 | `COPY packages/ packages/` 和 `COPY cli/ cli/` 在 `RUN pip install` 之前——應該先 `COPY pyproject.toml`，`RUN pip install`，然後再 COPY 源碼，以利用 Docker layer cache。當前順序每次代碼變動都會重新安裝依賴。 |

---

## 🚦 是否阻擋 Public Release？

**結論：否，但附帶條件。** 🟡

| 條件 | 說明 |
|------|------|
| ✅ 必須修復 | 無（無 CRITICAL blocker 阻止功能正常運行） |
| ⚠️ 強烈建議 | C-01（刪除死 `--template` 參數或實現） |
| ⚠️ 強烈建議 | H-01（regex 交叉污染修復） |
| 📝 建議 | H-02, H-03 和其他 MEDIUM 項目在首個 patch release 中處理 |
| 📝 建議 | 補充測試覆蓋（尤其是 `classify_doc` 和 `parse_shipping`） |

**核心功能完整，API/CLI 可用，測試全部通過。最大的已存在問題是文檔與實現不一致（模板系統），而最危險的 Bug 是跨 parser regex 污染。**
