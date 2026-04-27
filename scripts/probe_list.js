const { chromium } = require('C:/Users/user/anaconda3/node_modules/playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ locale: 'ko-KR' });
  const page = await ctx.newPage();

  const log = [];
  page.on('request', req => {
    const u = req.url();
    if (u.includes('openfiscaldata') && (u.includes('.do') || u.includes('OpenApi') || u.includes('selectOpen'))) {
      log.push({ phase: 'req', method: req.method(), url: u, postData: req.postData(), headers: req.headers() });
    }
  });
  page.on('response', async resp => {
    const u = resp.url();
    if (u.includes('selectOpenApi') || u.includes('OpenApiList') || u.includes('selectOpenApiDtl')) {
      let body = null;
      try { body = (await resp.text()).slice(0, 2000); } catch (e) { body = '<<unreadable>>'; }
      log.push({ phase: 'resp', status: resp.status(), url: u, bodySnippet: body });
    }
  });

  await page.goto('https://www.openfiscaldata.go.kr/op/ko/ds/UOPKODSA06', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);

  // Try to find pagination element and click next page
  const html1 = await page.content();
  fs.writeFileSync('rendered_p1.html', html1);

  // Look for pagination links
  const paginationInfo = await page.evaluate(() => {
    const links = [...document.querySelectorAll('a, button')]
      .filter(a => /paging|pageIndex|next|page=|fnLink|fn_paging/i.test(a.outerHTML.slice(0, 400)) || /^\d+$/.test((a.textContent || '').trim()))
      .slice(0, 30)
      .map(a => ({ tag: a.tagName, text: (a.textContent || '').trim().slice(0, 40), href: a.getAttribute('href'), onclick: a.getAttribute('onclick'), cls: a.className }));
    const totalText = document.body.innerText.match(/총\s*\d[\d,]*\s*건|전체\s*\d[\d,]*|\d+\s*\/\s*\d+\s*페이지/g) || [];
    return { links, totalText };
  });
  fs.writeFileSync('pagination_info.json', JSON.stringify(paginationInfo, null, 2));

  // Try clicking page 2 if a numeric link exists
  try {
    const page2 = page.locator('a, button').filter({ hasText: /^2$/ }).first();
    if (await page2.count() > 0) {
      await page2.click();
      await page.waitForTimeout(2500);
    }
  } catch (e) {
    log.push({ phase: 'err', msg: 'page2 click failed: ' + e.message });
  }

  fs.writeFileSync('network_log.json', JSON.stringify(log, null, 2));
  await browser.close();
  console.log('done. requests captured:', log.length);
})();
