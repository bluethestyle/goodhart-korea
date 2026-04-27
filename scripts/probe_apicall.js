const { chromium } = require('C:/Users/user/anaconda3/node_modules/playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ locale: 'ko-KR' });
  const page = await ctx.newPage();

  const log = [];
  page.on('request', req => {
    const u = req.url();
    if (u.includes('openapi.openfiscaldata') || u.includes('apiTest') || u.includes('Sample')) {
      log.push({ phase: 'req', method: req.method(), url: u, postData: req.postData(), headers: req.headers() });
    }
  });
  page.on('response', async resp => {
    const u = resp.url();
    if (u.includes('openapi.openfiscaldata') || u.includes('apiTest')) {
      let body = null;
      try { body = (await resp.text()).slice(0, 2500); } catch (e) { body = '<<unreadable>>'; }
      log.push({ phase: 'resp', status: resp.status(), url: u, bodySnippet: body });
    }
  });

  // 재정수입구조 detail
  const odtId = '0754F30NJD22E4T047346LC08';
  const url = `https://www.openfiscaldata.go.kr/op/ko/sd/UOPKOSDA01?odtId=${odtId}&dtaClsId=D301&ofdMngOgCd=B553658&dtaLoadPrdCd=RECY05`;
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForTimeout(2500);

  // Click OPEN API tab
  try {
    await page.locator('li.tab', { hasText: 'OPEN API' }).first().click({ timeout: 3000 });
    await page.waitForTimeout(1500);
  } catch (e) { console.log('OPEN API tab click failed:', e.message); }

  // Click 샘플URL
  try {
    await page.locator('li.tab', { hasText: '샘플URL' }).first().click({ timeout: 3000 });
    await page.waitForTimeout(1500);
  } catch (e) { console.log('샘플URL tab click failed:', e.message); }

  // capture sample URL text from the page
  const sampleText = await page.evaluate(() => {
    const all = [...document.querySelectorAll('input, textarea, code, .sample, pre')]
      .map(e => ({ tag: e.tagName, val: e.value || e.textContent || '', class: e.className }))
      .filter(o => /openapi\.openfiscaldata|http.*\?/i.test(o.val));
    return all.slice(0, 20);
  });
  fs.writeFileSync('tmp/sample_urls.json', JSON.stringify(sampleText, null, 2));

  // Try clicking Open API테스트 tab and any 호출/실행 buttons
  try {
    await page.locator('li.tab', { hasText: 'Open API테스트' }).first().click({ timeout: 3000 });
    await page.waitForTimeout(1500);
    const btn = page.locator('button', { hasText: /호출|테스트|실행|조회/ }).first();
    if (await btn.count() > 0) {
      await btn.click({ timeout: 3000 });
      await page.waitForTimeout(3000);
    }
  } catch (e) { console.log('test tab failed:', e.message); }

  fs.writeFileSync('tmp/apicall_network.json', JSON.stringify(log, null, 2));
  await page.screenshot({ path: 'tmp/apicall_screen.png', fullPage: true });
  await browser.close();
  console.log('done. requests:', log.length, 'sampleURLs:', sampleText.length);
})();
