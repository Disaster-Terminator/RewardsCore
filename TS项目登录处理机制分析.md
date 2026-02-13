# TypeScript 项目登录处理机制分析

## 问题背景

Python 脚本在登录时遇到不定的拒绝问题：

- 输完密码后有时弹出 "Please retry with a different device or other authentication method"
- 有时会弹出 2FA 验证

## TS 项目的核心解决方案

### 1. 状态机驱动的登录流程

TS 项目使用**状态机模式**处理登录的不确定性，而不是线性流程：

```typescript
type LoginState =
    | 'EMAIL_INPUT'           // 输入邮箱
    | 'PASSWORD_INPUT'        // 输入密码
    | 'SIGN_IN_ANOTHER_WAY'   // 选择其他登录方式（密码）
    | 'SIGN_IN_ANOTHER_WAY_EMAIL' // 选择其他登录方式（邮件验证码）
    | 'PASSKEY_ERROR'         // Passkey 错误
    | 'PASSKEY_VIDEO'         // Passkey 提示视频
    | 'KMSI_PROMPT'           // "保持登录" 提示
    | 'LOGGED_IN'             // 已登录
    | 'RECOVERY_EMAIL_INPUT'  // 恢复邮箱输入
    | 'ACCOUNT_LOCKED'        // 账号被锁
    | 'ERROR_ALERT'           // 错误提示
    | '2FA_TOTP'              // 2FA TOTP 验证
    | 'LOGIN_PASSWORDLESS'    // 无密码登录
    | 'GET_A_CODE'            // 获取验证码页面（有密码）
    | 'GET_A_CODE_2'          // 获取验证码页面（无密码）
    | 'OTP_CODE_ENTRY'        // OTP 验证码输入
    | 'UNKNOWN'               // 未知状态
    | 'CHROMEWEBDATA_ERROR'   // Chrome 数据错误
```

### 2. 循环检测 + 状态转换

核心登录逻辑：

```typescript
const maxIterations = 25
let iteration = 0
let previousState: LoginState = 'UNKNOWN'
let sameStateCount = 0

while (iteration < maxIterations) {
    iteration++
    
    // 1. 检测当前状态
    const state = await this.detectCurrentState(page, account)
    
    // 2. 检测是否卡在同一状态
    if (state === previousState && state !== 'LOGGED_IN') {
        sameStateCount++
        if (sameStateCount >= 4) {
            // 卡住了，刷新页面重试
            await page.reload({ waitUntil: 'domcontentloaded' })
            sameStateCount = 0
            previousState = 'UNKNOWN'
            continue
        }
    } else {
        sameStateCount = 0
    }
    
    // 3. 如果已登录，退出循环
    if (state === 'LOGGED_IN') break
    
    // 4. 处理当前状态
    const shouldContinue = await this.handleState(state, page, account)
    if (!shouldContinue) {
        throw new Error(`Login failed at state: ${state}`)
    }
    
    previousState = state
    await this.bot.utils.wait(1000)
}
```

### 3. 智能状态检测

`detectCurrentState()` 方法通过**并行检测多个选择器**来判断当前页面状态：

```typescript
private async detectCurrentState(page: Page, account?: Account): Promise<LoginState> {
    // 1. 检查 URL
    const url = new URL(page.url())
    if (url.hostname === 'rewards.bing.com') return 'LOGGED_IN'
    
    // 2. 并行检测所有可能的状态
    const stateChecks: Array<[string, LoginState]> = [
        [this.selectors.errorAlert, 'ERROR_ALERT'],
        [this.selectors.passwordEntry, 'PASSWORD_INPUT'],
        [this.selectors.emailEntry, 'EMAIL_INPUT'],
        [this.selectors.recoveryEmail, 'RECOVERY_EMAIL_INPUT'],
        [this.selectors.totpInput, '2FA_TOTP'],
        [this.selectors.otpCodeEntry, 'OTP_CODE_ENTRY'],
        // ... 更多状态检测
    ]
    
    const results = await Promise.all(
        stateChecks.map(async ([sel, state]) => {
            const visible = await this.checkSelector(page, sel)
            return visible ? state : null
        })
    )
    
    // 3. 按优先级返回状态
    const priorities: LoginState[] = [
        'ACCOUNT_LOCKED',
        'PASSKEY_VIDEO',
        'PASSWORD_INPUT',
        'EMAIL_INPUT',
        'SIGN_IN_ANOTHER_WAY',
        'OTP_CODE_ENTRY',
        '2FA_TOTP'
        // ...
    ]
    
    for (const priority of priorities) {
        if (foundStates.includes(priority)) {
            return priority
        }
    }
}
```

