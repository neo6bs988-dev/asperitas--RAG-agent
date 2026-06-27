---
source_id: ASP-P6-D1F4C9FC8737
source_priority: P6
source_type: benchmark_operating_intelligence
confidentiality: internal
license_status: verify_before_ingestion
evidence_use: benchmark_only_not_asperitas_fact
ingestion_status: extracted_to_markdown
verification_status: source_attached_not_external_verified
---

# Asperitas AI/Bio-AI Development Process Benchmark Report

> Boundary: P6 benchmark operating intelligence only. This markdown is extracted from the attached PDF and must not be used as Asperitas factual evidence.

## Page 1

<!-- source_ref: ASP-P6-D1F4C9FC8737 p.1 -->

Asperitas AI/Bio-AI Development Process Benchmark Report | Internal Working Draft
Page 1
 AI / Bio-AI 개발 프로세스 벤치마킹 보고서
 OpenAI, Anthropic, Google DeepMind, DeepSeek, LLM/Agent/RAG/AI-Ops/Bio-AI 기업 공개 자료 기반
 목적: Asperitas 개발 과정과 비교 분석하고, 벤치마킹 가능한 개발 원칙을 DB화하여 독자적 Biological Intelligence Factory Workflow로 고착화하기 위한
 내부 작업 문서
 Generated: 2026-06-27 | Classification: Internal Working Draft | Language: Korean
Executive bottom line: 이 문서의 결론은 단순하다. 최상위 AI 회사와 Bio-AI 회사들의 공통 개발 원리는 “모델”이 아니라 “검증 가능한 루프”다. 소스/데이터 -> 스키마/도구 -> 에이전트/워크플로우
-> 평가/관측 -> 인간 승인 -> 실험/제품 피드백으로 이어지는 반복 시스템을 먼저 구축해야 한다.

## Page 2

<!-- source_ref: ASP-P6-D1F4C9FC8737 p.2 -->

Asperitas AI/Bio-AI Development Process Benchmark Report | Internal Working Draft
Page 2
0. 사용 범위와 증거 경계
본 문서는 공개 웹 자료, 공식 문서, 공식 GitHub, 논문, 신뢰 가능한 산업/기관 자료를 기반으로 한 벤치마킹 보고서다. 각 회사의 내부 비공개 개발 프로세스 전체를 확인한 것이 아니며, 공개된 오픈소스/문서/논
문에서 관찰 가능한 개발 원리만 구조화했다. DB에 넣을 때는 반드시 source registry, license/terms review, provenance, ingestion_status, confidence를 분리해야 한다.
●
공식 문서/공식 GitHub/논문은 우선 사용했다. 블로그·뉴스는 보조 신호로만 사용했다.
●
“오픈소스”는 회사 전체 기술이 공개됐다는 뜻이 아니다. 대다수 Bio-AI 회사는 핵심 데이터와 모델이 비공개다.
●
Benchmark는 Asperitas 사실을 대체하지 않는다. 외부 자료는 operating analogy와 workflow primitive로만 흡수한다.
●
생물학/컴플라이언스/투자자-facing claim은 반드시 근거/검증상태/승인상태를 분리한다.
1. Executive Bottom Line
가장 중요한 패턴은 4개다. 첫째, OpenAI/Anthropic류 LLM 회사는 “모델 성능”보다 “행동 명세, 평가, 도구 권한, 관측 가능성”을 운영체계화한다. 둘째, LangChain/LlamaIndex/CrewAI류 에이전트 회사는 자
유로운 에이전트보다 상태 그래프, step/event workflow, guardrail, trace를 강조한다. 셋째, Hugging Face/Baseten/Modal/Databricks류 개발 운영 회사는 모델을 제품화하려면 패키징, 서빙, 비용,
latency, rollback, monitoring이 필요하다는 것을 보여준다. 넷째, Recursion/Ginkgo/Isomorphic/Owkin/GenerateBio/Xaira류 Bio-AI 회사는 “AI prediction”보다 “proprietary data + metadata +
wet-lab/assay validation + DBTL feedback loop”를 실제 moat로 만든다.
Asperitas에 대한 결론: 지금 단계의 최적 방향은 자율 실험실이 아니라 Benchmark Source Registry + AOS-aligned RAG/Agent + Eval/Trace/Compliance Gate + Bio Opportunity/DBTL
Queue다. 이후 PTMC/VITRAYA 등 제한된 프로젝트에서 인간승인형 DBTL loop를 붙이는 것이 맞다.
2. 공통 개발 프로세스: 경쟁사들이 반복하는 “진짜 루프”
 Pattern
 Seen in
 Operational meaning for Asperitas
