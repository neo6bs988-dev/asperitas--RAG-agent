# Asperitas Skills 사용 가이드

> **목적:** Asperitas repository의 30개 Skill이 무엇을 담당하고, 언제 선택하며, 어떻게 요청하는지 쉽게 설명한다.  
> **대상:** Codex 사용자, reviewer, maintainer, 신규 contributor  
> **중요 경계:** Skill은 작업 절차와 권한 선언을 제공하지만, 그 자체가 runtime 권한·배포·법률·과학·biosafety 승인을 부여하지 않는다.

---

## 1. Skill이란?

Asperitas의 **Skill**은 Codex가 특정 종류의 repository 작업을 수행할 때 사용하는 전문 작업 모듈이다.

각 Skill은 다음을 정한다.

- 언제 사용해야 하는가
- 어떤 입력이 필요한가
- 어떤 결과를 내야 하는가
- READ / DRAFT / WRITE 중 어디까지 가능한가
- 어떤 작업이 금지되는가
- 사람의 승인이 필요한가
- 무엇으로 검증하는가
- 실패하면 어떻게 rollback하는가

Skill은 모델 fine-tuning이 아니다. 모델의 weight를 바꾸는 대신, Codex가 **올바른 역할·권한·검증 절차**로 일하도록 만드는 execution harness다.

### Skill 파일 구조

```text
.agents/skills/<skill-name>/
├── SKILL.md             # 사람이 읽는 설명, trigger, workflow, output guidance
└── skill.contract.json  # machine-readable identity, mode, permission, gate, verification, rollback
```

상위 `AGENTS.md`, `SECURITY.md`, repository policy, 명시적 human approval이 Skill보다 우선한다.

---

## 2. 가장 쉬운 선택법

| 하려는 일 | 먼저 선택할 Skill |
|---|---|
| 실제 code를 수정하고 test를 추가 | `mvp-implementation` |
| 전체 architecture를 결정 | `asperitas-v1-architect` |
| workflow·state·단계 연결을 설계 | `asperitas-workflow` |
| RAG 구조를 설계·변경 | `asperitas-rag-development` |
| 검색·ranking·top-k를 개선 | `asperitas-retrieval` |
| retrieval 성능을 평가 | `retrieval-eval-quality-gate` |
| eval 설계와 metric을 정의 | `asperitas-evaluation` |
| 성능 향상 주장을 검증 | `performance-optimization-gate` |
| source와 evidence를 점검 | `source-grounding-check` |
| citation과 hallucination을 점검 | `source-grounding-citation` |
| 보안 위험을 검토 | `security-review` 또는 `asperitas-security` |
| CITES·Nagoya·biosafety·regulatory 위험을 검토 | `compliance-biosafety-review` |
| dependency나 library 도입을 검토 | `dependency-security-quality-gate` |
| PR을 검토 | `github-pr-review` |
| PR closeout 문서를 작성 | `pr-closeout` 또는 `pr-closeout-report` |
| 한 MVP stage를 종료 | `mvp-release-manager` |
| 아무것도 수정하지 않고 조사만 수행 | `read-only-audit` |

기본 원칙은 **Primary Skill 1개 + 꼭 필요한 companion Skill만 추가**하는 것이다. 모든 Skill을 동시에 호출하지 않는다.

---

## 3. Skill 요청 기본 형식

```text
PRIMARY:
<가장 중요한 Skill 하나>

COMPANIONS:
<필요한 보조 Skill만>

MODE:
READ | DRAFT | WRITE

GOAL:
<무엇을 끝내야 하는지>

SUCCESS_CRITERIA:
- <검증 가능한 조건>

ALLOWED_PATHS:
- <수정 가능한 경로>

FORBIDDEN_PATHS:
- <건드리면 안 되는 경로>

VERIFICATION:
- <실행할 test/eval>

STOP_CONDITIONS:
- <발견되면 멈출 조건>

HUMAN_GATE:
<push, PR, merge, release 등 별도 승인이 필요한 action>
```

### 간단한 예시

```text
PRIMARY: mvp-implementation
COMPANIONS: security-review, asperitas-evaluation
MODE: DRAFT

GOAL:
기존 retrieval 결과를 이용하는 provider-neutral answer contract를 구현한다.

SUCCESS_CRITERIA:
- 모든 claim이 evidence span 또는 abstention과 연결된다.
- focused tests가 통과한다.
- production deployment는 하지 않는다.
```

---

# 4. Architecture·Implementation Skills

## 4.1 `mvp-implementation`

