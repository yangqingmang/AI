# AutoJS 脚本逆向与 Hook 实战指南

本文档详细介绍了如何通过 Frida 对 AutoJS 打包的 Android 应用进行 Hook（钩子）操作，以分析其运行逻辑（如网络请求、UI 操作、文件读写等），从而在无法获取源码的情况下理解脚本行为。

## 1. 环境准备

在开始之前，请确保你拥有以下环境：

### 1.1 硬件/模拟器
*   **Android 设备**：真实的 Root 手机，或 Android 模拟器（推荐 **夜神模拟器** 或 **雷电模拟器**）。
*   **Root 权限**：确保设备/模拟器已开启 Root 权限。

### 1.2 电脑端软件
*   **Python**：用于安装 Frida 客户端工具。
*   **ADB (Android Debug Bridge)**：用于连接安卓设备（模拟器安装目录下通常自带 `adb.exe`）。
*   **文本编辑器**：如 VS Code，用于编写 Hook 脚本。

### 1.3 安装 Frida 客户端
在电脑终端（CMD/PowerShell）执行：
```powershell
pip install frida-tools
```

---

## 2. 安装 Frida 服务端 (Server)

需要在安卓设备上运行 Frida 服务端才能进行通信。

### 2.1 确定设备架构
连接设备，在电脑终端运行：
```powershell
関連記事：adb shell getprop ro.product.cpu.abi
```
*   **x86** 或 **x86_64**：常见于模拟器。
*   **arm64-v8a**：常见于真机。