Spec -> Eval -> Deployment
loop
OpenAI, Anthropic, W&B, MLflow
Every behavior rule becomes testable. Build evals before expanding autonomy.
Constitution / policy layer
Anthropic, OpenAI Model Spec, Asperitas AOS
AOS should be compiled into validators, not left as prose.
Typed tool/function
contracts
OpenAI Agents, Gemini, MCP, Ginkgo CFPS
Every tool call must have schema, permission, input validation, and human approval mode.
Source-grounded retrieval
LangChain, LlamaIndex, Perplexity, Glean
Separate internal truth, external current intelligence, and unverified benchmark sources.
Traceability / observability
W&B Weave, CrewAI, MLflow
Run logs, tool logs, decision logs, cost, latency, source citations, and error taxonomy are mandatory.
Biological data flywheel
Recursion, Ginkgo, Isomorphic, Xaira
Validated proprietary data beats generic model access. Build data acquisition and metadata systems now.
Closed-loop DBTL
Ginkgo/OpenAI, Recursion, Xaira
Hypothesis -> experiment spec -> execution -> assay -> learning update. Human-in-loop until safety/compliance proves stable.
Knowledge graph
foundation
BenevolentAI, Glean, biomedical KG-RAG
literature
Biology needs entity/evidence relations, not only vector chunks.
Privacy-preserving
collaboration
Owkin/Substra
Partner datasets may remain distributed; compute and evidence can move instead of raw data.
Protein/structure
generation as module
AlphaFold/Isomorphic, Chroma, AtomNet
Use prediction/generation as decision support; validation/IP/compliance gates determine value.

## Page 3

<!-- source_ref: ASP-P6-D1F4C9FC8737 p.3 -->

Asperitas AI/Bio-AI Development Process Benchmark Report | Internal Working Draft
Page 3
3. LLM / Foundation Model 회사별 개발 프로세스 벤치마킹
이 섹션은 LLM 회사들이 공개한 오픈소스, API 문서, 모델/에이전트 개발 자료에서 추출한 개발 강조점이다. Asperitas는 여기를 “모델을 직접 학습하는 방법”보다 “AI 시스템을 검증하고 운영하는 방식”으로 흡수
해야 한다.
 Company / stack
 Public/open artifact
 Observed development process emphasis
 Asperitas benchmark takeaway
OpenAI
Evals, Model Spec evals, Agents SDK,
structured-output eval cookbook [S01-S04]
Behavior spec -> eval harness -> typed agent outputs -> approval interruption.
OpenAI’s public tooling pushes teams to encode success criteria as tests rather than
relying on vibes.
Adopt: every AOS/agent behavior rule becomes an eval. No strategic
claim, RAG answer, or DBTL recommendation ships without schema,
citation, and regression test.
Anthropic
Claude Constitution, Agent SDK, MCP
[S05-S07]
Principle-governed model behavior plus production agent primitives: file tools,
command execution, context management, permissions, hooks, and external
tool/data protocol.
Adopt: AOS constitution + deterministic hooks. Use MCP-like
integration but require strict tool permissions, audit log, allowlists, and
prompt-injection tests.
Google / Gemini
Gemini API Cookbook and function calling
docs [S08-S09]
Multimodal/action model workflow: practical cookbook, function declarations,
external APIs, and agentic action patterns.
Adopt: Gemini-style function contracts for every internal tool:
search_source, read_source, check_compliance, create_decision_log,
queue_experiment.
Google DeepMind /
AlphaFold
AlphaFold/Isomorphic public tech narrative
[S10-S11]
Model alone is insufficient; structure prediction becomes valuable when integrated
into target/disease-agnostic drug design workflows and experimental decision loops.
Adopt: do not stop at prediction. Store confidence, input provenance,
assay requirement, validation status, and IP/compliance implications.
Meta AI / Llama
Llama Cookbook [S14]
Open model ecosystem: inference, fine-tuning, RAG, multimodal recipes,
community deployment patterns.
Use as local/private model option for low-cost internal tasks and eval
baseline, not as sole intelligence layer.
Mistral AI
Platform, agents, evals, judges, guardrails,
deployment portability [S15]
Enterprise AI stack emphasizes custom agents, observability, registry, guardrails,
and portability from edge to cloud.
Benchmark for internal/external deployment separation: local dev,
private inference, cloud fallback, full observability.
Cohere
Aya multilingual model and eval research [S16]
Data curation and multilingual evaluation are treated as first-class infrastructure,
not afterthoughts.
Useful for Korean/English/Chinese bio-intelligence. Build multilingual
golden sets and translation-risk tests.
DeepSeek
DeepSeek-V3/R1 repos and reports [S12-S13]
Efficiency-first model engineering: MoE, MLA, cost-aware training, RL/reasoning
release strategy.
Benchmark mindset: optimize cost per correct decision, not largest
model. Use small specialized models after RAG/evals prove the task.
Qwen / Alibaba
Open model family and cookbook ecosystem
(see source registry for active repo verification)
Broad open-weight strategy, multilingual/multimodal releases, ecosystem adoption.
Treat as deployable open baseline for internal/private workflows after
security and license review.
Zhipu / Z.ai
GLM open-source hybrid reasoning repo [S17]
Hybrid reasoning modes: thinking for complex/tool tasks, non-thinking for fast
responses.
Implement dual mode: fast answer for low-risk retrieval;
reasoning+approval for bio/compliance/IP decisions.
xAI
Grok open releases and weights (source-map
item; verify current license before ingestion)
Open-weight signaling with frontier-scale MoE framing, but limited process
transparency compared with eval-heavy providers.
Use mainly as external benchmark signal, not as process template
unless documentation/evals are stronger.
4. Agent / RAG / AI 개발운영 기업 벤치마킹
에이전트 생태계의 핵심은 “여러 에이전트가 알아서 한다”가 아니다. production-grade agent는 입력/출력 schema, 상태 관리, 도구 권한, 관측, 평가, rollback, human approval의 조합이다.
 Company / stack
 Public/open artifact
 Observed development process emphasis
 Asperitas benchmark takeaway
