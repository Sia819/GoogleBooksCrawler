# Google Books Crawler GUI 사용 가이드

## 개요
Google Books Crawler GUI는 Google Play Books에서 책을 스크래핑하고 이미지를 처리하는 전체 파이프라인을 그래픽 인터페이스로 제공합니다.

## 설치 및 실행

### 필수 요구사항
- Python 3.11.8 이상
- Chrome 브라우저

### 가상환경 설정 및 패키지 설치
```bash
# 가상환경 활성화 (Windows)
Scripts\activate

# 필수 패키지 설치 (이미 설치되어 있지 않은 경우)
pip install selenium undetected-chromedriver pillow requests
```

### GUI 실행
```bash
python gui_app.py
```

## 사용 방법

### 1. Scraper 탭 - 책 페이지 다운로드

1. **Initialize Driver**: Chrome 드라이버 초기화
   - 자동으로 Chrome 브라우저가 실행됩니다

2. **Book URL 입력**: Google Play Books의 책 URL 입력
   - 예: `https://play.google.com/books/reader?id=6ybeEAAAQBAJ&hl=ko`

3. **Download Path 설정**: 이미지를 저장할 폴더 경로 지정
   - Browse 버튼으로 폴더 선택 가능

4. **Navigate to Book**: 입력한 URL로 이동
   - Google 계정 로그인이 필요한 경우 브라우저에서 직접 로그인

5. **Start Scraping**: 스크래핑 시작
   - 자동으로 페이지를 스크롤하며 이미지 다운로드
   - 로그 창에서 진행 상황 확인 가능

6. **Stop Scraping**: 원하는 페이지까지 다운로드 후 중지

7. **Close Driver**: 작업 완료 후 브라우저 종료

### 2. PNG Converter 탭 - 이미지 형식 변환

#### PNG 변환
1. **Directory**: 변환할 이미지가 있는 폴더 선택
2. **Convert All to PNG**: 모든 이미지를 PNG 형식으로 변환
   - 잘못된 확장자 자동 수정
   - 진행 상황은 프로그레스바에 표시

#### JPEG 변환
1. **Output Directory**: JPEG 파일을 저장할 폴더 지정
2. **Apply Sharpness Enhancement**: 선명도 향상 옵션 (권장)
3. **Convert to JPEG**: PNG를 고품질 JPEG로 변환

### 3. File Reorder 탭 - 파일 이름 정리

1. **Directory**: 정리할 파일이 있는 폴더 선택

2. **Options 설정**:
   - File Extension: 정리할 파일 확장자 (기본: .png)
   - Start Number: 시작 번호 (기본: 0)

3. **Preview Files**: 변경될 파일명 미리보기
   - 현재 파일명 → 새 파일명 형식으로 표시

4. **Rename Files**: 실제 파일명 변경 실행
   - 자연스러운 숫자 순서로 정렬 (1, 2, 10, 11 순서)
   - 소수점 번호도 올바르게 처리 (1.1, 1.2 등)

### 4. PDF Creator 탭 - PDF 생성

1. **Source Directory**: PNG 이미지가 있는 폴더 선택

2. **Output PDF**: 생성할 PDF 파일 경로 지정
   - Browse 버튼으로 저장 위치와 파일명 지정

3. **Options**:
   - Enhance Colors: 색상 향상 (기본: 활성화)
   - Color Factor: 색상 강도 조절 (1.0~2.0, 기본: 1.5)

4. **Create PDF**: PDF 파일 생성
   - 모든 PNG 파일을 하나의 PDF로 병합
   - 진행 상황은 프로그레스바와 로그에 표시

## 전체 작업 흐름

1. **Scraper 탭**에서 책 페이지 다운로드
2. **PNG Converter 탭**에서 이미지 형식 검증 및 변환
3. **File Reorder 탭**에서 파일명 정리 (필요시)
4. **PDF Creator 탭**에서 최종 PDF 생성

## 주의사항

- 스크래핑 시 팝업 차단을 해제해야 합니다
- Google 계정 로그인이 필요한 책의 경우 브라우저에서 직접 로그인
- 스크래핑은 수동으로 중지할 때까지 계속됩니다
- 대용량 이미지 처리 시 시간이 걸릴 수 있습니다

## 문제 해결

### Chrome 드라이버 초기화 실패
- Chrome 브라우저가 설치되어 있는지 확인
- undetected-chromedriver 재설치: `pip install --upgrade undetected-chromedriver`

### 이미지 다운로드 실패
- 브라우저의 다운로드 권한 확인
- 다운로드 폴더 쓰기 권한 확인

### PDF 생성 실패
- PNG 파일이 올바른 형식인지 확인
- 디스크 공간이 충분한지 확인