### 4. 针对 "Get a Code" 拒绝页面的处理

这是你遇到的核心问题！TS 项目有专门的处理逻辑：

```typescript
case 'GET_A_CODE': {
    // 尝试绕过 "Get code" 页面
    
    // 方法 1: 点击 "Other ways to sign in" 链接
    const otherWaysLink = await page
        .waitForSelector(this.selectors.otherWaysToSignIn, { 
            state: 'visible', 
            timeout: 3000 
        })
        .catch(() => null)
    
    if (otherWaysLink) {
        await this.bot.browser.utils.ghostClick(page, this.selectors.otherWaysToSignIn)
        return true
    }
    
    // 方法 2: 尝试通用的 footer 链接
    const footerLink = await page
        .waitForSelector(this.selectors.viewFooter, { 
            state: 'visible', 
            timeout: 2000 
        })
        .catch(() => null)
    
    if (footerLink) {
        await this.bot.browser.utils.ghostClick(page, this.selectors.viewFooter)
        return true
    }
    
    // 方法 3: 点击返回按钮
    const backBtn = await page
        .waitForSelector(this.selectors.backButton, { 
            state: 'visible', 
            timeout: 2000 
        })
        .catch(() => null)
    
    if (backBtn) {
        await this.bot.browser.utils.ghostClick(page, this.selectors.backButton)
        return true
    }
    
    return true
}
```

**关键选择器：**

```typescript
otherWaysToSignIn: '[data-testid="viewFooter"] span[role="button"]'
viewFooter: '[data-testid="viewFooter"] >> [role="button"]'
backButton: '#back-button'
```

### 5. OTP 验证码页面的处理

当 Microsoft 强制要求 OTP 验证码时：

```typescript
case 'OTP_CODE_ENTRY': {
    // 尝试找到 "Use your password" 选项
    const footerLink = await page
        .waitForSelector(this.selectors.viewFooter, { 
            state: 'visible', 
            timeout: 2000 
        })
        .catch(() => null)
    
    if (footerLink) {
        await this.bot.browser.utils.ghostClick(page, this.selectors.viewFooter)
    } else {
        // 如果找不到 footer，点击返回按钮
        const backButton = await page
            .waitForSelector(this.selectors.backButton, { 
                state: 'visible', 
                timeout: 2000 
            })
            .catch(() => null)
        
        if (backButton) {
            await this.bot.browser.utils.ghostClick(page, this.selectors.backButton)
        }
    }
    
    return true
}
```

### 6. 2FA TOTP 验证处理

当检测到 2FA 验证时：

```typescript
case '2FA_TOTP': {
    await this.totp2FALogin.handle(page, account.totpSecret)
    return true
}
```

**TOTP 处理逻辑：**

