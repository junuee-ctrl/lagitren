# Lagi Tren — 세션 인수인계 (Handoff)

> 이 문서 하나면 다른 세션이 처음부터 설명 안 듣고 이어서 작업할 수 있게 정리한 거야.
> 작성 시점: 2026-07-14. 저장 위치: repo 루트 `HANDOFF.md`.

---

## 0. 지금 당장 할 일 (이 세션에 컴퓨터 제어 권한이 있다면)

이전 세션은 클라우드 샌드박스라 사용자 PC에 접근을 못 했음. **이 세션은 remote-devices(파일/로컬 실행) 권한을 받았다고 함.** 그래서 아래를 사용자 PC에서 직접 실행하는 게 최우선 작업:

1. 사용자 PC의 collector 폴더로 이동 (경로 예: `C:\lagitren\collector` — 실제 경로는 확인 필요).
2. `git pull` 로 최신 코드 받기.
3. **`setup_local.bat` 실행** — 이게 전부 자동으로 함:
   - `git pull` → 크롬 3탭(TikTok Trends·Instagram·X) 로그인 창 → 사용자가 로그인 → `run_local.py` 수집 → `schtasks`로 3시간마다 자동 갱신 등록.
   - 로그인 단계만 사람 손 필요(계정 자격증명 입력). 나머지 자동.
4. 실행 후 터미널 마지막 줄 `Ringkasan: {'tiktok': N, 'instagram': N, 'twitter': N}` 확인.
5. **검증**: `https://lagitren.id/tiktok` 과 `https://lagitren.id/api/collect-debug` 확인 → 틱톡 해시태그가 이전 3개에서 **~20개**로 늘고, 대표 비디오/인스타/X 트윗이 붙었는지.

> ⚠️ 주의: 로그인 크롤은 **사용자의 실제 로그인된 크롬 + 자카르타 가정용 IP**가 있는 PC에서만 제대로 됨. remote-devices 브릿지가 샌드박스 리눅스 VM만 준다면 실제 윈도우 크롬 조종은 안 될 수 있음 — 그 경우엔 사용자가 직접 `setup_local.bat`을 더블클릭하게 안내.

---

## 1. 프로젝트 개요

- **제품**: Lagi Tren (lagitren.id) — 인도네시아 실시간 트렌드 애그리게이터.
- **대상**: 인도네시아 18–40세. 사이트 언어 = **Bahasa Indonesia**.
- **플랫폼 7개(표시 순서)**: Google → YouTube → Instagram → TikTok → Netflix → X(Twitter) → **Produk Viral**(TikTok Shop 제휴 상품).
- **수익 모델**: Google AdSense + TikTok Shop/Tokopedia 제휴(affiliate). 목표: 월 $3,000.
- **repo**: github.com/junuee-ctrl/lagitren (branch: `main`). **호스팅**: Cloudflare(GitHub 자동 배포).

## 2. 아키텍처

- **프론트엔드**: Next.js 14 (App Router) + Tailwind CSS → `@opennextjs/cloudflare` → Cloudflare Workers.
- **DB**: Cloudflare **D1**(SQLite), binding `DB`. Python collector가 D1 REST API로 write.
- **collector(Python)** — 하이브리드:
  - **클라우드(GitHub Actions cron)**: google, youtube, twitter(검색), netflix, shopee(products.csv) — 공개 데이터라 서명/로그인 불필요.
  - **로컬 PC(자카르타)**: tiktok, instagram, twitter(대표 트윗) — 로그인·안티봇 서명 필요 → Playwright로 로그인된 크롬 조종.
- **AI 요약**: Ollama(로컬) 우선 / Claude Haiku(fallback). 요약 캐싱 있음.
- **Netflix 보강**: TMDB(포스터/시놉시스, 키 있음) → Wikipedia → iTunes fallback. 매일 갱신.

## 3. 디자인 시스템 (완료)

