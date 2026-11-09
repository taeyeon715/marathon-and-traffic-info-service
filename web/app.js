let races = [];  // marathons_raw.csv 전체

// 1. CSV 불러오기
Papa.parse('../data/marathons_raw.csv', {
  download: true,
  header: true,
  skipEmptyLines: true,
  complete: (result) => { races = result.data; },
});

// 2. 월 버튼을 누르면 그 달 대회만 표에 보여주기
document.querySelectorAll('.month').forEach((btn) => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.month').forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    showRaces(btn.dataset.month);
  });
});

function showRaces(month) {
  const tbody = document.querySelector('#race-table tbody');
  tbody.innerHTML = '';
  races
    .filter((r) => r['날짜'].startsWith(month))  // '2026-11-07'이 '2026-11'로 시작하는지
    .forEach((r) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${r['날짜']}</td>
        <td>${r['대회명']}</td>
        <td>${r['대회종목']}</td>
        <td>${r['대회장소']}</td>
        <td>${r['교통통제'] === '1' ? '있음' : '없음'}</td>`;
      tr.addEventListener('click', () => selectRace(tr, r));
      tbody.appendChild(tr);
    });
}

// 3. 대회를 클릭하면 지도·교통통제 영역 바꾸기
function selectRace(tr, race) {
  document.querySelectorAll('#race-table tr').forEach((t) => t.classList.remove('selected'));
  tr.classList.add('selected');
  document.querySelector('#map-title').textContent = '- ' + race['대회명'];

  drawMap(race['번호']);
  showTraffic(race['번호']);
}

function drawMap(raceNo) {
  // TODO(지도 담당): waypoints.csv에서 raceNo 경유지를 찾아 #map에 코스 그리기
  document.querySelector('#map').textContent = `지도 영역 (대회번호 ${raceNo})`;
}

function showTraffic(raceNo) {
  // TODO(교통통제 담당): raceNo 대회의 통제 구간·시간 보여주기
  document.querySelector('#traffic').textContent = `교통통제 영역 (대회번호 ${raceNo})`;
}

// 4. 하단 질문 버튼
// TODO(FAQ 담당): 질문과 답변 채우기
const FAQ = [
  { q: '질문 1', a: '답변 1' },
  { q: '질문 2', a: '답변 2' },
  { q: '질문 3', a: '답변 3' },
  { q: '질문 4', a: '답변 4' },
];

FAQ.forEach((item) => {
  const btn = document.createElement('button');
  btn.textContent = item.q;
  btn.addEventListener('click', () => {
    document.querySelector('#faq-answer').textContent = item.a;
  });
  document.querySelector('#faq-buttons').appendChild(btn);
});
