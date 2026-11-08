# Lion Heart · Lyric2Poster

소녀시대 〈Lion Heart〉에서 영감을 받은 빈티지 엽서 제작 앱입니다. 차트에서 곡을 선택하거나 직접 입력하고, 가사에서 아트 브리프를 만든 뒤 인쇄 스타일을 선택해 1024 × 1536 PNG를 내려받을 수 있습니다. 기본 삽화는 왕관 쓴 사자와 큐피드, 장미를 그린 AI 생성 이미지입니다.

## 실행

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m streamlit run streamlit_app.py
```

Linux에서는 한글과 라틴 글꼴을 위해 `packages.txt`의 시스템 패키지를 설치합니다. Windows에서는 맑은 고딕과 Georgia를 사용합니다.

## 키와 배포

- 키 없이 가사 분위기를 간단히 분류하는 데모 분석과 엽서 PNG 생성이 작동합니다. 샘플 목록은 실시간 순위와 구분됩니다.
- Claude는 앱에 개인 키를 입력해 사용할 수 있습니다. 운영자 키는 Streamlit Secrets의 `ANTHROPIC_API_KEY`와 `APP_PASSCODE`를 모두 설정하고 패스코드를 입력했을 때 사용합니다. Anthropic Console에서 지출 한도를 설정할 수 있습니다. 모델은 `L2P_CLAUDE_MODEL`로 변경합니다. 가사는 브리프 요청에 사용하고 입력창에서 지우며 파일에 저장하지 않습니다.
- FLUX 생성은 Streamlit Secrets의 `HF_TOKEN`과 `HF_MODEL`로 설정합니다. 추론 제공자가 지원하는 FLUX 모델을 선택하세요. 연동에 실패하면 기본 삽화로 PNG를 만듭니다.
- Last.fm 차트 갱신은 GitHub 저장소의 **Settings → Secrets and variables → Actions**에 `LASTFM_API_KEY`를 설정하면 작동합니다. 운영 전 데이터 사용 조건을 확인하세요.
- Community Cloud에서 GitHub 저장소, `main` 브랜치, `streamlit_app.py`를 지정합니다.

## 자동화

- **Poster tests**는 push, PR, 수동 실행에서 Python 3.11과 3.12로 테스트합니다.
- **Collect Last.fm charts**는 매일 서울 시간 04:17에 예약되며 수동으로 실행할 수도 있습니다. 최신 차트 JSON과 날짜별 CSV 기록을 커밋합니다. 같은 날의 기록은 교체하고, 수집에 실패한 차트는 기존 데이터를 유지합니다.

## 구성과 검증

- `streamlit_app.py`는 곡 선택, 가사 입력, 분석과 다운로드 화면을 제공합니다.
- `poster.py`는 브리프 검증, 데모 분석, FLUX 어댑터, 이미지 합성을 담당합니다.
- `collect_charts.py`는 Last.fm 응답을 차트와 기록 파일로 변환합니다.
- 자동 테스트는 데모 흐름, 가사 입력 삭제, PNG와 여섯 스타일, 브리프 검증 및 같은 날짜의 차트 재수집을 확인합니다. 외부 서비스 실호출은 별도 키가 필요합니다.

[Streamlit 배포 문서](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app) · [Claude 구조화 출력](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) · [Hugging Face 이미지 추론](https://huggingface.co/docs/inference-providers/tasks/text-to-image) · [Last.fm 차트 API](https://www.last.fm/api/show/chart.getTopTracks)
