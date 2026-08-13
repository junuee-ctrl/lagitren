# Lagi Tren — 개발 실행 계획 (DEVPLAN)

**작성:** 2026-08-13 · 기준 문서: `lagitrendevtasks.md` (외부 명세서)
**검증:** 명세서의 추정 원인을 실제 코드와 대조 완료. 아래는 코드 근거가 붙은 실행 계획.

## 명세서 대비 정정 사항 (중요)

1. **P2-1 "Google 1시간 주기" → 실제는 20분.** `collect.yml` cron `*/20`. 단축 여지는 있으나(최소 5분, GitHub Actions는 지연 잦음) "1시간이라 늦다"는 전제는 이미 해소됨. 참고로 우리 수집기는 Python이라 Workers Cron 이식 대상이 아님 — GH Actions `*/10`이 현실적 목표.
2. **P3-2 어필리에이트 자동 매칭 → 이미 구현됨.** `lib/shopping.ts`(detectCategory + relatedProducts)가 트렌드 상세에 관련 상품 노출 중이고, `affiliate_click` GA4 이벤트 트래킹도 작동 중. 남은 건 매칭 정확도 개선과 `Product` 구조화 데이터.
3. **P0-6 Instagram → 언어 필터는 이미 있음** (`base.py` acceptable_language, IG_MIN_LIKES). 없는 건 "인도네시아 관련성 가산점"이므로 그 부분만 추가.
4. **P0-4 메타태그** — 명세 그대로 유효. 단 `twitter:description`은 페이지별 metadata가 이미 있는 페이지도 있어 루트 layout의 고정값이 문제. 상수화 + 동적화로 해결.

## 실행 주체 구분

- 🌩 **클라우드(이 세션)**: 프론트/수집기 코드 수정, 배포, 검증 — repo 쓰기 권한만 있으면 전부 가능
- 💻 **로컬 PC**: tiktok/instagram/twitter(트윗) 수집 실행 — 코드는 클라우드에서 고치고, 반영은 다음 로컬 수집 때
- 👤 **사용자 직접**: 계정·가입·실명 정보 제공 (Publisher Center, Ezoic, 실명/연락처 등)

---

## Phase 0 — 버그 수정 (🌩 1일, 즉시 착수 가능)

| # | 작업 | 코드 근거 / 방법 |
|---|---|---|
| P0-1 | X 한글 mojibake | `collector/collectors/twitter_trending.py:191` `resp.text` → `resp.encoding="utf-8"` 명시. + 렌더 방어(mojibake 시그니처 감지 시 숨김). DB의 깨진 행은 수집기에 1회성 prune 로직 넣어 Actions 실행으로 삭제(내 D1 접근 불필요) |
| P0-2 | 비라틴 슬러그 | 슬러그 = `make_id()`(collector/base.py)에서 생성 → 라틴 비율<50%면 한글 로마자화/음역, 실패 시 `t-{sha256 8자}`. 프론트: 무의미 슬러그 페이지 `noindex` |
| P0-3 | /shopee→/produk 301 | `next.config.mjs`에 `redirects()` 추가. `PlatformSection.tsx:55` `href={/${platform}}` → `platformHref(platform)`. 코드 전체 `/shopee` 하드코딩 일괄 점검 |
| P0-4 | 메타태그 갱신 | 플랫폼 목록 문자열 상수화(`lib/platforms.ts`) → layout/OG/twitter description에서 참조. Netflix 포함, Shopee 문구 제거, meta-keywords 삭제 |
| P0-5 | Produk 8번 누락 | 리스트 렌더에서 rank 대신 필터 후 `index+1` 표기 (TikTok에 이미 적용한 패턴 재사용) |
| P0-6 | IG 인니 관련성 | `instagram_trending.py`에 인니 키워드/지명 가산점 + 인니어 우선 정렬 (💻 다음 로컬 수집부터 반영) |
| P0-7 | 실제 갱신 시각 | trends의 `collected_at` max를 플랫폼별로 조회 → 섹션 헤더에 "terakhir 13 Agu 14:32 WIB" 표기 |

## Phase 1 — Google Discover 준비 (🌩 2~3주, 트래픽 10배의 핵심)

**P1-1. OG 이미지 자동 생성 ⭐ 최우선**
- Next.js 내장 `ImageResponse`(satori) 사용 — @opennextjs/cloudflare에서 동작. 별도 KV/R2 없이 `Cache-Control` + Cloudflare CDN 캐시로 시작(충분하면 유지).
- 라우트: `app/og/[platform]/[slug]/route.tsx` → 1200×630. 구성: 키워드 대형 타이포(Jost) + 순위 배지 + 플랫폼 로고색 + `#` 브랜드 마크 + 그라디언트. 한글/CJK 폰트 서브셋 포함(P0-1 대응).
- 고해상 원본이 있는 경우(YouTube 썸네일·Netflix 포스터·상품 이미지) 배경 합성.
- 전 페이지 `og:image` 교체 + `max-image-preview:large` 로봇 메타 전면 적용.
- 완료 검증: Facebook Sharing Debugger / Twitter Card Validator.

