# 지금 당장 하는 순서 - Asperitas v10.4 Codex 적용

## 0단계 - 준비
1. GitHub repo 폴더를 연다.
2. 이 적용팩 ZIP을 repo 루트에 압축해제한다.
3. v10.4 PDF를 아래 위치에 복사한다.

```text
01_RAW_SOURCES/P0_ACTIVE_PROMPT/Asperitas_Ultimate_Prompt_Command_v10_4_20260628.pdf
```

## 1단계 - Git 상태 확인
터미널/PowerShell에서:

```powershell
git status --short
git branch --show-current
git log --oneline -5
```

## 2단계 - 작업 브랜치 생성
```powershell
git checkout main
git pull
git checkout -b chore/register-v10-4-prompt-control-plane
```

## 3단계 - Codex 첫 프롬프트 실행
Codex 새 채팅에 `CODEX_FIRST_PROMPT.txt` 내용을 붙여넣는다.

Codex가 해야 할 일:
- 현재 AGENTS.md 확인
- P0 폴더 확인
- registry 확인
- 생성/수정할 파일 목록 제시
- 바로 수정하지 않고 preflight report 제출

## 4단계 - 승인
Codex 보고서가 맞으면:

```text
APPROVE
```

이라고 답한다.

## 5단계 - 검증
Codex 작업 후, `CODEX_VERIFY_PROMPT.txt`를 붙여넣는다.

확인해야 할 것:
- active P0 constitution = v10.4
- required prompt slots 존재
- production-state non-confusion rules 존재
- KPI_REPORT 존재
- stop rules 존재

## 6단계 - 로컬 검증 명령
가능하면:

```powershell
git status --short
python scripts/verify_artifacts.py
python -m pytest
```

스크립트가 없거나 오래 걸리면 Codex에게 이유와 대체 검증을 보고하게 한다.

## 7단계 - 커밋
```powershell
git add AGENTS.md 00_ADMIN 01_RAW_SOURCES 03_PROCESSED_KB 05_EVALS 06_CODEX_HANDOFF docs
git commit -m "chore: register Asperitas v10.4 prompt control plane"
git push -u origin chore/register-v10-4-prompt-control-plane
```

## 8단계 - 다음부터 Codex 작업 방식
이후 모든 Codex 작업은 `06_CODEX_HANDOFF/codex_task_template_v10_4.md` 형식으로 요청한다.
