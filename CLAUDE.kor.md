# CLAUDE.md SHA256: 76fcc087ab905218d3a61e120e82f2b968af14b4b20d8c1766c426c4018935e2

이 파일은 Claude Code (claude.ai/code)가 이 저장소의 코드를 작업할 때 참고하는 가이드를 제공합니다.

## 프로젝트 개요

GoogleBooksCrawler는 Selenium과 undetected-chromedriver를 사용하여 Google Play 북스에서 책 페이지를 다운로드하는 Python 기반 웹 스크래핑 도구입니다. 이 프로젝트는 다운로드된 이미지를 파이프라인을 통해 처리합니다: 다운로드 → PNG 변환 → JPEG 변환 → PDF 생성.

## 개발 환경

- **Python 버전**: 3.11.8
- **환경**: Python 가상 환경(venv)을 사용하는 Windows
- **주요 의존성**: selenium, undetected-chromedriver, Pillow, requests

### 가상 환경 설정

```bash
# 가상 환경 활성화 (Windows)
Scripts\activate

# 비활성화
deactivate
```

## 프로젝트 구조

- **Source/**: 파이프라인의 각 단계를 위한 Jupyter 노트북 포함
  - `book.ipynb`: Selenium을 사용하여 책 페이지를 다운로드하는 메인 스크래핑 로직
  - `book_to_png.ipynb`: 다운로드된 이미지를 PNG 형식으로 변환하고 검증
  - `png_to_pdf.ipynb`: PNG 이미지를 색상 보정과 함께 PDF로 변환
  - `reorder.ipynb`: 자연스러운 정렬 순서로 파일 번호 재지정
  - `test_*.ipynb`: 특정 기능 테스트를 위한 노트북

- **Downloads/**: 스크랩된 이미지의 기본 출력 디렉토리 (git에 포함되지 않음)
- **Scripts/**: Python 가상 환경 스크립트

## 핵심 워크플로우

이 도구는 다단계 파이프라인을 따릅니다:

1. **스크래핑** (book.ipynb): Selenium을 사용하여 Google Play 북스 리더를 탐색하고, iframe 콘텐츠에서 blob URL을 추출하며, JavaScript 주입을 통해 이미지를 다운로드
2. **형식 변환** (book_to_png.ipynb): 모든 이미지를 PNG 형식으로 검증 및 변환하고, 잘못 명명된 파일 감지
3. **화질 개선** (book_to_png.ipynb): 선명도 향상과 함께 PNG를 JPEG로 변환 (품질=100)
4. **파일 정렬** (reorder.ipynb): 자연스러운 숫자 순서로 파일 번호 재지정 (소수점 처리)
5. **PDF 생성** (png_to_pdf.ipynb): 색상 보정과 함께 이미지를 단일 PDF로 컴파일

## 주요 기술 세부사항

### 웹 스크래핑 전략

- 봇 감지를 우회하기 위해 undetected-chromedriver 사용
- iframe (`.-gb-display`) 내에서 탐색하여 책 콘텐츠에 접근
- 동적으로 로드된 `<img>` 요소에서 blob URL 추출
- CORS를 우회하기 위해 JavaScript `fetch()`와 blob URL 생성을 통한 다운로드
- 인증된 접근을 위한 세션 쿠키 유지
- 더 많은 페이지를 로드하기 위해 가상 스크롤 컨테이너 자동 스크롤

### 이미지 처리

- 확장자가 .png여도 PNG 형식 검증 (JPEG를 PNG로 위장한 경우 감지)
- JPEG 변환 전 선명도 향상 적용 (팩터 1.2)
- 추가 선명도를 위한 선택적 UnsharpMask 필터
- PDF 생성 시 색상 보정 (팩터 1.5)
- JPEG/PDF 작업 전 항상 RGB 모드로 변환

### 파일 관리

- 숫자 시퀀스를 처리하는 자연스러운 정렬 사용 (1, 2, 10, 11이 아닌 1, 10, 11, 2)
- 소수점 번호 처리 (1.1, 1.2 등)
- 충돌을 피하기 위한 2단계 이름 변경 (임시 이름 → 최종 이름)
- 페이지 번호를 오프셋하기 위한 구성 가능한 `force_startnum`

## 파이프라인 실행

각 노트북은 Jupyter에서 실행되도록 설계되었습니다. 일반적인 실행 순서:

1. `book.ipynb`를 실행하여 페이지 스크랩 (Google 계정에 수동 로그인 필요)
2. `book_to_png.ipynb`를 실행하여 형식 검증/변환
3. 파일 번호 재지정이 필요한 경우 선택적으로 `reorder.ipynb` 실행
4. `png_to_pdf.ipynb`를 실행하여 최종 PDF 생성

### 중요 설정

실행 전에 노트북의 경로를 업데이트하세요:
- 변환 스크립트의 `directory_path`
- book.ipynb의 `download_path`
- 0이 아닌 페이지 번호에서 시작하는 경우 `force_startnum`

## 주의사항

- 다운로드 기능을 위해 브라우저가 팝업을 허용해야 함
- 스크래핑은 무한 루프로 실행됨 (완료 시 수동으로 중단)
- 쿠키 기반 인증은 대화형 브라우저 로그인 필요
- PIL의 `ImageFile.LOAD_TRUNCATED_IMAGES = True`는 불완전한 다운로드 처리
- 스크립트 실행 전에 다운로드 디렉토리가 존재해야 함
