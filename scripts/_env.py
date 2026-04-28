"""프로젝트 .env 자동 로드 — 의존성 없는 단순 파서.

사용:
    from _env import load_env
    load_env()                # 프로젝트 루트 .env 로드
    key = os.environ['OPENFISCAL_KEY']

키 우선순위: 이미 export된 환경변수 > .env 파일 > 없음
"""
import os

def load_env(path: str | None = None) -> dict[str, str]:
    if path is None:
        # scripts/ 또는 프로젝트 루트 어디서 호출해도 찾기
        here = os.path.dirname(os.path.abspath(__file__))
        for cand in [
            os.path.join(here, '.env'),
            os.path.join(os.path.dirname(here), '.env'),
            os.path.abspath('.env'),
        ]:
            if os.path.exists(cand):
                path = cand
                break
    if not path or not os.path.exists(path):
        return {}
    loaded = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            loaded[k] = v
            os.environ.setdefault(k, v)
    return loaded
