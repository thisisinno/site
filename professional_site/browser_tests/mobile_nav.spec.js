const { test, expect } = require("@playwright/test");

const baseURL = process.env.TEST_BASE_URL || "http://127.0.0.1:8000";
const viewports = [
  [320, 568], [360, 640], [375, 667], [390, 844], [393, 852],
  [412, 915], [430, 932], [568, 320], [667, 375], [844, 390],
];
const expectedLinks = [
  ["Home", "/"],
  ["About Me", "/about/"],
  ["Curriculum Vitae", "/curriculum-vitae/"],
  ["Articles", "/articles/"],
  ["Research & Publications", "/research-publications/"],
  ["Professional Experience", "/professional-experience/"],
  ["Projects", "/projects/"],
  ["Gallery", "/gallery/"],
  ["Testimonials", "/testimonials/"],
  ["Let’s Connect", "/contact/"],
];

async function waitForPage(page) {
  await page.goto(baseURL, { waitUntil: "networkidle" });
  await expect(page.locator("#siteLoader")).toHaveClass(/is-hidden/, { timeout: 4000 });
}

async function openDrawer(page) {
  await page.locator("#mobileNavTrigger").click();
  await expect(page.locator("#mobileNav")).toHaveClass(/is-open/);
  await expect(page.locator("#mobileNavBackdrop")).toHaveClass(/is-open/);
  await expect(page.locator("body")).toHaveClass(/mobile-nav-open/);
  await expect(page.locator("#mobileNavTrigger")).toHaveAttribute("aria-expanded", "true");
}

for (const [width, height] of viewports) {
  test(`custom drawer is reliable at ${width}x${height}`, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await waitForPage(page);

    const hitTarget = await page.locator("#mobileNavTrigger").evaluate(trigger => {
      const rect = trigger.getBoundingClientRect();
      const hit = document.elementFromPoint(rect.left + rect.width / 2, rect.top + rect.height / 2);
      return hit === trigger || trigger.contains(hit);
    });
    expect(hitTarget).toBe(true);

    await openDrawer(page);
    await page.waitForTimeout(350);
    const links = await page.locator("#mobileNav a").evaluateAll(anchors => anchors.map(anchor => {
      const rect = anchor.getBoundingClientRect();
      const style = getComputedStyle(anchor);
      return {
        text: anchor.textContent.trim(),
        width: rect.width,
        height: rect.height,
        visibility: style.visibility,
        opacity: style.opacity,
        pointerEvents: style.pointerEvents,
      };
    }));
    expect(links).toHaveLength(expectedLinks.length);
    for (const link of links) {
      expect(link.width).toBeGreaterThan(0);
      expect(link.height).toBeGreaterThan(0);
      expect(link.visibility).toBe("visible");
      expect(link.opacity).toBe("1");
      expect(link.pointerEvents).not.toBe("none");
    }
    expect(await page.locator(".mobile-nav-body").evaluate(element => ({
      overflowY: getComputedStyle(element).overflowY,
      scrollHeight: element.scrollHeight,
      clientHeight: element.clientHeight,
    }))).toEqual(expect.objectContaining({ overflowY: "auto" }));
    expect(await page.locator("body").evaluate(element => getComputedStyle(element).overflowY)).toBe("hidden");
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);

    await page.locator(".mobile-nav-close").click();
    await expect(page.locator("#mobileNav")).not.toHaveClass(/is-open/);
    await expect(page.locator("body")).not.toHaveClass(/mobile-nav-open/);
    await expect(page.locator("#mobileNavTrigger")).toBeFocused();

    await openDrawer(page);
    if (width > 420) {
      await page.locator("#mobileNavBackdrop").click({ position: { x: 5, y: 5 } });
      await expect(page.locator("#mobileNav")).not.toHaveClass(/is-open/);
    } else {
      await page.locator("#mobileNavBackdrop").dispatchEvent("click");
      await expect(page.locator("#mobileNav")).not.toHaveClass(/is-open/);
    }

    await openDrawer(page);
    await page.keyboard.press("Escape");
    await expect(page.locator("#mobileNav")).not.toHaveClass(/is-open/);
  });
}

test("every mobile link navigates on its first click", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  for (const [name, path] of expectedLinks) {
    await waitForPage(page);
    await openDrawer(page);
    const link = page.locator(`#mobileNav a[href="${path}"]`);
    await expect(link).toContainText(name);
    await link.click();
    await page.waitForURL(url => url.pathname === path, { timeout: 4000 });
  }
});

test("focus is trapped and desktop breakpoint resets all state", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await waitForPage(page);
  await openDrawer(page);
  const first = page.locator("#mobileNav").locator('a[href], button:not([disabled])').first();
  const last = page.locator("#mobileNav").locator('a[href], button:not([disabled])').last();
  await first.focus();
  await page.keyboard.press("Shift+Tab");
  await expect(last).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(first).toBeFocused();

  await page.setViewportSize({ width: 1400, height: 900 });
  await expect(page.locator("#mobileNav")).not.toHaveClass(/is-open/);
  await expect(page.locator("#mobileNavBackdrop")).not.toHaveClass(/is-open/);
  await expect(page.locator("body")).not.toHaveClass(/mobile-nav-open/);
  await expect(page.locator("#mobileNavTrigger")).toHaveAttribute("aria-expanded", "false");
});

test("drawer is independent of Bootstrap Offcanvas and survives rotation", async ({ page }) => {
  const consoleErrors = [];
  page.on("console", message => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await waitForPage(page);
  await page.evaluate(() => {
    if (window.bootstrap) window.bootstrap.Offcanvas = undefined;
  });
  await openDrawer(page);
  await page.setViewportSize({ width: 844, height: 390 });
  await page.locator(".mobile-nav-close").click();
  await page.setViewportSize({ width: 390, height: 844 });
  await openDrawer(page);
  await expect(page.locator("#mobileNav")).toHaveClass(/is-open/);
  await page.locator(".mobile-nav-close").click();
  expect(consoleErrors).toEqual([]);
});

test("back navigation restores a closed, scrollable drawer state", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await waitForPage(page);
  await openDrawer(page);
  await page.locator('#mobileNav a[href="/articles/"]').click();
  await page.waitForURL(url => url.pathname === "/articles/");
  await page.goBack({ waitUntil: "domcontentloaded" });
  await expect(page.locator("#mobileNav")).not.toHaveClass(/is-open/);
  await expect(page.locator("#mobileNavBackdrop")).not.toHaveClass(/is-open/);
  await expect(page.locator("body")).not.toHaveClass(/mobile-nav-open/);
  await expect(page.locator("#mobileNavTrigger")).toHaveAttribute("aria-expanded", "false");
});
