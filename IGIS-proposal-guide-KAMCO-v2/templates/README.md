# IGIS 제안서 디자인가이드-KAMCO · PowerPoint 템플릿

| 파일 | 내용 |
|---|---|
| `IGIS-KAMCO-template.potx` | 레이아웃 8종만 담은 템플릿. PowerPoint에서 열고 **홈 → 새 슬라이드**로 레이아웃을 고릅니다. |
| `IGIS-KAMCO-sample-deck.pptx` | 레이아웃별 샘플 슬라이드 7장 |
| `build/` | 생성 스크립트: `build-template.js`(pptxgenjs) + `postprocess.py`(python-pptx). 값은 모두 `../tokens.json`에서 읽습니다. |

## 사용 전

1. `../fonts/`의 TTF 4개(Pretendard Regular·Medium·SemiBold·Bold)를 설치합니다.
2. 최종본은 **파일 → 옵션 → 저장 → "파일의 글꼴 포함" → "모든 문자 포함"**으로 저장합니다. 발표 PC에 폰트가 없어도 그대로 보입니다.
3. PDF 백업본을 함께 준비합니다.

## 레이아웃

| 레이아웃 | 입력 영역 |
|---|---|
| IGIS 01 표지 (네이비) | eyebrow(사업명), title, meta, footer |
| IGIS 02 목차 | footer (목록은 슬라이드의 표) |
| IGIS 03 섹션 간지 (네이비) | number, title, subtitle, footer |
| IGIS 04 표준 본문 | eyebrow, title, lead, body, footer |
| IGIS 04b 제목+리드 | eyebrow, title, lead, footer (콘텐츠 자유 배치) |
| IGIS 05 2-패널 | eyebrow, title, panel A/B heading · body(● 글머리표) · tag, footer |
| IGIS 06 데이터·표 | eyebrow, title, chart, footer |
| IGIS 07 클로징 (흰 배경) | eyebrow, title, contact 1–3, disclaimer, footer |

- **푸터:** 모든 레이아웃에 `{워드마크} _ {페이지 번호}`가 있습니다. 왼쪽 footer에는 출처·단위·기준일을 씁니다.
- **발표·인쇄 공용:** 같은 파일을 발표와 인쇄에 씁니다. 네이비 배경은 표지와 간지에만 있습니다.
- **효과 차단:** 테마의 도형·배경 스타일은 단색으로만 만들었습니다. 도형 스타일 갤러리를 써도 그림자·그라데이션이 붙지 않습니다.

## 한계

- 페이지 번호는 `01`이 아니라 `1`로 표시됩니다 (PowerPoint 필드 제약).
- 연락처·수치는 예시입니다.

## 재생성

```bash
cd templates/build
npm install            # pptxgenjs 4.0.1
pip install python-pptx
npm run build
```
