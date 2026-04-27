const { chromium } = require('C:/Users/user/anaconda3/node_modules/playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ locale: 'ko-KR' });
  const page = await ctx.newPage();

  const log = [];
  page.on('request', req => {
    const u = req.url();
    if (u.includes('openfiscaldata') && u.includes('.do')) {
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

  // Try sample odtId from page 1: 재정수입구조
  const odtId = '0754F30NJD22E4T047346LC08';
  const url = `https://www.openfiscaldata.go.kr/op/ko/sd/UOPKOSDA01?odtId=${odtId}&dtaClsId=D301&ofdMngOgCd=B553658&dtaLoadPrdCd=RECY05`;
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2500);

  fs.writeFileSync('detail_rendered.html', await page.content());

  // Try to click any tab that might switch to "응답구조" or similar
  const tabs = await page.evaluate(() => {
    return [...document.querySelectorAll('a, button, .tab, [role="tab"]')]
      .map(e => ({ tag: e.tagName, text: (e.textContent || '').trim().slice(0, 60), cls: e.className, onclick: e.getAttribute('onclick'), href: e.getAttribute('href') }))
      .filter(e => e.text && /API|명세|응답|요청|구조|샘플|상세|미리|메타/.test(e.text));
  });
  fs.writeFileSync('detail_tabs.json', JSON.stringify(tabs, null, 2));

  // Click each potential tab
  for (const t of tabs.slice(0, 10)) {
    try {
      const loc = page.locator('a, button, [role="tab"], .tab').filter({ hasText: t.text.slice(0, 20) }).first();
      if (await loc.count() > 0) {
        await loc.click({ timeout: 2000 }).catch(()=>{});
        await page.waitForTimeout(800);
      }
    } catch (e) {}
  }
  await page.waitForTimeout(1000);
  fs.writeFileSync('detail_after_tabs.html', await page.content());

  fs.writeFileSync('detail_network.json', JSON.stringify(log, null, 2));
  await browser.close();
  console.log('detail done. requests:', log.length);
})();
