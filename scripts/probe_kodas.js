const { chromium } = require('C:/Users/user/anaconda3/node_modules/playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ locale: 'ko-KR' });
  const page = await ctx.newPage();

  const log = [];
  page.on('request', req => {
    const u = req.url();
    if (u.includes('openfiscaldata') && (u.includes('.do') || u.includes('UOPKOSBB'))) {
      log.push({ phase: 'req', method: req.method(), url: u, postData: req.postData() });
    }
  });
  page.on('response', async resp => {
    const u = resp.url();
    if (u.includes('openfiscaldata') && u.includes('.do')) {
      let body = null;
      try { body = (await resp.text()).slice(0, 4000); } catch (e) { body = '<<unreadable>>'; }
      log.push({ phase: 'resp', status: resp.status(), url: u, bodySnippet: body });
    }
  });

  const out = path.join(__dirname, '..', 'raw', 'kodas_probe');
  fs.mkdirSync(out, { recursive: true });

  // 1. open overview
  await page.goto('https://www.openfiscaldata.go.kr/op/ko/sb/UOPKOSBB01', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // find all subgnb / tab links to discover the "제공 데이터 목록" page
  const tabs = await page.evaluate(() => {
    return [...document.querySelectorAll('nav a, .subgnb-Wrap a, .tab a, li a')]
      .map(a => ({ text: (a.textContent || '').trim(), href: a.getAttribute('href') }))
      .filter(a => a.text && a.href && a.href.includes('UOPKOSB'));
  });
  fs.writeFileSync(path.join(out, 'overview_tabs.json'), JSON.stringify(tabs, null, 2));

  // 2. follow the "제공 데이터 목록" tab
  const dataListLink = tabs.find(t => /제공\s*데이터\s*목록/.test(t.text));
  if (dataListLink) {
    const url = new URL(dataListLink.href, 'https://www.openfiscaldata.go.kr').toString();
    log.push({ phase: 'nav', url });
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2500);
    fs.writeFileSync(path.join(out, 'data_list_p1.html'), await page.content());
    // try clicking page 2 to capture pagination payload
    try {
      const p2 = page.locator('a, button').filter({ hasText: /^2$/ }).first();
      if (await p2.count() > 0) { await p2.click(); await page.waitForTimeout(2000); }
    } catch (e) {}
    // capture total count text
    const meta = await page.evaluate(() => {
      const totals = document.body.innerText.match(/총\s*\d[\d,]*\s*건|전체\s*\d[\d,]*/g) || [];
      const ths = [...document.querySelectorAll('th')].map(th => th.textContent.trim());
      const formAction = [...document.querySelectorAll('form')].map(f => f.getAttribute('action'));
      const hiddenInputs = [...document.querySelectorAll('form input[type=hidden]')].map(i => ({ name: i.name, value: i.value }));
      const subgnb = [...document.querySelectorAll('nav a, .subgnb-Wrap a')].map(a => ({ text: a.textContent.trim(), href: a.getAttribute('href'), cls: a.className }));
      return { totals, ths, formAction, hiddenInputs, subgnb };
    });
    fs.writeFileSync(path.join(out, 'data_list_meta.json'), JSON.stringify(meta, null, 2));
  } else {
    log.push({ phase: 'err', msg: 'data list link not found in overview tabs' });
  }

  fs.writeFileSync(path.join(out, 'network.json'), JSON.stringify(log, null, 2));
  await browser.close();
  console.log('done. requests captured:', log.length, 'tabs found:', tabs.length);
})();
