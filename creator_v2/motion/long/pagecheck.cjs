const { pathToFileURL } = require('url');
const result = { pageerrors: [], console_errors: [], timelines: {} };
let browser;
(async () => {
  const puppeteer = require(process.argv[2]);
  browser = await puppeteer.launch({ executablePath: process.argv[3], headless: true,
    args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage();
  page.on('pageerror', error => result.pageerrors.push(error.stack || error.message));
  page.on('console', message => {
    if (message.type() === 'error') result.console_errors.push(message.text());
  });
  await page.goto(pathToFileURL(process.argv[4]).href, { waitUntil: 'load', timeout: 60000 });
  await new Promise(resolve => setTimeout(resolve, 4000));
  result.timelines = await page.evaluate(() => Object.fromEntries(
    Object.entries(window.__timelines || {}).map(([key, tl]) =>
      [key, typeof tl.duration === 'function' ? tl.duration() : null])));
})().catch(error => { result.fatal = error.message; }).finally(async () => {
  if (browser) await browser.close().catch(() => {});
  process.stdout.write(JSON.stringify(result));
});