**P1-2. E-E-A-T (👤 정보 필요: 운영자 실명, 연락 이메일, 소재지, SNS 링크)**
- About 보강, `/redaksi` 신설, 트렌드 하단 저자+발행/수정시각.
- JSON-LD: Organization(전역)·NewsArticle(상세, 기존 Article 업그레이드)·ItemList(목록)·Product+Offer(상품).
- `/feed.xml` RSS + 플랫폼별 피드. sitemap-index + news-sitemap(48시간).

**P1-3. 상세 페이지 기사 포맷화**
- `summarizer/prompts.py` 재설계: 리드 / Apa yang terjadi? / Kenapa rame? / Kenapa penting buat kamu? 구조, 800~1,200자.
- ⚠️ 비용: 현 3문장 대비 토큰 4~6배. 캐싱 유지 + **상위 트렌드(플랫폼별 상위 10)만 롱폼, 나머지는 기존 요약** 하이브리드로 시작 권장.
- 저품질/실패 시 noindex. 관련 뉴스 링크 전 플랫폼 확대(현재 Google만).

**P1-4. Google News Publisher Center (👤)** — P1-1~3 완료 후 사용자가 신청. 사전조건은 P1-2에서 전부 준비됨.

## Phase 2 — 속도·체류 (🌩 1주)

- **P2-1**: collect.yml `*/20`→`*/10`(공개 repo라 무료), 신규 키워드만 즉시 요약 생성(전량 재생성 금지 — 이미 캐싱 있음), **IndexNow** 핑(키 파일 + 수집기에서 신규 URL 핑), sitemap lastmod는 이미 정확.
- **P2-2**: 관련 트렌드 텍스트→썸네일 카드 그리드, 플랫폼 교차 추천(Google 상세→Netflix/Produk), "Tren lain hari ini" 더보기.
- **P2-3 (👤+🌩)**: Facebook 페이지/WA Channel/TikTok 계정 개설은 사용자, **일일 포스팅 콘텐츠 자동 생성기**(이미지 카드+캡션+링크, 하루 3~5건 분량)는 내가 구축. P1-1 선행 필수.

## Phase 3 — 수익 (P1 안정화 후)

- **P3-1 (👤+🌩)**: Ezoic 등 헤더비딩 가입은 사용자, 스크립트 통합은 나. 모바일 sticky anchor는 AdSense 자동 앵커 활성화로 먼저 시도(코드 0줄). 광고 슬롯 고정 높이 예약(CLS).
- **P3-2**: 기존 relatedProducts 매칭 정확도 개선(키워드 사전 확장) + Product 구조화 데이터(P1-2에 포함).
- **P3-3**: Google Trends 카테고리 필터(Autos/Finance/Tech/Beauty) 분기 → 롱폼 템플릿 → `/teknologi` 등 섹션. Discover 유입 확인 후 착수.

## 일정 요약

| 주차 | 내용 |
|---|---|
| 1일차 | P0 전체 (7건) + 배포·검증 |
| 1주차 | P1-1 OG 이미지 + max-image-preview + 검증 |
| 2주차 | P1-2 E-E-A-T (사용자 정보 수급 병행) + RSS/sitemap |
| 3주차 | P1-3 기사 포맷 (상위 트렌드 하이브리드) → P1-4 신청 |
| 4주차 | P2 속도·체류·소셜 자동화 |
| 이후 | P3 수익 스택 |

## 선행 조건 (차단 요소)

1. **repo 쓰기 권한**: 세션 작업공간이 초기화되며 기존 GitHub 토큰이 사라짐(보안상 오히려 잘됨 — 그 토큰은 노출 상태여서 교체 대상이었음). 구현 시작하려면 **새 fine-grained PAT**(junuee-ctrl/lagitren 한정, Contents RW + Actions RW) 필요. 또는 로컬 데스크톱 세션에서 이 계획을 실행해도 됨.
2. **P1-2 사용자 정보**: 실명(또는 법인명), 공개 가능 이메일, 소재지 표기 수준, SNS 링크.
3. **P1-3 비용 승인**: 롱폼 전환 시 Claude Haiku 비용 증가(하이브리드 기준 월 수 달러 수준 예상) — 진행 전 승인.
