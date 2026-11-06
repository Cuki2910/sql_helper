import Cocoa
import WebKit

// Offline shell: loads the bundled index.html from disk. No network access is configured anywhere.
final class AppDelegate: NSObject, NSApplicationDelegate, WKScriptMessageHandler, WKUIDelegate, WKNavigationDelegate {
    var window: NSWindow!
    var web: WKWebView!

    func applicationDidFinishLaunching(_ n: Notification) {
        let conf = WKWebViewConfiguration()
        conf.userContentController.add(self, name: "save")
        conf.websiteDataStore = WKWebsiteDataStore.default()  // persistent IndexedDB
        web = WKWebView(frame: .zero, configuration: conf)
        web.uiDelegate = self; web.navigationDelegate = self
        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 1180, height: 820),
                          styleMask: [.titled, .closable, .miniaturizable, .resizable], backing: .buffered, defer: false)
        window.title = "SQL Reference Finder (offline)"
        window.contentView = web
        window.center(); window.makeKeyAndOrderFront(nil)
        let site = Bundle.main.resourceURL!.appendingPathComponent("site")
        web.loadFileURL(site.appendingPathComponent("index.html"), allowingReadAccessTo: site)
        buildMenu()
        NSApp.activate(ignoringOtherApps: true)
    }
    // debug: SQLFINDER_SNAPSHOT=/path.png [SQLFINDER_QUERY="text"] renders the page to a PNG and exits
    func webView(_ w: WKWebView, didFinish n: WKNavigation!) {
        guard let out = ProcessInfo.processInfo.environment["SQLFINDER_SNAPSHOT"] else { return }
        let q = (ProcessInfo.processInfo.environment["SQLFINDER_QUERY"] ?? "").replacingOccurrences(of: "\\", with: "\\\\").replacingOccurrences(of: "\"", with: "\\\"").replacingOccurrences(of: "\n", with: "\\n")
        let js = "document.querySelector('#q').value=\"\(q)\"; document.querySelector('#go').click(); document.querySelector('#results').children.length"
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            w.evaluateJavaScript(js) { r, e in
                print("js:", r ?? "nil", e?.localizedDescription ?? "")
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) {
                    w.takeSnapshot(with: nil) { img, _ in
                        if let img = img, let t = img.tiffRepresentation, let b = NSBitmapImageRep(data: t), let png = b.representation(using: .png, properties: [:]) { try? png.write(to: URL(fileURLWithPath: out)) }
                        NSApp.terminate(nil)
                    }
                }
            }
        }
    }
    func applicationShouldTerminateAfterLastWindowClosed(_ a: NSApplication) -> Bool { true }

    func buildMenu() {
        let main = NSMenu(); let appItem = NSMenuItem(); main.addItem(appItem)
        let m = NSMenu(); m.addItem(withTitle: "Quit", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q"); appItem.submenu = m
        let editItem = NSMenuItem(); main.addItem(editItem)
        let e = NSMenu(title: "Edit")
        e.addItem(withTitle: "Undo", action: Selector(("undo:")), keyEquivalent: "z")
        e.addItem(withTitle: "Cut", action: #selector(NSText.cut(_:)), keyEquivalent: "x")
        e.addItem(withTitle: "Copy", action: #selector(NSText.copy(_:)), keyEquivalent: "c")
        e.addItem(withTitle: "Paste", action: #selector(NSText.paste(_:)), keyEquivalent: "v")
        e.addItem(withTitle: "Select All", action: #selector(NSText.selectAll(_:)), keyEquivalent: "a")
        editItem.submenu = e
        NSApp.mainMenu = main
    }

    // JS -> native save panel (blob downloads are unreliable in WKWebView)
    func userContentController(_ c: WKUserContentController, didReceive msg: WKScriptMessage) {
        guard let d = msg.body as? [String: String], let name = d["name"], let text = d["text"] else { return }
        let p = NSSavePanel(); p.nameFieldStringValue = name
        p.beginSheetModal(for: window) { r in
            if r == .OK, let url = p.url { try? text.write(to: url, atomically: true, encoding: .utf8) }
        }
    }
    // <input type=file> support
    func webView(_ w: WKWebView, runOpenPanelWith p: WKOpenPanelParameters, initiatedByFrame f: WKFrameInfo, completionHandler ch: @escaping ([URL]?) -> Void) {
        let o = NSOpenPanel(); o.allowsMultipleSelection = p.allowsMultipleSelection
        o.beginSheetModal(for: window) { r in ch(r == .OK ? o.urls : nil) }
    }
    func webView(_ w: WKWebView, runJavaScriptConfirmPanelWithMessage m: String, initiatedByFrame f: WKFrameInfo, completionHandler ch: @escaping (Bool) -> Void) {
        let a = NSAlert(); a.messageText = m; a.addButton(withTitle: "OK"); a.addButton(withTitle: "Cancel")
        ch(a.runModal() == .alertFirstButtonReturn)
    }
    func webView(_ w: WKWebView, runJavaScriptAlertPanelWithMessage m: String, initiatedByFrame f: WKFrameInfo, completionHandler ch: @escaping () -> Void) {
        let a = NSAlert(); a.messageText = m; a.runModal(); ch()
    }
    // refuse any navigation away from the bundled files
    func webView(_ w: WKWebView, decidePolicyFor a: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        decisionHandler(a.request.url?.isFileURL == true || a.request.url?.scheme == "about" ? .allow : .cancel)
    }
}
let app = NSApplication.shared
let del = AppDelegate()
app.delegate = del
app.setActivationPolicy(.regular)
app.run()