LangChain / LangGraph /
LangSmith
LangGraph, LangSmith ecosystem [S18-S19]
Stateful graph orchestration, long-running agents, tracing, debugging, evals,
and deployment management.
Use graph/state machine for Asperitas agents; no free-form
autonomous loop for compliance-sensitive tasks.
LlamaIndex
LlamaIndex OSS, Workflows [S20-S21]
Data ingestion, parsing, indexing, agentic applications; event-driven async step
workflows.
Best fit for source ingestion/RAG layer. Build source registry ->
parser -> chunk -> index -> retrieval -> citation checker.

## Page 4

<!-- source_ref: ASP-P6-D1F4C9FC8737 p.4 -->

Asperitas AI/Bio-AI Development Process Benchmark Report | Internal Working Draft
Page 4
 Company / stack
 Public/open artifact
 Observed development process emphasis
 Asperitas benchmark takeaway
CrewAI
CrewAI docs/GitHub [S22]
Role-based crews, flows, guardrails, memory, knowledge, observability;
deterministic workflow emphasis.
Use multi-agent roles only after core RAG/evals exist. Each agent
must have single responsibility and explicit stop rules.
Weights & Biases
Weave [S23-S24]
Trace LLM inputs/outputs/tool calls, debug regressions, apples-to-apples evals,
LLM judges/custom scorers.
Create internal trace/eval layer before expanding agents. Every
answer should be replayable and scored.
Hugging Face
Transformers, TRL, PEFT [S25-S26]
Open model hub + post-training + parameter-efficient adaptation; lower barrier
to custom models.
After source corpus/evals stabilize, train small adapters for Asperitas
style/classification, not before.
Baseten
Truss [S27]
Package model into deployable container with config, hardware,
runtime/dependency control.
Adopt model packaging discipline: config.yaml, reproducible
runtime, rollback, endpoint tests.
Modal
Serverless GPU/inference/training/sandboxes
[S28]
Elastic compute, low-latency inference, isolated sandboxes for AI-generated
code, batch scale-out.
Use for bursty eval/inference jobs after cost guardrails. Avoid
always-on GPU burn in Phase 0.
Databricks / MLflow
MLflow + Model Serving [S29-S30]
Debug/evaluate/monitor/optimize AI applications; serve models through
governed REST endpoints.
Benchmark for production-grade governance: registry, serving
endpoint, monitoring, quality/cost metrics.
Perplexity
Search API, Sonar API [S31-S32]
Web-grounded search and AI responses with real-time ranked results, streaming
and source controls.
Use as external intelligence layer for market/regulatory/news;
separate from internal source-of-truth.
Glean
Enterprise search/knowledge graph [S33]
Enterprise data graph, people/content/activity signals, governance-aware search
and assistant layer.
Model Asperitas KB as enterprise knowledge graph: documents,
people, species, protocols, decisions, experiments.
5. Bio-AI / AI Drug Discovery / Generative Biology 기업 벤치마킹
Bio-AI 회사들의 공통점은 “생물학적 데이터의 반복 생산과 검증”이다. 공개된 오픈소스는 일부 도구나 데이터셋에 그치지만, 개발 철학은 명확하다: 데이터 생성/정규화/표현학습/예측/실험/검증/제품화가 하나
의 flywheel로 연결되어야 한다.
 Company / stack
 Public/open artifact
 Observed development process emphasis
 Asperitas benchmark takeaway