```typescript
async handle(page: Page, totpSecret?: string): Promise<void> {
    if (totpSecret) {
        // 自动生成 TOTP 代码
        const code = this.generateTotpCode(totpSecret)
        await this.fillCode(page, code)
        await this.bot.browser.utils.ghostClick(page, this.submitButtonSelector)
        
        // 检查是否有错误
        const errorMessage = await getErrorMessage(page)
        if (errorMessage) {
            throw new Error(`TOTP failed: ${errorMessage}`)
        }
    } else {
        // 手动输入（最多 5 次尝试）
        for (let attempt = 1; attempt <= this.maxManualAttempts; attempt++) {
            const code = await promptInput({
                question: `Enter the 6-digit TOTP code: `,
                timeoutSeconds: 60,
                validate: code => /^\d{6}$/.test(code)
            })
            
            await this.fillCode(page, code)
            await this.bot.browser.utils.ghostClick(page, this.submitButtonSelector)
            
            const errorMessage = await getErrorMessage(page)
            if (!errorMessage) {
                return // 成功
            }
        }
    }
}
```

### 7. 禁用 FIDO/Passkey

TS 项目通过拦截网络请求来禁用 FIDO（指纹/Face ID）：

```typescript
async disableFido(page: Page) {
    await page.route('**/GetCredentialType.srf*', route => {
        const request = route.request()
        const postData = request.postData()
        const body = postData ? JSON.parse(postData) : {}
        
        // 强制设置为不支持 FIDO
        body.isFidoSupported = false
        
        route.continue({
            postData: JSON.stringify(body),
            headers: {
                ...request.headers(),
                'Content-Type': 'application/json'
            }
        })
    })
}
```

这样可以避免 Microsoft 强制使用 Passkey 登录。

### 8. 错误处理和重试机制

```typescript
case 'ERROR_ALERT': {
    const alertEl = page.locator(this.selectors.errorAlert)
    const errorMsg = await alertEl.innerText().catch(() => 'Unknown Error')
    throw new Error(`Microsoft login error: ${errorMsg}`)
}

case 'ACCOUNT_LOCKED': {
    throw new Error('This account has been locked!')
}

case 'CHROMEWEBDATA_ERROR': {
    // 尝试恢复
    await page.goto(this.bot.config.baseURL, {
        waitUntil: 'domcontentloaded',
        timeout: 10000
    })
    return true
}
```

### 9. 防卡死机制

```typescript
// 如果在同一状态停留 4 次循环，刷新页面
if (state === previousState && state !== 'LOGGED_IN') {
    sameStateCount++
    if (sameStateCount >= 4) {
        await page.reload({ waitUntil: 'domcontentloaded' })
        sameStateCount = 0
        previousState = 'UNKNOWN'
        continue
    }
}
```

## 关键技术要点总结

### 1. 状态机 vs 线性流程

**Python 脚本可能的问题：**

```python
# 线性流程（容易失败）
输入邮箱 → 输入密码 → 期望登录成功
```

**TS 项目的方案：**

```typescript
// 循环检测状态，动态响应
while (未登录 && 未超时) {
    当前状态 = 检测页面状态()
    
    switch (当前状态) {
        case 'GET_A_CODE': 尝试绕过()
        case 'OTP_CODE_ENTRY': 点击返回()
        case '2FA_TOTP': 处理2FA()
        case 'ERROR_ALERT': 抛出错误()
        // ...
    }
}
```

### 2. 多重后备方案

对于每个可能的拒绝页面，TS 项目都有多个后备方案：

```typescript
// 方案 1: 点击 "Other ways to sign in"
// 方案 2: 点击 footer 链接
// 方案 3: 点击返回按钮
// 方案 4: 刷新页面重试
```

### 3. 并行检测 + 优先级排序

不是顺序检测每个元素，而是：

1. **并行检测**所有可能的状态选择器
2. 按**优先级**返回最重要的状态
3. 避免误判（例如：ERROR_ALERT 在某些页面会误触发）

### 4. 关键选择器

