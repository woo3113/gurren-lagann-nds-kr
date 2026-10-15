# 천원돌파 그렌라간 (NDS) 한글패치 — **Beta v0.1 (v5 빌드)**

> 닌텐도 DS 「天元突破グレンラガン / Tengen Toppa Gurren Lagann」 (일본판, `YGRJ`) 한글패치 + 제작 툴체인

![status](https://img.shields.io/badge/status-beta-orange) ![platform](https://img.shields.io/badge/platform-Nintendo%20DS-red)

---

## 📥 적용법

1. **원본 일본판 롬** 준비 (`Tengen Toppa Gurren Lagann (Japan).nds`, 게임코드 `YGRJ`)
2. [Releases](../../releases) 에서 **`GurrenLagann_KR_beta.xdelta`** 다운로드
3. 패치:
   ```bash
   xdelta3 -d -s "Tengen Toppa Gurren Lagann (Japan).nds" GurrenLagann_KR_beta.xdelta "GurrenLagann_KR.nds"
   ```
   윈도우 GUI는 **Delta Patcher** 사용

> ⚠️ 저장소는 **패치 파일만** 배포합니다. 롬은 포함하지 않습니다.

---

## ✅ 이번 베타에 포함된 것 (v5)

| 범위 | 상태 |
|---|---|
| 시나리오 대사 (SPC 스크립트 38,335개) | ✅ 한글 |
| ARM9 UI·헤더·메뉴·기술명 | ✅ 1,016개 번역 (28개는 전각문자뿐이라 원문 유지) |
| 한글 폰트 (11×11, 1,028자) | ✅ 신규 생성 |
| **이미지 내 텍스트 (KPC/YCE)** | ✅ 일부 — `ストーリー`, `決定/却下`, `戻る`, 타이틀 인용구, 캐릭터명 등 |
| 맵 이름 | ✅ 한글 (`지하 마을` 등) |
| 고유명사 용어집 (시몬·카미나·요코·니아·그렌라간 등) | ✅ |

### 에뮬레이터 확인 완료 (melonDS 1.1)
> 타이틀 → `로드 파일 선택` → `플레이 모드 선택` → 스토리 시작 → 컷신 말풍선(한글) → 맵 진입(`지하 마을`) → 세이브 화면(`세이브 파일 선택`, `최종 결단`, `파일 4에 저장합니다. / 괜찮습니까?`)

---

## 🔧 기술 노트 (핵심)

### 정정: SPC 정지의 진짜 원인은 "쓰기 오프셋 버그"
초기 빌드는 `final.json`의 SPC `off` 값을 **텍스트 시작**으로 가정했지만, 실제로는 **명령코드 `0x10`의 위치**였습니다.
```
구조:  10 <len:u16> <Shift-JIS text> 00
        ↑off        ↑실제 텍스트 시작 = off+3
```
`off`에 그대로 쓰면 `10 <len>` 3바이트를 덮어써 **바이트코드가 깨져 검은 화면 정지**했습니다.
**`off+3`부터 쓰도록 수정**하면 맵 이름까지 전부 번역해도 멈추지 않습니다.
→ '맵 이름은 키라서 번역 금지'는 **틀린 가설**이었습니다.

### ARM9 헤더 렌더러는 전각(2바이트) 전용
UI 헤더 문자열에 **반각(ASCII) 문자가 1바이트라도 섞이면 정지**합니다.
- 원문에 ASCII가 없던 문자열 → 번역도 전각만 사용 (공백 `0x8140`, ASCII는 `+0xFEE0`)
- 원문에 ASCII가 있던 문자열 → 그 문자만 반각 유지

### 그래픽(KPC/YCE) 편집 메모
- `NFP2D.NFP` 엔트리의 size 필드는 실제 길이의 약 4배(다음 파일과 겹침). **수용 한도 = 다음 엔트리 offset − 자기 offset**
- YCE(`ECNY`): 프레임별 팔레트/타일, 레코드 `0x14`바이트, 1D 매핑. 동일 크기 편집 후 **변경 바이트만 diff 적용**
- KPC: 32×32 맵(타일 10비트+flip+팔레트뱅크), 4bpp, 팔레트 idx0 투명. **LZ10 재압축 시 displacement==1 매치 금지**(게임 디코더가 깨짐)
- 게임 폰트에 없는 한글은 넣을 수 없음 → 있는 글자로 대체 (예: '뺄'→'탈착')

---

## ⚠️ 알려진 문제 (베타)

1. **일부 이미지 텍스트 미번역** — 인트로 자막 등
2. **11×11 폰트** — 원작 폰트가 작아 한글이 빽빽함
3. **전각 공백** — 간격이 다소 넓음
4. **길이 초과로 축약된 대사** 일부 존재
5. **전체 스토리 플레이 검증 미완** — 초반부만 자동 검증했습니다. **제보 환영**

---

## 📊 규모

| 항목 | 값 |
|---|---|
| 추출 문자열 | 39,379 (ARM9 1,044 + 시나리오 38,335) |
| 고유 문장 | 9,137 |
| 번역 | DeepSeek `deepseek-chat` + 그랜라간 고유명사 용어집 |
| 한글 글리프 | 1,028자 |
| 코드 재매핑 | 안 쓰는 한자 코드 2,359개 풀에서 배정 |
| 패치 크기 | 565.8 KB |
| 롬 변경량 | 851,052 바이트 (0.63%) — font 26KB / ARM9 20KB / 그래픽 644KB / 대사 160KB |

---

## 🛠 툴체인 (`tools/`)

| 파일 | 역할 |
|---|---|
| `nft.py` | NFTR 폰트 파서/라이터 |
| `game.py` | SJIS 텍스트 추출 (ARM9 풀 / SCRP) |
| `step_extract.py` | 문자열 추출 → `out/strings.json` |
| `step_translate_ds.py` | **DeepSeek 번역 + 용어집** |
| `step_shorten_ds.py`, `step_string_ds*.py` | 길이 초과분 재번역·압축 |
| `step_assemble_ds.py` | 최종 조립 |
| `step_hangul.py` | 한글 글리프 생성 + SJIS 코드 배정 |
| `bspc.py` / `final2.py` | **v5 빌더** (SPC `off+3` 규칙 + ARM9 전각 규칙) |
| `gfx/` | KPC/YCE 파서·렌더러·편집기 (`kpc.py`, `yce.py`, `kedit.py`, `yedit.py`, `ct_ko.py` …) |
| `launch_test.ps1`, `emu_harness/` | melonDS 자동 구동 (Win / Linux+Xvfb) |
| `verify_patch.py`, `validate_encoding.py` | 검증 |

### 빌드
```
step_extract → step_translate_ds → step_shorten_ds → step_string_ds → step_string_ds2
→ step_assemble_ds → step_hangul → (bspc/final2 로 롬 조립) → gfx 패치
```

---

## 📁 롬 구조 (분석 결과)

```
루트 파일시스템 (6개, 무압축 NFP 아카이브)
├─ ETC.NFP     폰트 (GL_12FNT.NFT = NFTR 11×11 1bpp, 6,953글리프)
├─ NFP2D.NFP   2D 그래픽 (.KPC/.YCE)
├─ NFP3D.NFP   3D 모델 (.3DG)
├─ SOUND.NFP   사운드
├─ SPC.NFP     시나리오 스크립트 (.SPC = SCRP) 492개
└─ VOICE.NFP   음성
```
- **NFP**: 매직 `NFP2.0 (c)NOBORI 1997-2006`, 헤더 `0x50`, 엔트리 = `이름(16)+오프셋(4)+크기(4)`
- **NFTR**: `RTFN` + FNIF / PLGC(글리프) / HDWC(메트릭) / PAMC(CMAP, SJIS 기반)

---

## 🙏 고지

- 원작 「天元突破グレンラガン」의 권리는 **GAINAX / KDE-J / 테레비도쿄 / 반다이남코** 등 원 권리자에게 있습니다.
- 본 저장소는 **번역 데이터와 제작 툴만** 배포하며 게임 롬을 포함하지 않습니다.
- 툴체인은 자유롭게 쓰시되 원작 자산의 재배포는 하지 마세요.

## 🐛 제보
멈춤 / 깨짐 / 오역 발견 시 [Issues](../../issues)에 **씬 위치**(가능하면 스크린샷)와 함께 남겨주세요.