Recursion
RxRx datasets, RxRx3, Recursion OS narrative
[S34-S35, S51]
Industrial phenomics flywheel: perturbation data -> embeddings/models -> drug
discovery decisions; public datasets are only a small window into proprietary scale.
Critical lesson: proprietary biological data and batch-corrected
phenotypes are moat. Build Asperitas
phenotype/omics/compound registry early.
Ginkgo + OpenAI
CFPS autonomous lab paper and GitHub
interface [S36-S37]
LLM + cloud lab + schema validation + automation platform + iterative experiment
design/execution/data analysis. Reported 40% specific cost reduction and 27% titer
increase in CFPS in the public paper.
This is the strongest DBTL benchmark. Copy the architecture
pattern, not the exact biology: schema-validated experiment
specs, human approval, automated data capture, iteration logs.
Isomorphic Labs
Drug design engine and AlphaFold 3 tech pages
[S10-S11]
Biomolecular structure prediction is extended into an end-to-end,
target/disease-agnostic drug design engine.
Prediction must be embedded in workflow: target hypothesis,
candidate design, assay, clinical translatability, IP, and go/no-go.
Insilico Medicine
DORA open-source announcement and GitHub
[S38-S39]
Agentic research-document workflow with agile agents, engineered prompts,
references, workflows, and proprietary databases.
Useful for Literature/Patent/Grant Agent. Keep citation/relevance
checks; do not let document generation masquerade as validated
biology.
Exscientia
UKRI case study [S47]
AI-designed drug candidates with experienced drug hunter feedback; design and
experimental validation are fused.
Benchmark: AI proposes, medicinal chemistry and assays dispose.
Build wet-lab and domain review gates.
Atomwise
AtomNet paper and Scientific Reports study
[S45-S46]
Structure-based CNN virtual screening; large-scale virtual HTS can substitute some
early HTS functions when validated.
For Asperitas: use virtual screening only as prioritization. Wet-lab
validation and assay reproducibility remain mandatory.

## Page 5

<!-- source_ref: ASP-P6-D1F4C9FC8737 p.5 -->

Asperitas AI/Bio-AI Development Process Benchmark Report | Internal Working Draft
Page 5
 Company / stack
 Public/open artifact
 Observed development process emphasis
 Asperitas benchmark takeaway
BenevolentAI
Knowledge graph/data-foundation material
[S44]
Knowledge graph + proprietary ontologies + tooling on top for target/hypothesis
generation.
Build KG not as ornament but as discovery engine: entity
resolution, evidence paths, confidence, contradictory evidence.
Owkin
Substra federated learning [S42-S43]
Privacy-preserving collaborative model training on distributed medical datasets;
production FL environments.
For biodiversity/hospital/partner data: do not centralize
everything by default. Federated or partner-side compute can
unlock regulated data.
Generate:Biomedicines
Chroma GitHub and Nature paper [S40-S41]
Programmable protein generation with composable building blocks, all-atom
structure/sequence modeling and conditioning.
Asperitas should treat generative protein design as a module
attached to proprietary organism/protein data and DBTL
validation.
Formation Bio
Sanofi/OpenAI collaboration and Muse
[S48-S49]
AI-native pharma operations across drug-development lifecycle; patient recruitment
and development software.
Benchmark non-discovery bottlenecks too: trial design,
recruitment, document ops, asset diligence, and portfolio
execution.
Xaira Therapeutics
Official site and public launch narrative [S50]
Integrated AI biotech combining ML research, expansive data generation, and
therapeutic product development.
Closest strategic analogy to a full-stack AI-bio company.
Asperitas version must swap therapeutic-only focus for
biodiversity-derived biological infrastructure.
6. Asperitas에 바로 적용할 Workflow v0.1
6.1 Benchmark-to-DB ingestion workflow
●
1) Source discovery: 회사명, 소스명, URL, source_type, official 여부, license/terms 상태를 먼저 registry에 기록한다.
●
2) Evidence classification: official docs, GitHub repo, paper, blog, news, inference를 분리한다.
●
3) Workflow primitive extraction: eval, agent loop, data flywheel, tool contract, observability, DBTL loop 등 재사용 가능한 패턴만 추출한다.
●
4) Asperitas fit scoring: Scalability, Moat, Biosafety/Compliance, Capital Efficiency, Learning Velocity 기준으로 1-5점 평가한다.
●
5) AOS integration: 통과한 패턴만 AGENTS.md, evals, schemas, runbooks, source policy에 반영한다.
●
6) Regression: 반영 전후 golden question/eval 통과 여부를 기록한다.
6.2 Internal agent build sequence
 Phase
 Objective
 Build now / later
 Benchmark sources