**담당:** 범위가 고정된 실제 MVP code change.

**이럴 때 사용:**

- Python module 구현
- bug fix
- focused test 추가
- 관련 docs·decision log 업데이트

**호출 예시:**

```text
Use mvp-implementation to add a bounded claim-verification adapter with focused tests.
```

**주의:** local edit, commit, push, PR, Ready, merge는 서로 다른 WRITE action이다. 하나의 승인이 다른 action까지 자동 승인하지 않는다.

---

## 4.2 `asperitas-v1-architect`

**담당:** V1 architecture, layer, stage boundary와 기술 선택.

**이럴 때 사용:**

- deterministic helper와 agent 중 무엇을 쓸지 결정
- RAG, workflow, API, state 구조 비교
- 다음 MVP의 책임 범위 결정

**호출 예시:**

```text
Use asperitas-v1-architect to select the smallest architecture for the grounded answer path.
```

**주의:** architecture 문서는 구현 증거가 아니다. 실제 구현은 `mvp-implementation`과 별도 검증이 필요하다.

---

## 4.3 `asperitas-workflow`

**담당:** planner, retriever, reranker, validator, answer 단계의 연결과 state contract.

**이럴 때 사용:**

- fixed workflow 설계
- 단계별 input/output schema 정의
- retry, timeout, checkpoint, failure transition 설계

**호출 예시:**

```text
Use asperitas-workflow to design Extract → Retrieve → Verify → Answer as a fixed workflow.
```

**주의:** open-ended agent는 fixed workflow가 반복적으로 실패했다는 evidence가 있을 때만 고려한다.

---

## 4.4 `docs-only-governance-update`

**담당:** runtime behavior를 바꾸지 않는 governance·instruction·documentation 변경.

**이럴 때 사용:**

- `AGENTS.md` 설명 보완
- workflow 문서 정리
- 기존 정책을 더 명확하게 표현

**호출 예시:**

```text
Use docs-only-governance-update to clarify the existing approval boundary without changing runtime code.
```

**주의:** docs-only 작업에 runtime code, dependency, fixture, threshold 변경을 섞지 않는다.

---

# 5. RAG·Retrieval·Evaluation Skills

## 5.1 `asperitas-rag-development`

**담당:** RAG architecture 전반.

**이럴 때 사용:**

- chunking 전략
- retriever와 reranker 구조
- metadata schema
- vector DB·hybrid retrieval 후보
- answer-generation 구조

**호출 예시:**

```text
Use asperitas-rag-development to review chunking, retrieval, reranking, and answer-generation changes.
```

**주의:** RAG 설계가 존재한다고 production RAG가 구현된 것은 아니다.

---

## 5.2 `asperitas-retrieval`

**담당:** 실제 검색·candidate selection·ranking·context selection 변경.

**이럴 때 사용:**

- top-k 변경
- metadata filter 추가
- lexical·hybrid ranking 비교
- retrieval context budget 조정

**호출 예시:**

```text
Use asperitas-retrieval to assess a metadata filter and top-k change against the frozen baseline.
```

**주의:** retrieval 변경은 관련 eval 없이 promotion하지 않는다.

---

## 5.3 `embeddings-vector-db-mvp005`

**담당:** embedding, vector index, vector DB, hybrid retrieval 설계 검토.

**이럴 때 사용:**

- embedding model 후보 비교
- vector metadata 보존 설계
- index·cache·storage 구조 검토
- vector retrieval evaluation 계획

**호출 예시:**

```text
Explicitly use embeddings-vector-db-mvp005 to review the vector index design and deterministic fallback.
```

**현재 상태:** filesystem-only / `unregistered_review_required` / explicit-only.

**주의:** 자동 activation이나 runtime execution을 기대하지 않는다. 사용 시 이름을 명시한다.

---

## 5.4 `retrieval-eval-quality-gate`

**담당:** retrieval 변경의 품질 평가와 promotion gate.

**이럴 때 사용:**

- baseline vs candidate 비교
- precision·recall·ranking metric 검토
- regression·critical case 확인
- promotion / reject / defer 판정

**호출 예시:**

```text
Use retrieval-eval-quality-gate to compare the candidate retriever with the frozen incumbent dataset.
```

**주의:** local eval command 실행은 explicit approval이 필요하다. answer key가 runner input에 들어가면 결과는 invalid다.

---

## 5.5 `retrieval-regression-closeout`

**담당:** 발견된 retrieval regression을 분류하고 종료 여부를 판단.

**이럴 때 사용:**

- regression 원인 분류
- close / defer / reclassify 결정
- 기존 default 유지 여부 판단