- 무드: 생동감·플레이풀. 브랜드색 **마젠타 #E6007A** + **틸 #00C9B1**(보조 그레이프 #8B3DD6). Produk색 #FE2C55.
- **라이트/다크 토글**(localStorage, no-FOUC). Tailwind `darkMode:"class"`.
- 로고: `#` 글리치 마크(마젠타+틸) + "lagi tren.id" 워드마크. "lagi"=잉크/화이트, "tren"+"id"=브랜드색, "." = lagi와 같은 색. 폰트 = **Jost**(지오메트릭, Century Gothic 대체 — 원본은 상용이라 임베드 불가).
- 플랫폼 아이콘 = 실제 브랜드 로고(react-icons/si). tiktok/twitter는 near-black이라 테마 대응 색.
- Netflix는 포스터 그리드(영화/TV 분리). Produk 상세엔 관련 상품 카드(카테고리 매칭).

## 4. 이번 세션에서 한 일 (핵심)

### (A) 틱톡 "해시태그 3개만" 문제 — 수집기 강화 (commit ed2c8e6)
- 원인 2가지: (1) 수집기가 **첫 파싱되는 응답**에서 멈춰서, 초기 3줄짜리 응답이면 그걸로 끝남. (2) 틱톡 Trends는 **로그인 없으면 상위 ~3개만** 보여주고 나머진 잠금.
- 수정: `collector/collectors/tiktok_trending.py`
  - `PAGE_URLS`에 새 Trends URL(`ads.tiktok.com/creative/creativeCenter/trends/hashtag?region=ID&period=7`) 우선 + 기존 URL fallback.
  - 모든 응답 중 **가장 긴 목록** 채택(첫 응답 아님).
  - 폴링 15회로 늘리고 스크롤 + `_click_view_more()`(View more/Selengkapnya 클릭) 추가.
- 클라우드 직접 호출은 불가 확인: API가 `{"code":40101,"msg":"no permission"}`(서명 필요), 페이지는 JS 없이 "No data available". → 로컬 로그인 브라우저만 가능.

### (B) 전용 로그인 브라우저 통일 (commit 18db252)
- 함정: 로그인 저장 프로필이 `.browser_profile`(login_browser 옛버전)와 `chrome-lagitren`(run_local/CDP)로 **갈려 있어서** 로그인해도 크롤에 안 쓰일 수 있었음.
- 수정: `start_chrome.py`가 3탭(TikTok Trends·Instagram·X) 열도록, `login_browser.py`는 `start_chrome`로 위임 → **모두 `chrome-lagitren` 단일 프로필** 사용. `run_local.py`는 tiktok+instagram+twitter 수집.

### (C) 원클릭 셋업 + 자동 스케줄 (commit b2a30fc)
- `collector/setup_local.bat`: git pull → 로그인 창 → 수집 → `schtasks /Create ... LagiTrenCollect`(3시간마다) 등록까지 한 방.
- `collector/run_local_task.bat`: 스케줄러가 호출하는 실행 파일(venv 활성화 포함).

### (D) 상품 이미지 — 클라우드에선 불가, fallback 개선 (commit ed2c8e6 일부, cf28603)
- 클라우드에서 상품 이미지 자동 취득 **전부 실패 확인**: Tokopedia=provenance 차단, 브랜드/리테일러=403·404, 이미지검색=robots 차단.
- 유일한 안정 경로: `collector/enrich_products.py` — 사용자 로그인 크롬으로 각 affiliate_url 열어 og:image 추출 → products.csv `image` 채움(1회 실행).
- 임시 개선: `components/RelatedProducts.tsx` — 이미지 없을 때 **카테고리별 컬러 타일(이모지+제품명)**로 표시(빈 회색박스 방지).

## 5. Produk(TikTok Shop 제휴) 현황

