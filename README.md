# 천원돌파 그렌라간 (NDS) 한글패치 — 작업 저장소

닌텐도 DS 「天元突破グレンラガン / Tengen Toppa Gurren Lagann」 (일본판, `YGRJ`) 한글패치 작업 기록 + 툴체인.

> ✅ **프리징 해결 (2026-10-14)** — 원인/해결은 [docs/FIX_NOTES.md](docs/FIX_NOTES.md). 최신 롬 `out/... (Korea) v2.nds`
>
> (아래는 해결 전 기록)
>
> ⚠️ **현재 상태: 미완성 (WIP)**
> 번역·폰트·툴체인은 완성됐지만, **텍스트를 한글로 바꾸면 게임이 특정 지점에서 멈추는 문제**를 아직 해결하지 못했습니다. 자세한 내용은 [docs/STATUS.md](docs/STATUS.md) 참고.

---

## 상태 요약

| 작업 | 상태 |
|---|---|
| 롬 구조 분석 (NFP 컨테이너 / NFTR 폰트 / SCRP 스크립트) | ✅ 완료 |
| 텍스트 추출 (39,379개 문자열) | ✅ 완료 |
| 번역 (DeepSeek + 그랜라간 고유명사 용어집) | ✅ 완료 |
| 한글 폰트 글리프 생성 (11×11, 1,028자) | ✅ 완료 |
| 패치 툴체인 (동일 길이 덮어쓰기) | ✅ 완료 |
| 검증 (헤더/파일 크기/무효 SJIS 0건) | ✅ 완료 |
| **게임 구동 시 프리징** | ❌ **미해결** |

### 미해결 문제
- **ARM9 UI 문자열**을 번역하면 `로드 파일 선택` 화면 진입 시 흰 화면 정지
  - 이분 탐색 결과 `0x11DBAC 'ロードファイル選択'` 단일 문자열이 원인
  - 게임이 이 문자열을 내부 키/조회에 쓰는 것으로 추정
- **SPC 시나리오 문자열**을 번역하면 로드 화면 이후 **검은 화면 정지**
  - 원인 문자열 미특정

---

## 대상 롬 정보

| 항목 | 값 |
|---|---|
| 타이틀 | `GURRENLAGANN` |
| Game code | `YGRJ` (maker `A4`) |
| 크기 | 128 MB |
| 미들웨어 | NFP 2.0 (c)NOBORI |

## 롬 구조 (분석 결과)

```
루트 파일시스템 (6개, 전부 무압축 NFP 아카이브)
├─ ETC.NFP     폰트 (GL_12FNT.NFT = NFTR 11x11 1bpp, 6953글리프)
├─ NFP2D.NFP   2D 그래픽 (.KPC/.YCE)
├─ NFP3D.NFP   3D 모델 (.3DG)
├─ SOUND.NFP   사운드
├─ SPC.NFP     시나리오 스크립트 (.SPC = SCRP) 492개
└─ VOICE.NFP   음성
```

- **NFP**: 매직 `NFP2.0 (c)NOBORI 1997-2006`, 헤더 0x50,
  엔트리 = `이름(16) + 오프셋(4) + 크기(4)`
- **SCRP (.SPC)**: 텍스트가 `10 <len:u16> <Shift-JIS + 00>` 형태로 바이트코드에 인라인
- **NFTR**: `RTFN` 헤더 + FNIF/PLGC(글리프)/HDWC(메트릭)/PAMC(CMAP) 블록
  - CMAP은 SJIS 기반 (method0 = 연속 매핑, method1 = u16 테이블, `0xFFFF` = 미정의)
  - 글리프 = 11×11 1bpp, 16바이트/글리프

---

## 툴체인 (`tools/`)

| 파일 | 역할 |
|---|---|
| `nft.py` | NFTR 폰트 파서/라이터 (CMAP·글리프·메트릭) |
| `game.py` | SJIS 텍스트 추출기 (ARM9 문자열 풀 / SCRP 텍스트) |
| `step_extract.py` | 번역 대상 문자열 추출 → `out/strings.json` |
| `step_translate_ds.py` | DeepSeek 번역 (용어집 포함) |
| `step_shorten_ds.py` / `step_string_ds*.py` | 길이 초과분 재번역·압축 |
| `step_assemble_ds.py` | 최종 조립 (바이트 예산 맞춤) |
| `step_hangul.py` | 한글 글리프 생성 + SJIS 코드 배정 |
| `step_build.py` | 롬 패치 (동일 길이 덮어쓰기) |
| `verify_patch.py` / `validate_encoding.py` | 검증 |
| `launch_test.ps1` | melonDS 자동 구동 테스트 (화면 상태 지표 출력) |
| `bisect_arm9.py` | 원인 문자열 이분 탐색 |

### 재빌드 순서
```powershell
python tools/step_extract.py
python tools/step_translate_ds.py
python tools/step_shorten_ds.py
python tools/step_string_ds.py
python tools/step_string_ds2.py
python tools/step_assemble_ds.py
python tools/step_hangul.py
python tools/step_build.py
python tools/verify_patch.py
```

---

## 데이터 (`out/`)

| 파일 | 설명 |
|---|---|
| `translation_table.csv` | 번역 대조표 (원문 / 번역 / 축약여부) |
| `final.json` | 최종 번역 결과 (엔트리별) |
| `charmap.json` | 한글 ↔ SJIS 코드 매핑 |
| `GurrenLagann_KR.xdelta` | 원본 롬 → 패치 롬 차분 (174 KB, 참고용) |
| `작업정리.md` | 상세 작업 정리 |

> 롬 파일(`*.nds`)과 추출물(`work/`)은 저작권 문제로 저장소에 포함하지 않습니다.

---

## 알려진 버그 (해결 완료)

1. **무효 SJIS 코드 배정** — 행 끝 패딩 엔트리(`0x89 0x7F` 등)에 한글을 배정해 텍스트 파서 폭주
   → 유효 SJIS 코드만 배정하도록 수정
2. **전각 `％` → ASCII `%`** — printf 포맷 파서 오작동 (29건)
   → 전각 `％`로 복원
3. **melonDS가 한글 경로 롬을 CLI로 열지 못함** — 자동 테스트가 계속 헛돌던 원인
   → ASCII 경로로 복사 후 실행

---

## 라이선스 / 고지

- 코드/툴체인: 자유롭게 사용 (개인 학습·연구 목적)
- 게임 원본 및 파생물의 권리는 원 권리자에게 있습니다. 롬 파일은 배포하지 않습니다.