**호출 예시:**

```text
Use retrieval-regression-closeout to classify the failed queries and decide whether to close or defer the candidate.
```

**주의:** 일부 좋은 사례만 골라 전체 성능 향상으로 주장하지 않는다.

---

## 5.6 `asperitas-evaluation`

**담당:** eval contract, metric, baseline, threshold, trial count 설계.

**이럴 때 사용:**

- 새 기능의 평가 계획
- RAGAS-style metric 검토
- answer faithfulness 평가
- nondeterministic trial 설계

**호출 예시:**

```text
Use asperitas-evaluation to freeze the dataset, metrics, thresholds, and critical cases before implementation.
```

**주의:** 결과를 본 뒤 threshold나 expected answer를 완화하지 않는다.

---

## 5.7 `performance-optimization-gate`

**담당:** “성능이 좋아졌다”는 주장의 검증.

**이럴 때 사용:**

- retrieval quality 향상 주장
- latency·token·context 절감 주장
- groundedness·compliance 개선 주장

**호출 예시:**

```text
Use performance-optimization-gate to verify whether the claimed latency reduction is supported by comparable measurements.
```

**주의:** 측정되지 않은 성능은 `UNVERIFIED`로 남긴다.

---

# 6. Source·Evidence·Audit Skills

## 6.1 `source-grounding-check`

**담당:** source identity, evidence label, unsupported claim 점검.

**이럴 때 사용:**

- 답변이 실제 source와 연결되는지 확인
- source state와 claim state 구분
- 근거가 부족한 문장 표시

**호출 예시:**

```text
Use source-grounding-check to identify unsupported claims and missing source metadata.
```

---

## 6.2 `source-grounding-citation`

**담당:** citation target, evidence hierarchy, hallucination 방지.

**이럴 때 사용:**

- citation이 실제 문장을 지원하는지 확인
- source hierarchy가 지켜졌는지 확인
- 추론과 verified fact를 분리

**호출 예시:**

```text
Use source-grounding-citation to review claim-to-citation alignment and hallucination risk.
```

---

## 6.3 `asperitas-source-audit`

**담당:** source manifest, provenance, classification, license, disclosure, ingestion gate 검토.

**이럴 때 사용:**

- 새 source를 repository에 넣기 전
- source registry field를 변경할 때
- confidential/public classification을 검토할 때

**호출 예시:**

```text
Use asperitas-source-audit to review provenance, license, disclosure, and permitted-use metadata.
```

**주의:** source possession은 sequencing, model training, commercialization 권리를 자동 부여하지 않는다.

---

## 6.4 `reference-acquisition`

**담당:** 외부 자료를 ingestion하기 전 reference metadata 후보로 검토.

**이럴 때 사용:**

- 논문·공식 문서·repository 후보 기록
- license·security review 필요성 표시
- allowed next action 결정

**호출 예시:**

```text
Use reference-acquisition to register this library as a review candidate without ingestion or adoption.
```

---

## 6.5 `asperitas-audit-trace`

**담당:** provenance, trace, citation coverage, audit log, decision log 요구사항.

**이럴 때 사용:**

- 어떤 evidence를 로그에 남길지 정의
- source→retrieval→answer trace 설계
- decision record 누락 확인

**호출 예시:**

```text
Use asperitas-audit-trace to define the minimum provenance and decision-log evidence for this change.
```

---

## 6.6 `decision-log-maintainer`

**담당:** append-only decision log 유지.

**이럴 때 사용:**

- 중요한 architecture decision 기록
- metric provenance와 residual risk 기록
- 다음 action과 rollback 기록

**호출 예시:**

```text
Use decision-log-maintainer to record the selected architecture, rejected alternatives, evidence, and rollback.
```

**주의:** tracked log 작성은 WRITE이므로 별도 승인이 필요하다.

---

## 6.7 `read-only-audit`

**담당:** 어떤 파일도 수정하지 않고 repository 상태를 조사.

**이럴 때 사용:**

- 현재 implementation 조사
- PR·issue·metric 검토
- missing evidence와 risk 목록 작성

**호출 예시:**

```text
Use read-only-audit to inspect the current retrieval pipeline. Do not modify any file.
```

---

# 7. Security·Compliance·Adoption Skills

## 7.1 `security-review`

**담당:** 일반적인 repository change의 security review.

**이럴 때 사용:**

- secret 노출 가능성
- unsafe shell·path traversal
- dependency·external-call 위험
- scope creep와 permission 문제

**호출 예시:**

