# 2021-2-OSSProj-OTS-7
온라인 테트리미노(like Tetris) 게임. 

클라이언트, 멀티플레이어 서버, 웹으로 구성된 프로젝트입니다.
## Teams OTS
#### 법학과 2016110652 김성현 https://github.com/kshshkim
#### 불교학부 2016110061 유동안 https://github.com/daryu519
#### 산업시스템공학과 2017112546 소준용 https://github.com/jjunyong-e


# Client

[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://www.olis.or.kr/license/Detailselect.do?lId=1006)
![Language](https://img.shields.io/badge/python-3.9-blue.svg)
![pygame](https://img.shields.io/badge/pygame-2.1.0-important)
![PySide2](https://img.shields.io/badge/PySide2-5.15.2-important)

테트리미노(like Tetris) 게임입니다. 

[**PYTRIS**](https://github.com/injekim/PYTRIS)의 포크로 시작하였으나, 코드 대부분을 재작성하였습니다. 

- 중계 서버와의 웹소켓 연결을 통한 멀티플레이
- 모듈 분리 등, 객체지향적 설계
- **pygame**의 커스텀 이벤트를 이용하는 event-driven 설계 도입(WIP)
- **QT 5** 기반 GUI 런처, 온라인 로비
- 구동에 필요한 의존성을 포함하여 바이너리 빌드, 배포(예정)
- 스테이지별 아이템 등, 게임  추가, 개선 요소

# MultiPlayer Server
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://www.olis.or.kr/license/Detailselect.do?lId=1006)
![Language](https://img.shields.io/badge/python-3.9-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.70.0-important)
![rejson](https://img.shields.io/badge/rejson-0.5.6-important)

**FastAPI**와 rejson을 기반으로 하는 온라인 중계 서버입니다. **Uvicorn**(Gunicorn), **Redis(with RedisJSON module)** 환경에서 구동됩니다.
- 웹소켓 기반 클라이언트 연결
- Redis의 Message Broker 기능을 이용한 Worker-Process 간의 통신
- 비동기 IO 처리
- 유연한 스케일링
- JWT 기반 사용자 인증(WIP)