```typescript
// 绕过验证码页面
otherWaysToSignIn: '[data-testid="viewFooter"] span[role="button"]'
viewFooter: '[data-testid="viewFooter"] >> [role="button"]'
backButton: '#back-button'

// 检测 2FA
totpInput: 'input[name="otc"]'
totpInputOld: 'form[name="OneTimeCodeViewForm"]'

// 检测 OTP 验证码
otpCodeEntry: '[data-testid="codeEntry"]'
otpInput: 'div[data-testid="codeEntry"]'

// 检测错误
errorAlert: 'div[role="alert"]'
accountLocked: '#serviceAbuseLandingTitle'

// 检测密码选项
passwordIcon: '[data-testid="tile"]:has(svg path[d*="M11.78 10.22a.75.75"])'

// 检测邮件验证码选项
emailIcon: '[data-testid="tile"]:has(svg path[d*="M5.25 4h13.5a3.25"])'
```

### 5. 网络请求拦截

```typescript
// 禁用 FIDO/Passkey
await page.route('**/GetCredentialType.srf*', route => {
    body.isFidoSupported = false
    route.continue({ postData: JSON.stringify(body) })
})
```

这可以防止 Microsoft 强制使用生物识别登录。

## Python 脚本改进建议

### 1. 实现状态机

```python
class LoginState(Enum):
    EMAIL_INPUT = "email_input"
    PASSWORD_INPUT = "password_input"
    GET_A_CODE = "get_a_code"
    OTP_CODE_ENTRY = "otp_code_entry"
    TOTP_2FA = "2fa_totp"
    ERROR_ALERT = "error_alert"
    LOGGED_IN = "logged_in"
    UNKNOWN = "unknown"

def detect_current_state(page) -> LoginState:
    """并行检测所有可能的状态"""
    # 检查 URL
    if "rewards.bing.com" in page.url:
        return LoginState.LOGGED_IN
    
    # 并行检测选择器
    checks = {
        LoginState.PASSWORD_INPUT: 'input[type="password"]',
        LoginState.EMAIL_INPUT: 'input[type="email"]',
        LoginState.TOTP_2FA: 'input[name="otc"]',
        LoginState.OTP_CODE_ENTRY: '[data-testid="codeEntry"]',
        LoginState.ERROR_ALERT: 'div[role="alert"]',
    }
    
    for state, selector in checks.items():
        if page.query_selector(selector):
            return state
    
    # 检测 "Get a code" 页面
    if page.query_selector('[data-testid="identityBanner"]'):
        return LoginState.GET_A_CODE
    
    return LoginState.UNKNOWN

def login(page, account):
    max_iterations = 25
    iteration = 0
    previous_state = LoginState.UNKNOWN
    same_state_count = 0
    
    while iteration < max_iterations:
        iteration += 1
        state = detect_current_state(page)
        
        # 防卡死
        if state == previous_state and state != LoginState.LOGGED_IN:
            same_state_count += 1
            if same_state_count >= 4:
                page.reload()
                same_state_count = 0
                previous_state = LoginState.UNKNOWN
                continue
        else:
            same_state_count = 0
        
        if state == LoginState.LOGGED_IN:
            break
        
        # 处理状态
        handle_state(state, page, account)
        previous_state = state
        time.sleep(1)
```

### 2. 处理 "Get a Code" 拒绝页面

```python
def handle_get_a_code(page):
    """尝试绕过验证码页面"""
    # 方法 1: 点击 "Other ways to sign in"
    other_ways = page.query_selector('[data-testid="viewFooter"] span[role="button"]')
    if other_ways:
        other_ways.click()
        return
    
    # 方法 2: 点击 footer 链接
    footer = page.query_selector('[data-testid="viewFooter"] >> [role="button"]')
    if footer:
        footer.click()
        return
    
    # 方法 3: 点击返回按钮
    back_btn = page.query_selector('#back-button')
    if back_btn:
        back_btn.click()
        return
```

### 3. 处理 OTP 验证码页面

```python
def handle_otp_code_entry(page):
    """尝试返回密码登录"""
    # 尝试点击 "Use your password"
    footer = page.query_selector('[data-testid="viewFooter"] >> [role="button"]')
    if footer:
        footer.click()
        return
    
    # 如果找不到，点击返回
    back_btn = page.query_selector('#back-button')
    if back_btn:
        back_btn.click()
```