- `collector/products.csv` = 상위 20개 베스트셀러, 사용자 실제 제휴링크 채워짐(형식 `https://shop-id.tokopedia.com/view/product/{id}?region=ID&locale=en&source=agency`). 컬럼: title,image(비어있음),price,sales,category,affiliate_url.
- collector `shopee` 키가 `shopping_products.py`로 이 CSV를 읽어 사이트에 노출(클라우드에서 동작, 20개 라이브 확인됨).
- **남은 것**: `image` 컬럼이 비어 있음 → `enrich_products.py`를 로컬 로그인 크롬에서 1회 실행해 채우고 commit/push 하면 실제 상품사진 노출.

## 6. 검증 방법

- 로컬 수집 후: `https://lagitren.id/api/collect-debug` 로 각 플랫폼 `LAST_DEBUG` 확인(예: `ok: 20 hashtag (ID), 10 video`).
- 라이트빌드 확인: repo 루트에서 `npx tsc --noEmit`(타입), `npm run build`(풀빌드).
- 화면 확인: `/tiktok`, `/produk`(=`/shopee` 라우트), 상세페이지 관련상품 카드.

## 7. 남은 작업 / 알려진 이슈

- [ ] **로컬 수집 실제 실행**(setup_local.bat) → 틱톡 20개·인스타·X 채우기. **최우선**.
- [ ] **상품 이미지**: `enrich_products.py` 로컬 1회 실행 → products.csv image 채우고 push.
- [ ] **X(Twitter) 대표 트윗**: 크롬에 X 로그인돼 있어야 함(현재 0/8). setup_local의 X 탭 로그인으로 해결.
- [ ] **상단 메뉴 "Produk" 링크**: 사용자가 "잘못 링크된 것 같다"고 지적했었음. 가설 = "Produk" 메뉴가 `/shopee`로 가는데 라우트/라벨 불일치. 미해결 — 실제로 어느 항목이 깨지는지 확인 필요(라우트를 `/produk`로 바꾸는 것도 옵션).
- [ ] **보안 위생**: 노출된 키 교체 필요 — GitHub PAT(현재 remote URL에 평문 포함), Cloudflare API 토큰, TMDB 키, Anthropic 키. 사용자가 이전에 보류함.
- [ ] AdSense 승인 준비, 제휴 수익 최적화(장기).

## 8. 주요 파일 지도

- 프론트: `app/[platform]/page.tsx`(리스트), `app/[platform]/[slug]/page.tsx`(상세), `components/`(Logo, ThemeToggle, PlatformIcon, NetflixSplit, RelatedProducts, TrendListItem 등), `lib/`(platforms.ts, shopping.ts, db.ts, types.ts).
- collector: `collectors/tiktok_trending.py`(강화됨), `instagram_trending.py`, `twitter_trending.py`, `netflix_trending.py`, `shopping_products.py`, `_browser.py`(프로필/CDP), `run_local.py`, `start_chrome.py`, `login_browser.py`, `setup_local.bat`, `run_local_task.bat`, `enrich_products.py`, `products.csv`.
- 규칙: `CLAUDE.md`(루트), `collector/CLAUDE.md`, `collector/LOCAL_COLLECTOR.md`.

## 9. 최근 커밋

```
b2a30fc setup_local.bat: pull+login+crawl+jadwal 3 jam (satu klik)
18db252 로컬 크롤 로그인 프로필 chrome-lagitren로 통일, 3탭(TikTok/IG/X)
ed2c8e6 TikTok Trends 새 URL + 최장 목록 채택(3개 버그 fix); Produk 이미지없을때 카테고리 타일
cf28603 enrich_products.py: 로그인 브라우저로 상품 이미지 채우기
e372934 TikTok Shop 상품 products.csv 20개
```

---

## 세션 2 (2026-07-15) — 데스크톱 로컬 세션에서 진행

> 이 세션은 사용자 PC(로컬 폴더 `C:\lagitren` 연결)에서 실행됨. 파일 편집·git·collector 직접 실행 가능.
> **원격/모바일 세션에서는 로컬 파일 접근 불가** — collector 로그인 크롤/이미지 수집은 이 PC(로그인된 chrome-lagitren 프로필)에서만 가능.

