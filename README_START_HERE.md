# Asperitas v10.4 Codex 적용팩 - START HERE

## 결론
이 팩은 Codex가 Asperitas Ultimate Prompt Command v10.4를 매 작업마다 따르도록 만드는 repo-level instruction package다.

중요: 이것은 "모델 학습/fine-tuning"이 아니다. Codex가 작업 시작 시 읽는 `AGENTS.md`, source policy, prompt templates, eval checklist, handoff templates를 repo에 넣는 방식이다.

## 지금 당장 할 일

### 1. 이 ZIP을 repo 루트에 압축해제
예시 repo:
`C:\Users\jbc89\OneDrive\문서\Asperitas AI agent\repo`

### 2. v10.4 PDF를 아래 위치에 직접 복사
```text
01_RAW_SOURCES/P0_ACTIVE_PROMPT/Asperitas_Ultimate_Prompt_Command_v10_4_20260628.pdf
```

### 3. Codex 새 채팅에 `CODEX_FIRST_PROMPT.txt` 내용을 그대로 붙여넣기
이 단계는 preflight-only다. 바로 파일을 바꾸지 않고 현재 repo 상태를 점검하게 만든다.

### 4. Codex가 파일 변경 계획을 보고하면 `APPROVE`라고 답하기
그 다음 Codex가 AGENTS.md와 필요한 문서들을 실제 repo에 생성/수정한다.

### 5. 작업 후 검증 프롬프트 실행
`CODEX_VERIFY_PROMPT.txt`를 붙여넣고 Codex가 v10.4를 제대로 로딩했는지 확인한다.

## 파일 구성
```text
AGENTS.md
CODEX_FIRST_PROMPT.txt
CODEX_VERIFY_PROMPT.txt
QUICKSTART_STEP_BY_STEP.md
00_ADMIN/source_priority_policy.md
00_ADMIN/confidentiality_policy.md
00_ADMIN/decision_log.md
00_ADMIN/source_registries/active_prompt_source_registry.csv
01_RAW_SOURCES/P0_ACTIVE_PROMPT/README.md
03_PROCESSED_KB/prompt_library/asperitas_universal_master_prompt_v10_4.md
05_EVALS/prompt_lint_checklist_v10_4.md
06_CODEX_HANDOFF/codex_task_template_v10_4.md
06_CODEX_HANDOFF/codex_review_only_template_v10_4.md
docs/AGENTS_MIGRATION_v10_3_to_v10_4.md
```

## 표현 주의
- 맞는 표현: "v10.4가 repo-level AGENTS.md와 P0 source registry에 등록됨"
- 틀린 표현: "Codex가 v10.4를 영구 학습함"
- 틀린 표현: "production DB/KG/vector/eval/legal/wet-lab 완료됨"