### 4. 禁用 FIDO

```python
def disable_fido(page):
    """拦截网络请求，禁用 FIDO"""
    def handle_route(route):
        if "GetCredentialType.srf" in route.request.url:
            post_data = route.request.post_data
            if post_data:
                body = json.loads(post_data)
                body['isFidoSupported'] = False
                route.continue_(post_data=json.dumps(body))
            else:
                route.continue_()
        else:
            route.continue_()
    
    page.route("**/GetCredentialType.srf*", handle_route)
```

### 5. 处理 2FA

```python
def handle_2fa_totp(page, totp_secret):
    """处理 TOTP 2FA"""
    if totp_secret:
        # 自动生成代码
        import pyotp
        totp = pyotp.TOTP(totp_secret)
        code = totp.now()
        
        # 填入代码
        totp_input = page.query_selector('input[name="otc"]')
        if totp_input:
            totp_input.fill(code)
            page.query_selector('button[type="submit"]').click()
    else:
        # 手动输入
        code = input("Enter 6-digit TOTP code: ")
        totp_input = page.query_selector('input[name="otc"]')
        if totp_input:
            totp_input.fill(code)
            page.query_selector('button[type="submit"]').click()
```

## 核心差异对比

| 特性 | Python 脚本（可能） | TS 项目 |
|------|-------------------|---------|
| 登录流程 | 线性流程 | 状态机循环 |
| 状态检测 | 顺序检测 | 并行检测 + 优先级 |
| 拒绝处理 | 可能缺失 | 多重后备方案 |
| 防卡死 | 可能缺失 | 同状态 4 次刷新 |
| FIDO 处理 | 可能缺失 | 网络拦截禁用 |
| 2FA 处理 | 可能简单 | 自动 + 手动 + 重试 |
| 错误恢复 | 可能直接失败 | 多层次恢复机制 |

## 最关键的改进点

1. **不要假设登录流程是线性的**
   - Microsoft 会随机要求不同的验证方式
   - 必须用状态机动态响应

2. **必须处理 "Get a Code" 页面**
   - 这是你遇到的核心问题
   - 需要点击 "Other ways to sign in" 或返回按钮

3. **禁用 FIDO/Passkey**
   - 通过网络拦截设置 `isFidoSupported = false`
   - 避免被强制使用生物识别

4. **实现防卡死机制**
   - 检测是否卡在同一状态
   - 超过阈值后刷新页面重试

5. **并行检测状态**
   - 不要顺序检测，会浪费时间
   - 使用 `Promise.all()` 或 Python 的 `asyncio.gather()`

## 调试建议

1. **记录每次状态转换**

   ```python
   logger.info(f"State transition: {previous_state} → {current_state}")
   ```

2. **截图保存失败页面**

   ```python
   if state == LoginState.ERROR_ALERT:
       page.screenshot(path=f"error_{timestamp}.png")
   ```

3. **记录页面 URL 和 HTML**

   ```python
   logger.debug(f"Current URL: {page.url}")
   logger.debug(f"Page title: {page.title()}")
   ```

4. **测试每个状态处理器**
   - 单独测试 `handle_get_a_code()`
   - 单独测试 `handle_otp_code_entry()`
   - 确保每个都能正确处理

## 总结

TS 项目的成功关键在于：

1. **状态机驱动** - 不假设流程，动态响应
2. **多重后备** - 每个拒绝页面都有 3+ 种绕过方法
3. **并行检测** - 快速准确判断当前状态
4. **防卡死** - 自动检测并恢复
5. **禁用 FIDO** - 避免被强制使用 Passkey

你的 Python 脚本需要实现类似的状态机逻辑，特别是处理 "Get a Code" 和 "OTP Code Entry" 这两个拒绝页面。