Phase 0 - Internal credibility
memory
Create source-grounded operating memory,
benchmark DB, citations, evals, compliance gates.
Build now: source registry, metadata, parsers, RAG, agent harness, trace/eval, report generator,
decision log. Do not build autonomous wet-lab execution yet.
OpenAI evals, LlamaIndex, LangGraph, W&B,
Glean
Phase 1 - Human-in-loop bio
intelligence
Turn documents and datasets into structured bio
opportunity cards and DBTL queues.
Build next: species/protein/pathway cards, literature/patent agent, compliance gatekeeper,
experiment registry, assay-result schema.
Recursion, BenevolentAI, Owkin, GenerateBio
Phase 2 - Semi-automated
DBTL
Use AI to recommend next experiments and capture
results, with human approval and lab integration.
Build after data maturity: protocol registry, ELN/LIMS-ready schema, image/phenotype analysis,
human-in-loop active learning.
Ginkgo/OpenAI autonomous lab, Recursion,
Xaira
Phase 3 - Biological
Intelligence Factory
Repeatable data/model/experiment/IP/product
flywheel.
Build only after validated proprietary datasets and compliant execution infrastructure exist.
Isomorphic, Recursion, Xaira, Formation Bio
6.3 Recommended software modules

## Page 6

<!-- source_ref: ASP-P6-D1F4C9FC8737 p.6 -->

Asperitas AI/Bio-AI Development Process Benchmark Report | Internal Working Draft
Page 6
●
source_registry: 외부 benchmark source와 내부 Asperitas source를 같은 registry에서 관리하되 priority/disclosure는 분리.
●
benchmark_parser: GitHub README, API docs, papers, PDF, company pages를 markdown + metadata로 추출.
●
pattern_extractor: “개발 프로세스/강조점/오픈소스 artifact/Asperitas 적용점”을 JSON으로 추출.
●
comparison_engine: 현재 AOS/Codex roadmap 대비 gap과 action item 생성.
●
eval_harness: citation accuracy, unsupported claim, compliance escalation, phase discipline, Korean COO style 검증.
●
workflow_compiler: 통과한 benchmark pattern만 runbook, Codex prompt, AGENTS.md patch proposal로 변환.
7. 최소 DB Schema 제안
아래 스키마는 “나중에 학습시킬 예정”이라는 목표를 구현 가능한 DB 구조로 바꾸는 최소 단위다. 핵심은 원문을 무작정 넣는 것이 아니라, 출처/라이선스/검증상태/적용가능성/위험을 함께 넣는 것이다.
 Table
 Core fields
 Purpose
benchmark_company
company_id, name, domain, category, source_priority, confidence, last_verified
Company-level benchmark registry.
benchmark_artifact
artifact_id, company_id, artifact_type, url, license_status, open_source_status, checksum,
ingestion_status
Track repos, docs, papers, APIs, cookbooks.
process_pattern
pattern_id, name, source_artifacts, workflow_step, evidence_type, applicability, risk
Extract reusable workflow primitives from competitors.
asperitas_gap
gap_id, benchmark_pattern, current_state, required_change, owner, deadline, score
Compare benchmark to current Asperitas roadmap.
eval_case
eval_id, target_agent, prompt, expected_behavior, source_requirement, compliance_trigger, pass_rule
Regression tests for agent quality and safety.
decision_log
decision_id, context, sources_used, chosen_path, rejected_alternatives, risk, next_action, review_date
Preserve strategic memory and audit trail.
dbtl_event
event_id, hypothesis, design, protocol_version, approval_status, assay_result, validation_status,
learning_update
Connect biological experiments to model learning.
7.1 JSONL record example
{
 "artifact_id": "BENCH-OPENAI-EVALS-001",
 "company": "OpenAI",
 "category": "LLM_eval_ops",
 "source_type": "official_github",
 "url": "https://github.com/openai/evals",
 "license_status": "verify_before_ingestion",
 "process_pattern": "behavior_spec_to_eval_harness",
 "asperitas_application": "Convert AOS rules into golden evals and regression tests",
 "evidence_label": "document_supported",
 "confidence": "high",
 "ingestion_status": "source_mapped_not_ingested",
 "risk": "do not store private eval data in public repos",
 "next_action": "Create eval_cases for citation accuracy, compliance escalation, phase discipline"
}
8. 우선순위 Action Plan