### 배포된 커밋 (main)
- `00307f2` feat(produk): 상품 이미지 고해상도(썸네일→원본 CDN)
- `0eddbff` feat(produk): 상품 이미지 Google Images로 채움(썸네일)
- `882841a` feat(tiktok): 해시태그/비디오 2섹션 분리 + 순위 1..N
- `91d0b1c` feat(nav): Produk URL `/produk` 통일 + cloudflare_api.txt gitignore

### 이번 세션에 한 일
1. **Produk 메뉴 링크 → `/produk` 통일.** `lib/platforms.ts`에 `PLATFORM_SLUG`(shopee→produk)/`platformHref`/`keyFromSlug` 추가. Header/Footer/`[platform]`/`[slug]`/sitemap 전부 `platformHref` 사용. `/shopee`는 하위호환으로 계속 동작.
2. **TikTok 2섹션 분리.** 새 컴포넌트 `components/TikTokSplit.tsx` — "Video lagi viral"(대표영상 그리드) + "Hashtag lagi tren"(순위 목록). 순위는 섹션별 `index+1` 재부여 → **21+ 이상 순위 버그 fix**. 수집기 `tiktok_trending.py` rank도 순차(`rank=i`)로 근본 수정.
3. **로컬 수집 실행.** `{tiktok:20, instagram:15, twitter:20}` D1 저장. 스케줄 `LagiTrenCollect`(3시간)는 **이미 등록됨**.
4. **상품 이미지.** `enrich_products.py`(Tokopedia og:image)는 0/20 실패 확인. 새로 `collector/gimg_run.py` 작성 — Google Images에서 상품명 전체로 검색해 **원본 대형 이미지 URL** 추출 → `products.csv` image 채움 → `shopee` 수집기로 D1 반영. 20/20 성공.

### 남은 일
- [ ] **보안 키 교체(사용자 직접)**: GitHub PAT(remote URL 평문), Cloudflare 토큰, TMDB, Anthropic 키.
- [ ] 상품 이미지 일부는 머천트 CDN **핫링크 차단**으로 사이트에서 안 뜰 수 있음 → 확인 후 필요시 대체.
- [ ] `collector/gimg_run.py`/`run_local.py`는 **로컬 로그인 크롬(CDP 9222)** 필요 → 원격/모바일 세션에서 실행 불가.

### 로컬 실행 팁
- git 업데이트: `C:\lagitren\git-update.bat` 더블클릭(stash→pull→pop).
- 수집(수동): `collector\`에서 `python run_local.py` (tiktok/ig/x).
- 상품 이미지 재수집: `collector\`에서 `python gimg_run.py` → `python -c "from main import run; run(['shopee'])"` 로 D1 반영.
- **마운트 주의**: 큰 파일은 샌드박스 읽기/편집이 잘릴 수 있어, 파일 편집·git 커밋은 **네이티브(Windows)** 로 하는 게 안전.

---

## 애널리틱스/광고 최종 상태 (2026-07-19 확정 — 변경 금지)

- **GA4 측정 ID: `G-CMQVHLJJTY`** (app/layout.tsx의 GA_ID 기본값). 실시간 수집 검증 완료.
  - 이전 ID들(G-CZCFHY3VWY, GT-TWTPKF3C, G-H75SZLGOLP/G-H75SZLG0LP)은 폐기 — 절대 되돌리지 말 것.
  - 교훈: 측정 ID는 심기 전에 `googletagmanager.com/gtag/js?id=...`가 200인지 검증할 것 (0/O 오독으로 하루 낭비했음).
- **AdSense**: 게시자 ID `ca-pub-1581394816942984` (lib/adsense.ts). ads.txt 자동 생성 OK.
  - 광고 단위 슬롯: atas=9914312757, bawah=4661986078, beranda=9618799281 (lib/adsense.ts AD_SLOTS).
  - 사이트 심사 "준비 중" — 승인되면 광고 자동 게재.
- 제품 클릭 추적: `affiliate_click` 이벤트 (components/AffiliateLink.tsx) → GA4로 전송.
