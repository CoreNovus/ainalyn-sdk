## 你目前結構的最大問題：把「六角」畫成「洋蔥層」，而且角色有誤放

六角架構的核心是：

* **Application Core**：Domain + Application（Use Cases）
* **Ports**：核心定義的介面（inbound / outbound）
* **Adapters**：介面實作（例如 CLI、HTTP、DB、File、外部服務）
* **外層**：Framework/Driver（FastAPI、Click、DB client、SDK包裝）

你現在的圖，主要問題在這幾點：

---

## 1) Layer 5 “Public API & CLI” 放錯角色：它其實是 Adapter，不應是最上層「公共 API」

在六角架構裡：

* CLI / HTTP API / SDK Facade 都是 **Inbound Adapter**（輸入端適配器）
* 它們應該依賴 **Inbound Port（Use case interface）** 或直接呼叫 Application service（看你是否顯式定義 inbound port）

你把它獨立成一層「Public API」沒錯，但**命名上會誤導**：讓人以為這層是“核心 API”，其實它只是**介面入口**，不應包含業務流程。

✅ 建議改名：

* `Inbound Adapters: CLI, Python API (Facade)`
  並且保證它只做：
* parse args / request mapping
* 呼叫 use case
* format output / error mapping

---

## 2) Ports 層定義「Builder/Validator/Exporter」很危險：這些多半是“技術/流程名”，不是業務用例

在六角架構裡，**Ports 應以「用例需要什麼能力」來命名**，而不是以某個實作策略命名。

例如：

* `Writer`、`SchemaValidator`（Outbound port）這種偏技術可以
* 但 `Builder`/`Exporter`/`Validator` 很容易變成「什麼都塞進來」的雜物口

常見結果是：

* Ports 變成工具介面集合（utility interfaces）
* Adapter 變成業務邏輯所在地（反六角）

✅ 更可維護的做法是：

* Inbound ports 用 **Use case** 命名，例如：`BuildDefinition`, `ValidateDefinition`, `ExportWorkflow`
* Outbound ports 用**外部能力**命名，例如：`DefinitionRepository`, `SchemaRegistry`, `ArtifactWriter`, `Telemetry`

> 重點：Ports 是核心對外界的“需求介面”，不是“工具分類”。

---

## 3) “Validators” 出現三次（Domain Rules、Ports、Adapters）：責任邊界已經開始重疊

你圖裡同時存在：

* Domain 的 `Rules/Validators`
* Ports 的 `Validator Protocols`
* Adapters 的 `Validators`

這會導致長期最難修的問題：**到底哪裡才是權威的驗證？**

典型壞味道：

* Domain 有一套規則
* Adapter 又做一套（例如 schema validation）
* Application 又做一套（例如 use case validation）
* 結果改一條規則要改三處，還可能互相矛盾

✅ 嚴格建議（很重要）：
把 validation 分成兩類並明確放置：

1. **Domain validation（不可被繞過）**

* 例如：Workflow 必須 DAG、node id 唯一、必填欄位語意正確
  ➡️ 放在 **Domain**（Entity/Value Object/Domain service），且在建立/轉換時就 enforce

2. **Input/Schema validation（邊界防呆）**

* JSON schema、格式檢查、型別檢查、CLI 參數驗證
  ➡️ 放在 **Inbound Adapter**（或 application 的 request DTO validation）

Outbound 的 schema validator 若是 “對外部規格” 的檢查才算 outbound port。

---

## 4) “Builders” 放在 Adapters 很可疑：Builder 多半是 Application 的 orchestration（用例的一部分）

如果你說的 Builder 是：

* 把 AgentDefinition / Workflow 組裝起來
* 執行一系列規則、補預設、做關聯解析
  那它通常是 **Application service / Use case**（核心流程），不應放在 Adapter。

Adapter 的 builder 通常只負責：

* 把輸入（json/yaml/cli args）轉成 request DTO
* 或把外部資料結構轉成 domain

✅ 判斷準則：

* **會不會影響業務結果？會** → 放 Application/Domain
* **只是資料轉換/框架整合？** → 放 Adapter

---

## 5) “Errors” 放在 Adapters 也會變得亂：你需要「Domain error vs Use case error vs Adapter error」

六角架構通常會清楚分：

* Domain errors（不變的業務規則錯）
* Application errors（用例流程錯、依賴失敗的語意封裝）
* Adapter errors（HTTP 狀態碼、CLI exit code、第三方 SDK error）

你把 Errors 放在 Adapters，最後會出現：

* 核心丟出 adapter-specific exception
* 或外層到處 try/except

✅ 建議：

* Domain：定義 domain exceptions（或 Result types）
* Application：定義 use case errors（可包裝 domain error + infra error）
* Adapter：只做 mapping（HTTP 400/422/500，CLI exit 1/2）

---

## 6) 你現在的 Layer 1~5 其實「過度分層」：維護成本會上升

六角不是一定要畫 5 層。
你現在多層會帶來兩個風險：

* 目錄很多、但規則模糊 → 新人不知道該放哪
* “Ports/Adapters” 變成大型雜物層 → 什麼都能合理化放進去

✅ 更簡潔且更標準的結構（Python SDK 很常用）：

* `domain/`（entities, value objects, domain services, domain rules）
* `application/`（use cases, orchestrators, ports interfaces）
* `adapters/`

  * `inbound/`（cli, python facade, request mapping）
  * `outbound/`（writers, exporters, external clients）
* `infra/`（框架、第三方、組裝 wiring）

---

# 我給你一個「依照你現有名詞」的修正版對照

你目前：

* Layer 5: Public API & CLI
  ✅ 應改：**Inbound adapters**

你目前：

* Layer 4: Application (Use Cases, Services)
  ✅ OK（這是 application core 的一半）

你目前：

* Layer 3: Adapters (Builders, Errors, Validators, Exporters…)
  ⚠️ 建議拆成 inbound/outbound adapter，並把 “Builder” 視情況移到 application

你目前：

* Layer 2: Ports (Builder/Validator/Exporter protocols, Writer, SchemaValidator…)
  ⚠️ Ports 命名要改成 **Use case ports / External capability ports**，避免工具化

你目前：

* Layer 1: Domain (Entities, Rules, Validators)
  ✅ OK，但要確保 domain rules 是唯一權威

---

## 最後：這套會不會「有錯」？

不是錯到不能用，但以「嚴格六角」來說目前有三個高風險點會讓你越做越難維護：

1. **Validation 責任重疊**（最容易爆雷）
2. **Ports 命名偏工具分類**（會讓 adapter 變成業務邏輯集中地）
3. **Builder/Errors 放置可能導致核心依賴外層**（反向依賴）