## Page 7

<!-- source_ref: ASP-P6-D1F4C9FC8737 p.7 -->

Asperitas AI/Bio-AI Development Process Benchmark Report | Internal Working Draft
Page 7
 Priority
 Action
 Definition of done
 Why now
P0
Benchmark Source Registry 생성
50개 이상 source row: source_type, URL, license_status, confidence, ingestion_status 입력
자료를 “긁음”과 “DB화”를 분리해야 환각/저작권/출처 붕괴를
막는다.
P0
Golden Eval 20개 작성
citation accuracy, unsupported claim, compliance, phase discipline, Korean COO style 테스트 통과
최고 기업들은 eval로 운영한다. 에이전트 성능 향상은 eval 없
이는 감으로 전락한다.
P0
Benchmark Pattern JSON 추출기
각 source에서 process_pattern, applicability, risk, action_item 추출
PDF 보고서가 DB 입력으로 이어져야 한다.
P1
AOS-Codex Roadmap Gap Matrix
현재 repo roadmap과 benchmark pattern 간 gap/owner/deadline 작성
벤치마킹이 실제 개발 순서 수정으로 연결된다.
P1
Human-in-loop DBTL schema
hypothesis, design, approval, protocol, assay, result, validation fields 정의
Bio-AI moat는 실험 데이터와 검증 label에서 생긴다.
P2
Bio opportunity cards MVP
species/protein/pathway/literature/compliance/IP 카드 자동 생성
COO/연구팀이 매일 쓸 수 있는 내부 intelligence product로
전환된다.
9. Devil’s Advocate: 벤치마킹할 때 반드시 피해야 할 착각
●
오픈소스 repo를 모았다고 그 회사의 moat를 복제한 것이 아니다. Recursion/Isomorphic/Xaira의 핵심은 공개 repo가 아니라 데이터, 실험, 팀, 파트너, capital, validation loop다.
●
에이전트를 많이 나누면 성능이 올라가는 것이 아니다. source grounding, eval, trace, tool permission이 없으면 다중 에이전트는 환각을 여러 명이 나눠서 하는 구조가 된다.
●
Bio-AI에서 prediction은 validation이 아니다. 구조 예측, virtual screening, protein generation은 prioritization signal이지 wet-lab proof가 아니다.
●
웹 크롤링은 DB화가 아니다. license/terms, provenance, redaction, checksum, metadata, ingestion logs가 있어야 DB화다.
●
Phase 0에서 autonomous wet-lab을 만들면 안 된다. 먼저 source registry, schema, compliance gate, eval, decision log를 완성해야 한다.
10. Source Registry: 이번 보고서에 사용한 핵심 공개 자료
DB에 실제로 넣을 때는 아래 각 row를 benchmark_artifact 테이블로 이동시키고, license_status와 ingestion_status를 별도로 관리한다. URL은 공개 접근 가능한 위치를 가리키며, 이용약관/라이선스 검토 전
에는 원문 대량 저장을 하지 않는다.
 ID
 Source
 Organization
 Use
 URL
S01
OpenAI Evals GitHub
OpenAI
Eval framework for LLMs/systems; private/custom eval patterns
https://github.com/openai/evals
S02
OpenAI structured output eval cookbook
OpenAI
Structured output evaluation example with Evals API
https://developers.openai.com/cookbook/examples/evaluation/use-c
ases/structured-outputs-evaluation
S03
OpenAI Model Spec / model_spec_evals
OpenAI
Desired model behavior and evaluation harness
https://github.com/openai/model_spec_evals
S04
OpenAI Agents SDK results
OpenAI
Typed final outputs and approval interruption patterns
https://openai.github.io/openai-agents-python/results/
S05
Claude Agent SDK overview
Anthropic
Production agent loop, tools, context management
https://code.claude.com/docs/en/agent-sdk/overview
S06
Claude Constitution
Anthropic
Constitutional behavior framework
https://www.anthropic.com/constitution
S07
MCP engineering article
Anthropic
Open standard for connecting AI agents to external systems
https://www.anthropic.com/engineering/code-execution-with-mcp
S08
Gemini API Cookbook
Google
Structured learning path and practical API examples
https://github.com/google-gemini/cookbook
S09
Gemini function calling cookbook
Google
Function calling with REST / notebooks
https://github.com/google-gemini/cookbook/blob/main/quickstarts/
Function_calling.ipynb

## Page 8

<!-- source_ref: ASP-P6-D1F4C9FC8737 p.8 -->