### 2.2 下载并推送 Server
1.  访问 [Frida GitHub Releases](https://github.com/frida/frida/releases)。
2.  下载对应架构的 Server 文件，例如：`frida-server-16.x.x-android-x86.xz`。
3.  解压文件，并将解压后的文件重命名为 `frida-server`。
4.  推送到设备：
    ```powershell
    adb push frida-server /data/local/tmp/
    ```

### 2.3 启动 Server
在电脑终端运行：
```powershell
関連記事：adb shell
su                     # 获取 Root 权限（模拟器可能需要点确认）
cd /data/local/tmp
chmod 777 frida-server # 赋予执行权限
./frida-server &       # 后台启动
```
*如果不报错且光标换行，说明启动成功。*

---

## 3. 编写 Hook 脚本 (`hook_autojs.js`)

将以下代码保存为 `hook_autojs.js`。此脚本专门针对 AutoJS 的常用 API 编写。

```javascript
Java.perform(function () {
    console.log("========================================");
    console.log("[*] Frida Hook 脚本已注入");
    console.log("[*] 正在监控 AutoJS 关键行为...");
    console.log("========================================");

    // ============================================================
    // 1. 监控 HTTP 网络请求 (基于 OkHttp3)
    // AutoJS http 模块底层通常依赖 OkHttp3
    // ============================================================
    try {
        var OkHttpClient = Java.use("okhttp3.OkHttpClient");
        
        // Hook newCall 方法，拦截请求对象
        OkHttpClient.newCall.overload('okhttp3.Request').implementation = function (request) {
            var url = request.url().toString();
            var method = request.method();
            
            console.log("\n[HTTP] " + method + " 请求: " + url);
            
            // 可选：打印 Header
            // var headers = request.headers().toString();
            // console.log("   Headers: " + headers);

            return this.newCall(request);
        };
    } catch (e) {
        console.log("[!] Hook HTTP 失败 (可能被混淆或未使用 OkHttp): " + e);
    }

    // ============================================================
    // 2. 监控 UI 点击操作 (Accessibility)
    // 监控 id("xyz").click() 或 click(x, y) 等行为
    // ============================================================
    try {
        var AccessibilityNodeInfo = Java.use("android.view.accessibility.AccessibilityNodeInfo");
        
        // 16 代表 ACTION_CLICK
        AccessibilityNodeInfo.performAction.overload('int').implementation = function (action) {
            if (action === 16) {
                var viewId = this.getViewIdResourceName();
                var text = this.getText();
                var cls = this.getClassName();

                console.log("\n[UI] 正在点击控件 >>>");
                console.log("     ID  : " + (viewId ? viewId : "无"));
                console.log("     文本: " + (text ? text : "无"));
                console.log("     类型: " + cls);
            }
            return this.performAction(action);
        };
    } catch (e) {
        console.log("[!] Hook UI 操作失败: " + e);
    }

    // ============================================================
    // 3. 监控日志输出 (Logcat)
    // 对应脚本中的 log(), console.log(), print()
    // ============================================================
    try {
        var Log = Java.use("android.util.Log");

        // 拦截 Log.d (Debug) 和 Log.v (Verbose)
        // 通常 AutoJS 的 console.log 会调用其中之一
        var logOverlay = function (tag, msg) {
            // 过滤掉系统杂音，只看 AutoJS 相关
            if (tag && (tag.indexOf("AutoJs") !== -1 || tag.indexOf("Script") !== -1)) {
                console.log("[Log] [" + tag + "] " + msg);
            }
            // 继续执行原生逻辑，不影响 APP 运行
            return this.d(tag, msg);
        };

        Log.d.overload('java.lang.String', 'java.lang.String').implementation = logOverlay;
        Log.v.overload('java.lang.String', 'java.lang.String').implementation = logOverlay;

    } catch (e) {
         // console.log("[!] Hook Log 失败: " + e);
    }

    // ============================================================
    // 4. 监控 Toast 弹窗
    // 对应脚本中的 toast("Hello")
    // ============================================================
    try {
        var Toast = Java.use("android.widget.Toast");
        Toast.show.implementation = function () {
            console.log("\n[Toast] 脚本弹出了提示气泡 (Toast)");
            // 尝试获取 Toast 内容在不同安卓版本较复杂，此处仅提示动作
            return this.show();
        };
    } catch (e) {
        console.log("[!] Hook Toast 失败");
    }

    // ============================================================
    // 5. 监控文件读取
    // 对应 files.read(), open()
    // ============================================================
    try {
        var FileInputStream = Java.use("java.io.FileInputStream");
        FileInputStream.$init.overload('java.lang.String').implementation = function(path) {
            // 过滤掉系统底层文件，只看可能是脚本配置的文件
            if (path.indexOf(".js") !== -1 || path.indexOf(".json") !== -1 || path.indexOf(".txt") !== -1) {
                console.log("[File] 读取文件: " + path);
            }
            return this.$init(path);
        }
    } catch(e) {}
    
    // ============================================================
    // 6. 监控 SharedPreferences (本地存储)
    // 对应 storages.create()
    // ============================================================
    try {
         var Activity = Java.use("android.app.Activity");
         Activity.getSharedPreferences.overload('java.lang.String', 'int').implementation = function(name, mode) {
             console.log("[Storage] 访问本地存储库: " + name);
             return this.getSharedPreferences(name, mode);
         }
    } catch(e) {}

});
```

---

## 4. 执行 Hook

1.  **确定包名**：确保你知道目标 APK 的包名（例如 `org.ldffd.myld`）。如果不确定，可以在模拟器打开 APP，然后在电脑运行 `adb shell dumpsys window | findstr mCurrentFocus` 查看。

2.  **运行命令**：
    在 `hook_autojs.js` 所在目录打开终端，运行：

    ```powershell
    # -U 连接 USB/模拟器
    # -f 强制启动 APP (如果 APP 已经运行会自动重启)
    # -l 加载脚本
    # --no-pause 启动后不暂停
    frida -U -f org.ldffd.myld -l hook_autojs.js
    ```

## 5. 分析结果

运行成功后，终端会实时输出 APP 的行为日志。你可以根据这些日志重构脚本逻辑。

**示例输出及分析：**

```text
[HTTP] POST 请求: http://api.target.com/api/v1/login
   -> 分析：脚本正在进行登录，目标是这个 URL。

[Storage] 访问本地存储库: user_config
   -> 分析：脚本使用了一个名为 "user_config" 的本地存储。

[File] 读取文件: /sdcard/脚本/配置.txt
   -> 分析：脚本依赖这个配置文件，去看看里面写了什么。

[UI] 正在点击控件 >>>
     ID  : com.example:id/btn_start
     文本: 开始运行
     类型: android.widget.Button
   -> 分析：脚本点击了“开始运行”按钮，我可以写代码 id("btn_start").click() 来模仿。
```