```text
Use security-review to inspect the changed files for secret exposure, unsafe execution, and permission escalation.
```

---

## 7.2 `asperitas-security`

**담당:** Asperitas agent architecture 특화 보안.

**이럴 때 사용:**

- prompt injection
- source poisoning
- connector permission
- agent/tool escalation
- CI authority와 confidential data exposure

**호출 예시:**

```text
Use asperitas-security to threat-review the new tool interface and untrusted-content boundary.
```

---

## 7.3 `compliance-biosafety-review`

**담당:** biological data, biodiversity, CITES, Nagoya/ABS, DSI, LMO/GMO, biosafety, regulatory 위험.

**이럴 때 사용:**

- biological source나 sequence 관련 작업
- 국가 간 유전자원 이동
- permit·PIC/MAT·CITES 관련 판단
- biosafety·biosecurity 영향

**호출 예시:**

```text
Use compliance-biosafety-review to classify the CITES, Nagoya, biosafety, and regulatory gates.
```

**주의:** risk를 분류할 뿐, 최종 legal·rights·biosafety approval을 내리지 않는다.

---

## 7.4 `asperitas-compliance-audit`

**담당:** legal, privacy, IP, investor, public communication까지 포함한 광범위 compliance audit.

**이럴 때 사용:**

- 외부 발표·투자자 자료
- partner/customer 공유 자료
- privacy·IP·legal risk가 섞인 변경

**호출 예시:**

```text
Use asperitas-compliance-audit to identify blocked claims and required human approvers before external use.
```

---

## 7.5 `dependency-security-quality-gate`

**담당:** dependency, package, CI, scanner, lint, typing 도구의 도입 검토.

**이럴 때 사용:**

- 새 Python package 추가
- CI scanner 변경
- lint/type-check tool 도입
- transitive dependency 위험 검토

**호출 예시:**

```text
Use dependency-security-quality-gate to review the package license, vulnerabilities, transitive impact, and rollback.
```

---

## 7.6 `open-source-review`

**담당:** open-source 후보의 초기 license·security·adoption-level 검토.

**이럴 때 사용:**

- 외부 repository를 참고할지 판단
- code copy 전에 license 검토
- dependency adoption 전 preliminary review

**호출 예시:**

```text
Use open-source-review to determine whether this repository may be referenced, adapted, or adopted.
```

---

## 7.7 `open-source-adoption-review`

**담당:** 외부 AI/RAG/vector/eval library를 Asperitas 내부 구조에 실제 채택할지 검토.

**이럴 때 사용:**

- 기존 code와 통합 범위 분석
- build vs adopt 비교
- license·security·maintenance·rollback 판단

**호출 예시:**

```text
Explicitly use open-source-adoption-review to assess adopting this reranking library.
```

**현재 상태:** filesystem-only / `unregistered_review_required` / explicit-only.

**주의:** 사용 시 Skill 이름을 직접 명시한다. 실제 dependency 추가는 별도 WRITE 승인 대상이다.

---

## 7.8 `asperitas-mcp-expansion`

**담당:** MCP, connector, external tool 후보와 allowlist 경계 설계.

**이럴 때 사용:**

- GitHub·Drive·Slack 등 connector 후보 검토
- tool input/output schema 설계
- egress·secret·permission 범위 정의

**호출 예시:**

```text
Use asperitas-mcp-expansion to review the connector allowlist, data exposure, and approval boundary.
```

**주의:** connector를 검토하는 것과 실제 연결·호출 권한은 별개다.

---

# 8. GitHub·PR·Release Skills

## 8.1 `github-pr-review`

**담당:** commit, push, PR, merge 전 diff·test·secret·scope 검토.

**이럴 때 사용:**

- changed files가 scope와 일치하는지 확인
- test/eval evidence 검토
- merge recommendation 작성

**호출 예시:**

```text
Explicitly use github-pr-review to review the diff, tests, secrets, scope, and merge readiness.
```

**현재 상태:** filesystem-only / `unregistered_review_required` / explicit-only.

**주의:** review Skill은 push·Ready·merge 권한을 부여하지 않는다.

---

## 8.2 `pr-closeout`

**담당:** PR body와 간단한 closeout package 작성.

**이럴 때 사용:**

- objective와 scope 요약
- tests·risks·next MVP 정리
- reviewer가 이해할 PR body 작성

**호출 예시:**

```text
Use pr-closeout to prepare the PR body, verification summary, residual risks, and next action.
```

---

## 8.3 `pr-closeout-report`

**담당:** 더 상세한 PR closeout evidence.