Asperitas AI/Bio-AI Development Process Benchmark Report | Internal Working Draft
Page 8
 ID
 Source
 Organization
 Use
 URL
S10
AlphaFold 3 / Isomorphic Labs article
Isomorphic Labs
Drug design engine beyond structure prediction
https://www.isomorphiclabs.com/articles/the-isomorphic-labs-drug-
design-engine-unlocks-a-new-frontier
S11
Isomorphic Labs Our Tech
Isomorphic Labs
AlphaFold 3 and end-to-end drug design engine framing
https://www.isomorphiclabs.com/our-tech
S12
DeepSeek-V3 GitHub
DeepSeek
MoE, MLA, DeepSeekMoE, multi-token prediction
https://github.com/deepseek-ai/deepseek-v3
S13
DeepSeek-R1 GitHub
DeepSeek
R1/R1-Zero derived from V3-base; open model downloads
https://github.com/deepseek-ai/deepseek-r1
S14
Meta Llama Cookbook
Meta AI
Inference, fine-tuning and end-to-end recipes
https://github.com/meta-llama/llama-cookbook
S15
Mistral AI platform page
Mistral AI
Enterprise AI platform: agents, evals, guardrails, deployment portability
https://mistral.ai/
S16
Cohere Aya paper
Cohere For AI
Multilingual instruction tuning/evaluation across 99+ languages
https://arxiv.org/abs/2402.07827
S17
Z.ai / GLM open-source repo
Z.ai
Hybrid reasoning modes and open model releases
https://github.com/zai-org/GLM-4.5
S18
LangGraph GitHub
LangChain
Long-running, stateful agent orchestration
https://github.com/langchain-ai/langgraph
S19
LangSmith / LangGraph docs via LangChain
LangChain
Agent orchestration, debug, scale, eval ecosystem
https://www.langchain.com/langgraph
S20
LlamaIndex GitHub
LlamaIndex
Agentic applications, parsing, extraction, indexing
https://github.com/run-llama/llama_index
S21
LlamaIndex Workflows
LlamaIndex
Event-driven, async, step-based workflows
https://github.com/run-llama/llama-agents
S22
CrewAI docs
CrewAI
Multi-agent systems with guardrails, memory, knowledge, observability
https://docs.crewai.com/
S23
W&B Weave GitHub
Weights & Biases
Trace/debug LLM IO and rigorous evaluations
https://github.com/wandb/weave
S24
W&B Weave docs
Weights & Biases
Observability and evaluation with LLM judges/custom scorers
https://docs.wandb.ai/weave
S25
Hugging Face TRL
Hugging Face
SFT/RLHF/GRPO-style post-training workflows
https://github.com/huggingface/trl
S26
Hugging Face PEFT
Hugging Face
Parameter-efficient fine-tuning to reduce compute/storage
https://github.com/huggingface/peft
S27
Baseten Truss
Baseten
Open-source packaging/deployment for model serving
https://github.com/basetenlabs/truss
S28
Modal docs
Modal
Serverless compute/inference/training/sandboxes
https://modal.com/docs/guide
S29
MLflow
Databricks/MLflow
Open-source AI engineering platform for agents, LLMs, ML
https://mlflow.org/
S30
Databricks Model Serving
Databricks
Unified REST API for real-time/batch model serving
https://docs.databricks.com/aws/en/machine-learning/model-serving
/
S31
Perplexity API Platform
Perplexity
Real-time web search and grounded AI API
https://www.perplexity.ai/api-platform
S32
Perplexity Sonar API
Perplexity
Web-grounded AI responses with tools/search options
https://docs.perplexity.ai/docs/sonar/quickstart
S33
Glean Work AI / Knowledge Graph
Glean
Enterprise knowledge graph/search/agent governance
https://www.glean.com/
S34
Recursion RxRx Datasets
Recursion
Public research datasets repository
https://github.com/recursionpharma/rxrx-datasets
S35
RxRx3 public map of biology
Recursion
Public subset of Recursion dataset, <1% of total
https://www.rxrx.ai/rxrx3

## Page 9

<!-- source_ref: ASP-P6-D1F4C9FC8737 p.9 -->

Asperitas AI/Bio-AI Development Process Benchmark Report | Internal Working Draft
Page 9
 ID
 Source
 Organization
 Use
 URL
