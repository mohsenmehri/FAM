// Optional real-browser regression; only the synthetic local fixture is reachable.
const {chromium} = require(process.env.FAM_PLAYWRIGHT_MODULE);
const assert = require('assert');
(async () => {
  const origin = process.env.FAM_FIXTURE_ORIGIN;
  const browser = await chromium.launch({executablePath: process.env.FAM_BROWSER_EXECUTABLE,
    headless: true, args: ['--no-sandbox', '--disable-background-networking',
      '--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE 127.0.0.1']});
  try {
    const context = await browser.newContext();
    await context.route('**/*', route => route.request().url().startsWith(origin + '/')
      ? route.continue() : route.abort());
    await context.addCookies([{name:'fam_session',value:process.env.FAM_FIXTURE_COOKIE,
      url:origin,httpOnly:true,sameSite:'Strict'}]);
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(origin + '/app', {waitUntil:'domcontentloaded'});
    await page.waitForFunction(() => typeof Access !== 'undefined' && !!Access.current());
    assert.strictEqual(await page.evaluate(() => Access.can('users')), true);
    assert.strictEqual(await page.evaluate(() => Access.can('equipment')), false);
    await page.locator('#workspace-enter-panel').click();
    await page.locator('[data-act="toggle-sidebar"]').click();
    await page.locator('[data-act="manage-users"]').first().click();
    await page.waitForSelector('#user-form');
    assert.strictEqual(await page.locator('#user-broken-fixture-id').isDisabled(), true);
    await page.locator('#user-target-fixture-id').click();
    const inScope = page.locator('[data-equipment-dimension="regions"][data-equipment-ref="region-1"]');
    const outScope = page.locator('[data-equipment-dimension="regions"][data-equipment-ref="region-2"]');
    assert.strictEqual(await inScope.isChecked(), true);
    assert.strictEqual(await outScope.count(), 1);
    await inScope.uncheck(); await outScope.check();
    const saved = page.waitForResponse(r => r.url().endsWith('/api/users') && r.request().method() === 'POST');
    await page.locator('#user-save').click();
    assert.strictEqual((await saved).status(), 200);
    await page.waitForFunction(() => document.querySelector('#users-status')?.textContent.includes('ذخیره شد'));
    await page.locator('#user-target-fixture-id').click();
    assert.strictEqual(await page.locator('[data-equipment-dimension="regions"][data-equipment-ref="region-2"]').isChecked(), true);
    assert.strictEqual(await page.locator('[data-equipment-all="regions"]').isChecked(), false);
    await page.locator('#user-legacy-fixture-id').click();
    const implicitEquipment = await page.locator('[data-user-permission^="equipment-"]:checked').count();
    assert.strictEqual(implicitEquipment, 0);
    await page.locator('#user-name').fill('legacy edited');
    const legacySaved = page.waitForResponse(r => r.url().endsWith('/api/users') && r.request().method() === 'POST');
    await page.locator('#user-save').click();
    assert.strictEqual((await legacySaved).status(), 200);
    assert.strictEqual(await page.evaluate(async () => (await fetch('/api/equipment/state')).status), 403);
    assert.deepStrictEqual(errors, []);
    console.log('Browser scope editor regression: PASS');
  } finally { await browser.close(); }
})().catch(error => { console.error(error.stack); process.exitCode = 1; });