**이럴 때 사용:**

- commands run
- test/eval 결과
- skipped gates와 이유
- merge readiness와 rollback

**호출 예시:**

```text
Use pr-closeout-report to produce an evidence-complete closeout with commands, metrics, skipped checks, risks, and rollback.
```

---

## 8.4 `mvp-release-manager`

**담당:** 한 MVP stage의 최종 종료와 다음 stage 진입 판정.

**이럴 때 사용:**

- stage 목표 달성 여부 확인
- artifact·test·risk closeout
- 다음 MVP 추천

**호출 예시:**

```text
Use mvp-release-manager to determine whether this MVP stage can close and what the next scoped stage should be.
```

**주의:** stage closeout은 production release나 deployment 승인이 아니다.

---

# 9. 자주 쓰는 Skill 조합

## 일반 code 구현

```text
PRIMARY: mvp-implementation
COMPANIONS:
- security-review
- asperitas-evaluation
- github-pr-review
- pr-closeout
```

## RAG·retrieval 변경

```text
PRIMARY: asperitas-rag-development
COMPANIONS:
- asperitas-retrieval
- retrieval-eval-quality-gate
- source-grounding-citation
- security-review
```

## 새로운 dependency 도입

```text
PRIMARY: open-source-adoption-review
COMPANIONS:
- dependency-security-quality-gate
- security-review
- reference-acquisition
```

## CITES·Nagoya·biological data 작업

```text
PRIMARY: compliance-biosafety-review
COMPANIONS:
- asperitas-source-audit
- asperitas-security
- source-grounding-check
```

## PR merge 전 검토

```text
PRIMARY: github-pr-review
COMPANIONS:
- security-review
- pr-closeout-report
- performance-optimization-gate
```

## 변경 없는 현황 조사

```text
PRIMARY: read-only-audit
MODE: READ
```

---

# 10. Canonical 이름과 legacy alias

새로운 요청에는 canonical 이름을 우선 사용한다.

| Legacy ID | Canonical Skill | 상태 |
|---|---|---|
| `compliance_review` | `compliance-biosafety-review` | deprecated compatibility alias |
| `retrieval_eval` | `retrieval-eval-quality-gate` | deprecated compatibility alias |
| `benchmark_workflow_preflight` | `mvp-implementation` | migration required; capability 자동 상속 금지 |

`benchmark_workflow_preflight`는 read-only preflight였고 `mvp-implementation`은 WRITE capability를 포함할 수 있으므로 단순 alias처럼 자동 전환하지 않는다.

### Filesystem-only / explicit-only Skills

다음 세 Skill은 문서와 contract는 있지만 incumbent Python `SkillSpec` registry에는 등록되지 않았다.

- `embeddings-vector-db-mvp005`
- `github-pr-review`
- `open-source-adoption-review`

이들은 요청에 이름을 명시해서 사용하며, runtime 자동 activation을 주장하지 않는다.

---

# 11. Mode와 승인 경계

| Mode | 의미 |
|---|---|
| `READ` | 읽기, 검색, 계산, 비교, 보고만 수행 |
| `DRAFT` | local plan, patch, test, 문서 초안 생성; 외부 효과 없음 |
| `WRITE` | 정확히 승인된 repository 또는 external mutation 수행 |

다음 action은 서로 독립적인 승인이 필요하다.

```text
local edit
commit
push
Draft PR creation
review comment
Ready transition
merge
release
deployment
repository setting change
delete / rollback
```

“파일을 수정해도 된다”는 승인은 “merge해도 된다”는 승인이 아니다.

---

# 12. Skill이 보장하지 않는 것

현재 Skill system이 제공하는 것:

- typed governance
- deterministic identity lookup
- permission declaration
- fail-closed evaluation policy
- GitHub mode decision cases
- human approval gate
- verification·rollback contract

현재 Skill system만으로 보장하지 않는 것:

- 30-Skill automatic runtime router
- actual runtime permission enforcement
- tool-call interception gateway
- production GitHub authorization
- production deployment
- legal·rights·scientific·biosafety approval
- model weight fine-tuning

`skill.contract.json`의 permission은 **선언된 metadata**다. 실제 side effect는 repository policy, runtime control, tool permission, action-specific human approval이 모두 충족돼야 한다.

---

# 13. 한 문장 정리

> **Asperitas Skill은 Codex가 “어떤 역할을 맡고, 어디까지 행동하며, 무엇으로 검증하고, 언제 사람의 승인을 받아야 하는지”를 통제하는 전문 execution contract다.**