S36
OpenAI/Ginkgo autonomous lab PDF
OpenAI/Ginkgo
GPT-5 autonomous lab for CFPS optimization
https://cdn.openai.com/pdf/5a12a3bc-96b7-4e07-9386-db6ee5bb2
ed9/using-a-gpt-5-driven-autonomous-lab-to-optimize-the-cost-and-
titer-of-cell-free-protein-synthesis.pdf
S37
Ginkgo CFPS automation interface GitHub
Ginkgo Bioworks
Interface between GPT-5 and autonomous laboratory
https://github.com/ginkgobioworks/ginkgo-automation-cfps
S38
Insilico DORA news
Insilico Medicine
Agentic research document drafting with agents/prompts/workflows
https://insilico.com/news/kv5e80yc41-insilico-open-sources-dora-on-
github-sup
S39
Insilico GitHub
Insilico Medicine
DORA and other public repos
https://github.com/insilicomedicine
S40
GenerateBio Chroma GitHub
Generate:Biomedicines
Programmable generative protein design model
https://github.com/generatebio/chroma
S41
Chroma Nature paper
Generate:Biomedicines
Programmable generative protein design
https://www.nature.com/articles/s41586-023-06728-8
S42
Owkin/Substra GitHub
Owkin / LF AI & Data
Open-source federated learning software
https://github.com/substra
S43
Substra docs
Owkin / LF AI & Data
Production federated learning environments
https://docs.substra.org/
S44
BenevolentAI data foundations
BenevolentAI
Knowledge graph enriched with data and products/tools on top
https://www.benevolent.com/news-and-media/blog-and-videos/buil
ding-data-foundations-accelerate-drug-discovery/
S45
AtomNet paper
Atomwise
Structure-based deep convolutional network for bioactivity prediction
https://arxiv.org/abs/1510.02855
S46
AtomNet Scientific Reports 2024
Atomwise
Virtual HTS campaign with AtomNet
https://www.nature.com/articles/s41598-024-54655-z
S47
Exscientia UKRI case study
Exscientia
AI-designed drug candidate pipeline
https://www.ukri.org/who-we-are/how-we-are-doing/research-outc
omes-and-impact/bbsrc/exscientia-a-clinical-pipeline-for-ai-designed
-drug-candidates/
S48
Sanofi-Formation Bio-OpenAI announcement
Formation Bio / Sanofi /
OpenAI
AI-powered software across drug development lifecycle
https://www.sanofi.com/en/media-room/press-releases/2024/2024-
05-21-05-30-00-2885244
S49
Formation Bio Muse
Formation Bio
AI tool for patient recruitment in drug development
https://www.formation.bio/press/introducing-muse
S50
Xaira Therapeutics official
Xaira Therapeutics
Predictive AI across target, therapeutic, patient selection
https://www.xaira.com/
S51
Recursion official technology page
Recursion
Recursion OS, data, ML models, BioHive-2
https://www.recursion.com/
Appendix A. 벤치마킹 흡수 규칙
●
Rule 1 - Benchmark source is not company fact. 외부 회사 자료는 Asperitas의 실제 구축 상태를 증명하지 않는다.
●
Rule 2 - Open-source status must be checked per artifact. GitHub repo가 있어도 모델/데이터/weights/API/라이선스 범위가 다르다.
●
Rule 3 - Every claim gets evidence_label. fact, inference, speculation, verification_needed를 분리한다.
●
Rule 4 - Compliance-first bio workflow. CITES, Nagoya, LMO, biosafety, biosecurity, IP, privacy는 후처리 항목이 아니라 설계 항목이다.
●
Rule 5 - Phase discipline. Phase 0은 internal source-grounded decision system, Phase 1은 human-in-loop bio intelligence, Phase 2는 semi-automated DBTL, Phase 3는 full Biological
Intelligence Factory다.
Appendix B. Codex에 줄 최소 명령어 초안

## Page 10

<!-- source_ref: ASP-P6-D1F4C9FC8737 p.10 -->

Asperitas AI/Bio-AI Development Process Benchmark Report | Internal Working Draft
Page 10
Build BENCHMARK_DB_V0 for Asperitas.
Goal: turn public AI/Bio-AI company development-process sources into source-grounded benchmark records and compare them against current Asperitas AOS/Codex roadmap.
Create: data/benchmark_sources.csv, data/benchmark_patterns.jsonl, app/benchmark_compare.py, evals/test_benchmark_grounding.py, docs/BENCHMARK_WORKFLOW.md.
Rules: no uncontrolled scraping; store URL/provenance/license_status/ingestion_status; separate official docs, GitHub, paper, news, inference; no claim becomes fact without source; no
external benchmark overwrites internal Asperitas truth.
Output: gap matrix with action_item, owner_placeholder, priority, risk, phase, eval_required.
Tests: citation accuracy, source-type labeling, unsupported-claim refusal, compliance escalation, phase discipline.
